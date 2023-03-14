
import re
from ui_backend.app import bot
from ui_backend.common import universal_reply_markup, paginate_buttons, city_reply_markup, escape_telegram_specials, logs_types_reply_markup, universal_reply_markup_additionally, advert_info_message_maker, reply_markup_payment, adv_settings_reply_markup, action_history_reply_markup, action_history_filter_reply_markup
from telebot import types
from db.queries import db_queries
from wb_common.wb_queries import wb_queries
from datetime import datetime, timedelta
from cache_worker.cache_worker import cache_worker
from ui_backend.message_queue import queue_message_async
import copy

import io

from ui_backend.bot import *
from yookassa import Payment

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

    logger.debug('user_session')
    logger.debug(user_session)

    message.user_session = user_session
    message.user_session_old = copy.deepcopy(user_session)
    message.user_session_step_set = False

    user_step = user_session.get('step', 'База')

    possible_actions = step_map.get(user_step, {})

    user_action = None
    for key in possible_actions:
      if re.search(key, message.text):
        user_action = possible_actions[key]
        break

    logger.debug('user_action')
    logger.debug(user_action)

    user_action_default = possible_actions.get('default')
    if user_action:
      await user_action(message)
    elif user_action_default:
      await user_action_default(message)
      

    if not message.user_session_step_set:
      set_user_session_step(message, 'База')

    update_user_session(message)


  except Exception as e:
    traceback.print_exc()
    logger.error(e)

    if str(e) == 'Неверный токен!':
      await queue_message_async(
        destination_id = message.chat.id,
        message = 'Произошла ошибка валидации токена! Возможно срок его действия истек, попробуйте перезагрузить токен!'
      )
      return


    await queue_message_async(
      destination_id = message.chat.id,
      message = 'На стороне сервера произошла ошибка, обратитесь к разработчику или попробуйте позже'
    )



# Ветка "Поиск" --------------------------------------------------------------------------------------------------------

async def search_adverts(message):
  await bot.send_message(message.chat.id, 'Введите ключевое слово', reply_markup=types.ReplyKeyboardRemove())
  set_user_session_step(message, 'Search_adverts')
        
async def search_next_step_handler(message, after_city_choose=False):
  telegram_user_id = message.from_user.id
  keyword = None

  if after_city_choose:
    keyword = message.user_session.get('search_last')
  else:
    keyword = message.text
    
  db_queries.add_action_history(telegram_user_id=telegram_user_id, action="Поиск", action_description=f"Поиск по запросу: '{keyword}'")
  
  city = message.user_session.get('search_city')
  if city == None:
    city = "Москва"
  
  
  proccesing = await bot.send_message(message.chat.id, 'Обработка запроса...')
  item_dicts = wb_queries.search_adverts_by_keyword(keyword, telegram_user_id)
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
  adverts_info = wb_queries.get_products_info_by_wb_ids(position_ids, city, telegram_user_id)

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
  await search_next_step_handler(message, after_city_choose=True)

# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Помощь" ---------------------------------------------------------------------------------------------------------------------------------

async def help(message):
  await queue_message_async(
    destination_id = message.chat.id,
    message = 'По вопросам работы бота обращайтесь: \n (https://t.me/Ropejamp) \n (https://t.me/plazmenni_rezak)'
  )

async def misSpell(message):
  await queue_message_async(
    destination_id = message.chat.id,
    message = 'Для работы с ботом используйте меню',
  )

# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Установить токен" -----------------------------------------------------------------------------------------------------------------------

async def set_token_cmp(message):
  await bot.send_message(message.chat.id, 'Введите токен', reply_markup=types.ReplyKeyboardRemove())
  set_user_session_step(message, 'Set_token_cmp')

async def set_token_cmp_handler(message):
  clear_token = message.text.replace('/set_token_cmp ', '').strip()
  user = db_queries.get_user_by_telegram_user_id(message.from_user.id)


  try:
    wb_queries.reset_base_tokens(user, token=clear_token)
  except Exception as e:
    if str(e) == 'Неверный токен!':
      await bot.send_message(message.chat.id, 'Неверный токен!', reply_markup=universal_reply_markup())
      return
    raise e


  db_queries.set_user_wb_cmp_token(telegram_user_id=message.from_user.id, wb_cmp_token=clear_token)
  await bot.send_message(message.chat.id, 'Ваш токен установлен\!', reply_markup=universal_reply_markup(), parse_mode='MarkdownV2')
  db_queries.add_action_history(user_id=user.id, action="Токен", action_description=f"Был установлен токен: '{clear_token}'")

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
  
  # user_atrevds_data = wb_queries.get_user_atrevds(req_params, page_number)
  user_atrevds_data = wb_queries.get_user_atrevds(req_params)
  
  page_size = 6
  logger.info(len(user_atrevds_data['adverts']))
  result_msg = advert_info_message_maker(user_atrevds_data['adverts'], page_number=page_number, page_size=page_size, user=user)

  total_count_adverts = user_atrevds_data['total_count']
  action = "page"
  inline_keyboard = paginate_buttons(action, page_number, total_count_adverts, page_size, message.from_user.id)

  await bot.send_message(message.chat.id, result_msg, reply_markup=inline_keyboard, parse_mode='MarkdownV2')



@bot.callback_query_handler(func=lambda x: re.match('page', x.data))
async def kek(data):
  await bot.edit_message_text('Вайлдберис старается 🔄', data.message.chat.id, data.message.id, parse_mode='MarkdownV2')
  type_of_callback, page_number, user_id = data.data.split(':') # parameters = [type_of_callback, page_number, user_id]
  page_number = int(page_number)
  user = db_queries.get_user_by_telegram_user_id(user_id)
  user_wb_tokens = wb_queries.get_base_tokens(user)
  req_params = wb_queries.get_base_request_params(user_wb_tokens)
  
  # user_atrevds_data = wb_queries.get_user_atrevds(req_params, page_number=1)
  user_atrevds_data = wb_queries.get_user_atrevds(req_params)

  page_size = 6
  result_msg = advert_info_message_maker(user_atrevds_data['adverts'], page_number=page_number, page_size=page_size, user=user)

  total_count = user_atrevds_data['total_count']
  action = "page"
  inline_keyboard = paginate_buttons(action, page_number, total_count, page_size, user_id)

  await bot.edit_message_text(result_msg, data.message.chat.id, data.message.id, parse_mode='MarkdownV2')
  await bot.edit_message_reply_markup(data.message.chat.id, data.message.id , reply_markup=inline_keyboard)
  await bot.answer_callback_query(data.id)

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

# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Показать логи человека" -----------------------------------------------------------------------------------------------------------------
@bot.message_handler(regexp='Показать логи человека')
async def cb_adverts(message):
  pass # TODO refactor
  # sent = await bot.send_message(message.chat.id, 'Введите id user\'а\nи через пробел дату, пример формата 2023-03-02 14:30', reply_markup=types.ReplyKeyboardRemove())
  # await bot.register_next_step_handler(sent, search_logs_next_step_handler)
        
        
async def search_logs_next_step_handler(message):
  search_logs = re.sub('/search_id ', '', message.text)
  search_user_id = search_logs.split()[0]
  timestamp = search_logs.split()[1] + " " + search_logs.split()[2]
  await bot.send_message(message.chat.id, f"user_id: {search_user_id}\ntimestamp: {timestamp}\nВыберите какой тип логов Вас интерисует", reply_markup=logs_types_reply_markup(user_id=search_user_id, timestamp=timestamp))

        
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Дополнительные опции ---------------------------------------------------------------------------------------------------------------------------

async def menu_additional_options(message):
  await bot.send_message(message.chat.id, "Вы перешли в раздел *Дополнительные опции*", parse_mode='MarkdownV2', reply_markup=universal_reply_markup_additionally())
        

async def menu_back(message):
  await bot.send_message(message.chat.id, "Добро пожаловать *Назад* 🤓", parse_mode='MarkdownV2', reply_markup=universal_reply_markup())


# ------------------------------------------------------------------------------------------------------------------------------------------------

# История действий -------------------------------------------------------------------------------------------------------------------------------
async def show_action_history(message):
  page_number = 1
  page_action = 5
  action_history = db_queries.show_action_history(message.chat.id)
  total_count_action = action_history.count()
  
  action = "Нет"
  result_message = f'Список Ваших последних действий в боте\nФильтр: {action}\nCтраница: {page_number}\n\n'
  i = 1
  if total_count_action == 0:
    return await bot.send_message(message.chat.id, 'Нет истории действий', reply_markup=universal_reply_markup())
  else:
    if page_number == 1:
      action_history = action_history[page_number-1:page_action]
  
  for action in action_history:
    result_message += f'[{i}]-----------------------------\nДата: {(action.date_time + timedelta(hours=3)).strftime("%m/%d/%Y, %H:%M:%S")}\n\nДействие: {action.description}\n-----------------------------\n\n'
    i+=1

  action = "action"
  inline_keyboard = paginate_buttons(action, page_number, total_count_action, page_action, message.from_user.id)
  await bot.send_message(message.chat.id, result_message, reply_markup=inline_keyboard)
  await bot.send_message(message.chat.id, 'На панеле снизу Вы можете выбрать фильтрацию для истории действий или загрузить свою историю', reply_markup=action_history_reply_markup())


@bot.callback_query_handler(func=lambda x: re.match('action', x.data))
async def action_page(data):
  await bot.edit_message_text('Информация загружается 🔄', data.message.chat.id, data.message.id)
  type_of_callback, page_number, user_id = data.data.split(':') # parameters = [type_of_callback, page_number, user_id]
    
  page_number = int(page_number)
  page_action = 5
  action = "Нет"
  if type_of_callback == "action_filter":
    action = cache_worker.get_action_history_filter(data.message.chat.id)
    action_history = db_queries.show_action_history(data.message.chat.id, action=action)
  else:
    action_history = db_queries.show_action_history(data.message.chat.id)
  result_message = f'Список Ваших последних действий в боте\nФильтр: {action}\nCтраница: {page_number}\n\n'
  total_count_action = action_history.count()
  
  if page_number != 1:
    action_history = action_history[(page_action*(page_number-1)):page_action*page_number]
    i = (5 * page_number)-4
  else:
    action_history = action_history[page_number-1:page_action]
    i = (5 * page_number)-4
    
  for action in action_history:
    result_message += f'[{i}]-----------------------------\nДата: {(action.date_time + timedelta(hours=3)).strftime("%m/%d/%Y, %H:%M:%S")}\n\nДействие: {action.description}\n-----------------------------\n\n'
    i+=1
  
  if type_of_callback == "action_filter":
    action = "action_filter"
  else:
    action = "action"
  inline_keyboard = paginate_buttons(action, page_number, total_count_action, page_action, user_id)      

  await bot.answer_callback_query(data.id)
  await bot.edit_message_text(result_message, data.message.chat.id, data.message.id)
  await bot.edit_message_reply_markup(data.message.chat.id, data.message.id , reply_markup=inline_keyboard)
  
# ------------------------------------------------------------------------------------------------------------------------------------------------

# ---- История действий // КНОПКИ -------------------------------------------------------------------------------------------------------------------

async def action_history_filter(message):
  await bot.send_message(message.chat.id, 'Выберите фильтрацию', reply_markup=action_history_filter_reply_markup(action="filter:action"))
  
  
@bot.callback_query_handler(func=lambda x: re.match('filter:action:', x.data))
async def action_page(data):
  action = data.data.split(':')[2] # parameters = [type_of_callback, page_number, user_id]
  # await bot.edit_message_text(action, data.message.chat.id, data.message.id)
  
  cache_worker.set_action_history_filter(user_id=data.message.chat.id, filter=action)
  
  page_number = 1
  page_action = 5
  action_history = db_queries.show_action_history(data.message.chat.id, action=action)
  total_count_action = action_history.count()
  
  
  result_message = f'Список Ваших последних действий в боте\nФильтр: {action}\nCтраница: {page_number}\n\n'
  i = 1
  if total_count_action == 0:
    return await bot.send_message(data.message.chat.id, 'Нет истории действий', reply_markup=universal_reply_markup())
  else:
    if page_number == 1:
      action_history = action_history[page_number-1:page_action]
  
  for action in action_history:
    result_message += f'[{i}]-----------------------------\nДата: {(action.date_time + timedelta(hours=3)).strftime("%m/%d/%Y, %H:%M:%S")}\n\nДействие: {action.description}\n-----------------------------\n\n'
    i+=1

  action = "action_filter"
  
  inline_keyboard = paginate_buttons(action, page_number, total_count_action, page_action, data.message.from_user.id)
  await bot.edit_message_text(result_message, data.message.chat.id, data.message.id, reply_markup=inline_keyboard)
  
  
async def action_history_download(message):
  await bot.send_message(message.chat.id, 'Выберите фильтр', reply_markup=action_history_filter_reply_markup(action="download:action"))


@bot.callback_query_handler(func=lambda x: re.match('download:action:', x.data))
async def action_page(data):
  await bot.edit_message_text("Подготовка файла к установке", data.message.chat.id, data.message.id)
  action = data.data.split(':')[2] # parameters = [type_of_callback, page_number, user_id]
  action_history = db_queries.show_action_history(data.message.chat.id, action=action, download=True)
  
  result_message = ""
  i = 1
  for action in action_history:
    result_message += f'[{i}]-----------------------------\nДата: {(action.date_time + timedelta(hours=3)).strftime("%m/%d/%Y, %H:%M:%S")}\n\nДействие: {action.description}\n-----------------------------\n\n'
    i+=1
    
  file = io.BytesIO(result_message.encode('utf-8'))
  file.name = "action_history.txt"
  await bot.delete_message(data.message.chat.id, data.message.id)
  
  await bot.send_document(chat_id=data.message.chat.id, document=file, caption="Файл готов")
  

# ------------------------------------------------------------------------------------------------------------------------------------------------

# --- правка ставки компании --------------------------------------------------------------------------------------------

async def send_message_for_advert_bid(message, adv_id):
  campaign_link = f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{adv_id}"
  result_msg = f'Укажите максимальную ставку для РК с id [{adv_id}]({campaign_link}) в рублях' #f"\t ID: [{advert['id']}]({campaign_link}) Статус: {stat}\n"
  await bot.send_message(message.chat.id, result_msg, parse_mode = 'MarkdownV2') 
  set_user_session_step(message, 'Add_advert')
  

# ------------------------------------------------------------------------------------------------------------------------------------------------


# --- добавление компании --------------------------------------------------------------------------------------------

async def add_advert(message):
  user_text = message.text
  adv_id = re.sub('/add_adv_', '', user_text)
  message.user_session['add_adv_id'] = adv_id
  await send_message_for_advert_bid(message, adv_id)
  # await bot.send_message(message.chat.id, f'Укажите максимальную ставку для РК с id {adv_id} в рублях')
  # set_user_session_step(message, 'Add_advert')
    


async def add_advert_with_define_id(message):
  user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
  adv_id = message.user_session.get('add_adv_id')
  if adv_id == None:
    adv_id = message.user_session.get('adv_settings_id')
  user_number_value = re.sub(r'[^0-9]', '', message.text)
  db_queries.add_user_advert(user, adv_id, user_number_value, status='ON')
  await bot.send_message(message.chat.id, f'РК с id {adv_id} отслеживается с максимальной ставкой {user_number_value}')
  message.user_session['add_adv_id'] = None
    

# --- Настройки компании --------------------------------------------------------------------------------------------

async def adv_settings(message):
  user_text = message.text
  adv_id = re.sub('/adv_settings_', '', user_text)
  message.user_session['adv_settings_id'] = adv_id
  await bot.send_message(message.chat.id, f'Ниже представлена панель, для возможных действий с компанией {adv_id}', reply_markup=adv_settings_reply_markup())


async def adv_settings_budget(message):
  adv_id = message.user_session.get('adv_settings_id')
  await send_message_for_advert_bid(message, adv_id)
  # await bot.send_message(message.chat.id, f'Укажите максимальную ставку для РК с id {adv_id} в рублях')
  # set_user_session_step(message, 'Add_advert')
    

# Подписка -----------------------------------------------------------------------------------------------------------------------

async def show_my_sub(message):
  user = db_queries.get_user_by_telegram_user_id(message.chat.id)
  my_sub = db_queries.get_sub(sub_id=user.subscriptions_id)
  if user.subscriptions_id:
    await bot.send_message(message.chat.id, 'Подключен: `{}`\nСрок действия с `{}` по `{}`'.format(my_sub.title, user.sub_start_date.strftime('%d/%m/%Y'), user.sub_end_date.strftime('%d/%m/%Y')), reply_markup=universal_reply_markup())
    if not "Advanced" in my_sub.title:
      await bot.send_message(message.chat.id, 'Вы можете обновиться на более крутую подписку', reply_markup=universal_reply_markup())
      sub_list = db_queries.get_all_sub()
      # if PAYMENT_TOKEN.split(':')[1] == 'LIVE':
      if PAYMENT_TOKEN.split(':')[1] == 'TEST':
        for sub in sub_list:
          if sub.title == my_sub.title:
            continue
          await bot.send_message(message.chat.id, f'Подписка - {sub.title}\nЦена - {sub.price}\nОписание - {sub.description}\n\nХотите ли вы оплатить через telegram?\nЕсли - Да, нажмите на кнопку `Оплата через телеграм`\nЕсли через сайт, нажмите на кнопку `Оплата через сайт`', reply_markup=reply_markup_payment(user_data=f"{sub.title}"))
  else:
    await bot.send_message(message.chat.id, 'У вас не подключено никаких платных подписок\nНиже предоставлены варианты для покупки: ')
    sub_list = db_queries.get_all_sub()
    # if PAYMENT_TOKEN.split(':')[1] == 'LIVE':
    if PAYMENT_TOKEN.split(':')[1] == 'TEST':
      for sub in sub_list:
        await bot.send_message(message.chat.id, f'Подписка - {sub.title}\nЦена - {sub.price}\nОписание - {sub.description}\n\nХотите ли вы оплатить через telegram?\nЕсли - Да, нажмите на кнопку `Оплата через телеграм`\nЕсли через сайт, нажмите на кнопку `Оплата через сайт`', reply_markup=reply_markup_payment(user_data=f"{sub.title}"))

# --------------------------------------------------------------------------------------------------------------------------------



# --- работа с сессией --------------------------------------------------------------------------------------------

def set_user_session_step(message, step_name):
  message.user_session['step'] = step_name
  message.user_session_step_set = True

def update_user_session(message):
  if message.user_session == message.user_session_old:
    return
  
  message.user_session['updated_at'] = str(datetime.now())
  cache_worker.set_user_session(message.from_user.id, message.user_session)



# --- маппинг степов --------------------------------------------------------------------------------------------

step_map = {
  'База': {
    'Помощь': help,
    'Поиск': search_adverts,
    'Моя подписка': show_my_sub,
    'Список рекламных компаний': list_adverts,
    'Выбрать город': choose_city,
    'Выбор:': choose_city_handler,
    'Установить токен': set_token_cmp,
    'История действий': show_action_history,
    'Дополнительные опции': menu_additional_options,
    'Выбрать фильтрацию': action_history_filter,
    'Загрузить историю действий': action_history_download,
    'Назад': menu_back,
    'add_adv_': add_advert,
    'adv_settings_': adv_settings,
    'Изменить максимальную ставку': adv_settings_budget,
    'default': misSpell
  },
  'Search_adverts': {
    'default': search_next_step_handler
  },
  'Set_token_cmp': {
    'default': set_token_cmp_handler
  },
  'Add_advert': {
    'default': add_advert_with_define_id
  }
}
