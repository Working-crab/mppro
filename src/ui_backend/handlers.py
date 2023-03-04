
import re
from ui_backend.app import bot
from ui_backend.common import universal_reply_markup, paginate_buttons, city_reply_markup, escape_telegram_specials, logs_types_reply_markup, universal_reply_markup_additionally, advert_info_message_maker
from telebot import types
from db.queries import db_queries
from wb_common.wb_queries import wb_queries
from datetime import datetime, timedelta
from cache_worker.cache_worker import cache_worker
from ui_backend.message_queue import queue_message_async
import copy

import traceback
from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)

#Пример для создания истории действий
#db_queries.add_action_history(user_id=message.chat.id, action=f"Какое-то событие")

# all messages handler
@bot.message_handler(func=lambda m: True)
async def message_handler(message):

  try:
    logger.info('message from')
    logger.info(message.chat.id)
    logger.info('message text')
    logger.info(message.text)

    telegram_user_id = message.from_user.id

    user_session = cache_worker.get_user_session(telegram_user_id)
    message.user_session = user_session
    message.user_session_old = copy.deepcopy(user_session)
    message.user_session_step_set = False

    user_step = user_session.get('step')
    if not user_step:
      user_step = 'База'

    possible_actions = step_map.get(user_step, {})

    user_action = None
    for key in possible_actions:
      if re.search(key, message.text):
        user_action = possible_actions[key]
        break

    logger.info('user_action')
    logger.info(user_action)

    user_action_default = possible_actions.get('default')
    if user_action:
      await user_action(message)
    elif user_action_default:
      await user_action_default(message)

    if not message.user_session_step_set:
      set_user_session_step(message, 'База')
    else:
      update_user_session(message)


  except Exception as e:
    logger.error(e)
    traceback.print_exc()
    await queue_message_async(
      destination_id = message.chat.id,
      message = 'На стороне сервера произошла ошибка, обратитесь к разработчику или попробуйте позже'
    )



# Ветка "Поиск" --------------------------------------------------------------------------------------------------------

async def search_adverts(message):
  await bot.send_message(message.chat.id, 'Введите ключевое слово', reply_markup=types.ReplyKeyboardRemove())
  set_user_session_step(message, 'Search_adverts')
        
async def search_next_step_handler(message, after_choose=False):
  user_id = message.from_user.id
  keyword = None

  if after_choose:
    keyword = message.user_session.get('search_last')
  else:
    keyword = message.text
    
  db_queries.add_action_history(user_id=message.chat.id, action=f"Поиск по запросу: '{keyword}'")
  
  city = message.user_session.get('search_city')
  if city == None:
    city = "Москва"
  
  
  proccesing = await bot.send_message(message.chat.id, 'Обработка запроса...')
  item_dicts = wb_queries.search_adverts_by_keyword(keyword, user_id)
  result_message = ''
  position_ids = []
  
  chat_id_proccessing = proccesing.chat.id
  message_id_proccessing = proccesing.message_id
  
  if len(item_dicts) == 0:
    await bot.delete_message(chat_id_proccessing, message_id_proccessing)
    await bot.send_message(message.chat.id, 'Такой товар не найден', reply_markup=universal_reply_markup())
    return

  for item_idex in range(len(item_dicts)):
    position_ids.append(str(item_dicts[item_idex]['p_id']))

    price = item_dicts[item_idex]['price']
    p_id = item_dicts[item_idex]['p_id']
    result_message += f'\\[{item_idex + 1}\\]   *{price}₽*,  [{p_id}](https://www.wildberries.ru/catalog/{p_id}/detail.aspx) 🔄 \n'
  
  await bot.delete_message(chat_id_proccessing, message_id_proccessing)
  message_to_update = await bot.send_message(message.chat.id, result_message, reply_markup=universal_reply_markup(), parse_mode='MarkdownV2')


  result_message = f'Текущие рекламные ставки по запросу: *{keyword}*\nГород доставки: *{city}*\n\n'
  adverts_info = wb_queries.get_products_info_by_wb_ids(position_ids, city, user_id)

  logger.info('adverts_info')
  logger.info(adverts_info)

  logger.info('range(len(item_dicts))')
  logger.info(range(len(item_dicts)))
  for item_idex in range(len(item_dicts)):

    product_id = item_dicts[item_idex]['p_id']
    price = item_dicts[item_idex]['price']
    message_string = f'\\[{item_idex + 1}\\]   *{price}₽*,  [{product_id}](https://www.wildberries.ru/catalog/{product_id}/detail.aspx)'
    advert_info = adverts_info.get(product_id)

    if advert_info:
      product_name = escape_telegram_specials(advert_info.get('name')[:30]) if advert_info.get('name')[:30] else product_id
      product_time = f'{advert_info.get("time2")}ч' if advert_info.get('time2') else ''
      product_category_name = advert_info.get('category_name') if advert_info.get('category_name') else ''
      message_string = f'\\[{item_idex + 1}\\] \t *{price}₽*, \t {product_category_name} \t {product_time} \t [{product_name}](https://www.wildberries.ru/catalog/{product_id}/detail.aspx)'
    else:
      message_string += ' возможно нет в наличии'

    result_message += f'{message_string}\n'

  if result_message:
    await bot.delete_message(message_to_update.chat.id, message_to_update.message_id)
    await bot.send_message(message.chat.id, result_message, reply_markup=universal_reply_markup(search=True), parse_mode='MarkdownV2')
    message.user_session['search_last'] = keyword



async def choose_city(message):
  city = message.user_session.get('search_city')
  if city == None:
    city = "Москва"
  
  await bot.send_message(message.chat.id, f'Выберите город из предоставленных на панели\nУ вас стоит: *{city}*', reply_markup=city_reply_markup(), parse_mode='MarkdownV2')
        
        
async def choose_city_handler(message):
  city = message.text.split()[1]
  message.user_session['search_city'] = city
  await search_next_step_handler(message, after_choose=True)

# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Помощь" ---------------------------------------------------------------------------------------------------------------------------------

async def help(message):
  await queue_message_async(
    destination_id = message.chat.id,
    message = 'По вопросам работы бота обращайтесь: \n (https://t.me/tNeymik) \n (https://t.me/plazmenni_rezak)'
  )
  pass
# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Установить токен" -----------------------------------------------------------------------------------------------------------------------

async def set_token_cmp(message):
  await bot.send_message(message.chat.id, 'Введите токен', reply_markup=types.ReplyKeyboardRemove())
  set_user_session_step(message, 'Set_token_cmp')

async def set_token_cmp_handler(message):
    try:
        clear_token = message.text.replace('/set_token_cmp ', '').strip()
        db_queries.set_user_wb_cmp_token(telegram_user_id=message.from_user.id, wb_cmp_token=clear_token)
        user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
        wb_queries.reset_base_tokens(user)

        await bot.send_message(message.chat.id, 'Ваш токен установлен\!', reply_markup=universal_reply_markup(), parse_mode='MarkdownV2')
        db_queries.add_action_history(user_id=message.chat.id, action=f"Был установлен токен: '{clear_token}'")

    except Exception as e:

        # TODO check Exception for "Неверный токен!" Exception
        await bot.send_message(message.chat.id, e, reply_markup=universal_reply_markup())
        db_queries.add_action_history(user_id=message.chat.id, action=f"Произошла ошибка при установке токена")
        logger.error(e)
# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Список рекламных компаний" --------------------------------------------------------------------------------------------------------------
async def list_adverts(message):
  await list_adverts_handler(message)

async def list_adverts_handler(message):
  """Функия которая формирует и отправляет рекламные компании пользователя"""

  user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
  user_wb_tokens = wb_queries.get_base_tokens(user)
  req_params = wb_queries.get_base_request_params(user_wb_tokens)
  
  page_number = 1
  user_atrevds_data = wb_queries.get_user_atrevds(req_params, page_number)

  result_msg = advert_info_message_maker(user_atrevds_data['adverts'], page_number=page_number)

  page_size = 6
  total_count_adverts = user_atrevds_data['total_count']
  action = "page"
  inline_keyboard = paginate_buttons(action, page_number, total_count_adverts, page_size, message.from_user.id)

  await bot.send_message(message.chat.id, result_msg, reply_markup=inline_keyboard, parse_mode='MarkdownV2')



@bot.callback_query_handler(func=lambda x: re.match('page', x.data))
async def kek(data):
    try:
      await bot.edit_message_text('Вайлдберис старается 🔄', data.message.chat.id, data.message.id, parse_mode='MarkdownV2')
      type_of_callback, page_number, user_id = data.data.split(':') # parameters = [type_of_callback, page_number, user_id]
      page_number = int(page_number)
      user = db_queries.get_user_by_telegram_user_id(user_id)
      user_wb_tokens = wb_queries.get_base_tokens(user)
      req_params = wb_queries.get_base_request_params(user_wb_tokens)
      user_atrevds_data = wb_queries.get_user_atrevds(req_params, page_number)

      
      # kek1 = get_bids_table(user_id, 3833716) TODO
      result_msg = advert_info_message_maker(user_atrevds_data['adverts'], page_number=page_number)

      total_count = user_atrevds_data['total_count']
      page_size = 6
      action = "page"
      inline_keyboard = paginate_buttons(action, page_number, total_count, page_size, user_id)

      await bot.edit_message_text(result_msg, data.message.chat.id, data.message.id, parse_mode='MarkdownV2')
      await bot.edit_message_reply_markup(data.message.chat.id, data.message.id , reply_markup=inline_keyboard)
      await bot.answer_callback_query(data.id)
    except Exception as e:
        bot.send_message(data.message.chat.id, f'{e} ,')
        traceback.print_exc()
# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Добавить рекламную компанию" ------------------------------------------------------------------------------------------------------------
@bot.message_handler(regexp='Добавить рекламную компанию')
async def cb_adverts(message):
  pass # TODO refactor
  # msg_text = 'Введите данные в формате "<campaign_id> <max_budget> <place> <status>" в следующем сообщение.'
  # sent = await bot.send_message(message.chat.id, msg_text, reply_markup=types.ReplyKeyboardRemove())
  # await bot.register_next_step_handler(sent,add_advert_handler)

async def add_advert_handler(message):
    """
    Команда для запсии в бд информацию о том, что юзер включает рекламную компанию
    TO wOrKeD:
    (индентификатор, бюджет, место которое хочет занять)
    записать это в бд
    """
    try:
        user = db_queries.get_user_by_telegram_user_id(message.from_user.id)

        #(индентификатор, бюджет, место которое хочет занять)args*
        message_args = re.sub('/add_advert ', '', message.text).split(sep=' ', maxsplit=4)
        if len(message_args) != 4:
            msg_text = 'Для использования команды используйте формат: /add_advert <campaign_id> <max_budget> <place> <status>'
            await bot.send_message(message.chat.id, msg_text, reply_markup=universal_reply_markup())
            return

        campaign_id = re.sub('/add_advert ', '', message_args[0])
        max_budget = re.sub('/add_advert ', '', message_args[1])
        place = re.sub('/add_advert ', '', message_args[2])
        status = re.sub('/add_advert ', '', message_args[3])

        add_result = db_queries.add_user_advert(user, status, campaign_id, max_budget, place)
        
        res_msg = ''
        if add_result == 'UPDATED':
            res_msg = 'Ваша рекламная компания успешно обновлена\!'
        elif add_result == 'ADDED':
            res_msg = 'Ваша рекламная компания успешно добавлена\!'

        await bot.send_message(message.chat.id, res_msg, reply_markup=universal_reply_markup(), parse_mode='MarkdownV2')
    except Exception as e:
        await bot.send_message(message.chat.id, 'Что-то пошло не так', reply_markup=universal_reply_markup())
        logger.error(e)
# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Показать логи человека" -----------------------------------------------------------------------------------------------------------------
@bot.message_handler(regexp='Показать логи человека')
async def cb_adverts(message):
  pass # TODO refactor
  # sent = await bot.send_message(message.chat.id, 'Введите id user\'а\nи через пробел дату, пример формата 2023-03-02 14:30', reply_markup=types.ReplyKeyboardRemove())
  # await bot.register_next_step_handler(sent, search_logs_next_step_handler)
        
        
async def search_logs_next_step_handler(message):
  try:
    search_logs = re.sub('/search_id ', '', message.text)
    search_user_id = search_logs.split()[0]
    timestamp = search_logs.split()[1] + " " + search_logs.split()[2]
    await bot.send_message(message.chat.id, f"user_id: {search_user_id}\ntimestamp: {timestamp}\nВыберите какой тип логов Вас интерисует", reply_markup=logs_types_reply_markup(user_id=search_user_id, timestamp=timestamp))
    
    
  except Exception as e:
    traceback.print_exc()
    await bot.send_message(message.chat.id, e, reply_markup=universal_reply_markup())

        
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Дополнительные опции ---------------------------------------------------------------------------------------------------------------------------

async def menu_additional_options(message):
    try:
        await bot.send_message(message.chat.id, "Вы перешли в раздел *Дополнительные опции*", parse_mode='MarkdownV2', reply_markup=universal_reply_markup_additionally())
    except Exception as e:
        await bot.send_message(message.chat.id, e)
        

async def menu_back(message):
    try:
        back = await bot.send_message(message.chat.id, "Добро пожаловать *Назад* 🤓", parse_mode='MarkdownV2', reply_markup=universal_reply_markup())

    except Exception as e:
        await bot.send_message(message.chat.id, e)

# ------------------------------------------------------------------------------------------------------------------------------------------------

# История действий -------------------------------------------------------------------------------------------------------------------------------

async def show_action_history(message):
  try:
    page_number = 1
    page_action = 5
    action_history = db_queries.show_action_history(message.chat.id, page_action)
    total_count_action = action_history.count()
    
    result_message = f'Список Ваших последних действий в боте, страница: {page_number}\n\n'
    i = 1
    if total_count_action == 0:
      return await bot.send_message(message.chat.id, 'Нет истории действий', reply_markup=universal_reply_markup())
    else:
      if page_number == 1:
        action_history = action_history[page_number-1:page_action]
    
    for action in action_history:
      result_message += f'[{i}]-----------------------------\nДата: {(action.date_time + timedelta(hours=3)).strftime("%m/%d/%Y, %H:%M:%S")}\n\nДействие: {action.action}\n-----------------------------\n\n'
      i+=1
      
    action = "action"
    inline_keyboard = paginate_buttons(action, page_number, total_count_action, page_action, message.from_user.id)
    await bot.send_message(message.chat.id, result_message, reply_markup=inline_keyboard)
    
    
  except Exception as e:
      await bot.send_message(message.chat.id, e)
        

@bot.callback_query_handler(func=lambda x: re.match('action', x.data))
async def action_page(data):
    try:
      await bot.edit_message_text('Информация загружается 🔄', data.message.chat.id, data.message.id)
      type_of_callback, page_number, user_id = data.data.split(':') # parameters = [type_of_callback, page_number, user_id]
      page_number = int(page_number)
      page_action = 5
      action_history = db_queries.show_action_history(data.message.chat.id, page_action)
      total_count_action = action_history.count()
      
      result_message = f'Список Ваших последних действий в боте, страница: {page_number}\n\n'
      
      if page_number != 1:
        action_history = action_history[(5*(page_number-1)):page_action*page_number]
        i = (5 * page_number)-4
      else:
        action_history = action_history[page_number-1:page_action]
        i = (5 * page_number)-4
        
      for action in action_history:
        result_message += f'[{i}]-----------------------------\nДата: {(action.date_time + timedelta(hours=3)).strftime("%m/%d/%Y, %H:%M:%S")}\n\nДействие: {action.action}\n-----------------------------\n\n'
        i+=1
      action = "action"
      inline_keyboard = paginate_buttons(action, page_number, total_count_action, page_action, user_id)      
    
      await bot.edit_message_text(result_message, data.message.chat.id, data.message.id)
      await bot.edit_message_reply_markup(data.message.chat.id, data.message.id , reply_markup=inline_keyboard)
      await bot.answer_callback_query(data.id)
    except Exception as e:
      await bot.send_message(data.message.chat.id, f'{e} ,')
      traceback.print_exc()
# ------------------------------------------------------------------------------------------------------------------------------------------------


def set_user_session_step(message, step_name):
  user_id = message.from_user.id
  message.user_session['step'] = step_name
  message.user_session_step_set = True
  message.user_session['updated_at'] = str(datetime.now())
  cache_worker.set_user_session(user_id, message.user_session)


def update_user_session(message):
  if message.user_session == message.user_session_old:
    return
  
  message.user_session['updated_at'] = str(datetime.now())
  cache_worker.set_user_session(message.from_user.id, message.user_session)


step_map = {
  'База': {
    'Помощь': help,
    'Поиск': search_adverts,
    'Список рекламных компаний': list_adverts,
    'Выбрать город': choose_city,
    'Выбор:': choose_city_handler,
    'Установить токен': set_token_cmp,
    'История действий': show_action_history,
    'Дополнительные опции': menu_additional_options,
    'Назад': menu_back,
    'default': help
  },
  'Search_adverts': {
    'default': search_next_step_handler
  },
  'Set_token_cmp': {
    'default': set_token_cmp_handler
  }
}
