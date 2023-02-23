from ui_backend.app import bot
from ui_backend.common import universal_reply_markup, status_parser, paginate_buttons
import re
from telebot import types
from db.queries import db_queries
from wb_common.wb_queries import wb_queries
import traceback

from ui_backend.message_queue import queue_message

from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)

# Ветка "Поиск" --------------------------------------------------------------------------------------------------------
@bot.message_handler(regexp='Поиск')
def cb_adverts(message):
    try:
        sent = bot.send_message(message.chat.id, 'Введите ключевое слово', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(sent,search_next_step_handler)
    except Exception as e:
        bot.send_message(message.chat.id, e)
        
def search_next_step_handler(message):
    try:
        keyword = re.sub('/search ', '', message.text)
        item_dicts = wb_queries.search_adverts_by_keyword(keyword)
        result_message = ''

        if len(item_dicts) == 0:
            bot.send_message(message.chat.id, 'Такой товар не найден', reply_markup=universal_reply_markup())
        else:
            for item_idex in range(len(item_dicts)):
                price = item_dicts[item_idex]['price']
                p_id = item_dicts[item_idex]['p_id']
                result_message += f'\\[{item_idex + 1}\\]   *{price}₽*,  [{p_id}](https://www.wildberries.ru/catalog/{p_id}/detail.aspx) 🛍\n'
            bot.send_message(message.chat.id, result_message, reply_markup=universal_reply_markup(), parse_mode='MarkdownV2')
    except Exception as e:
        bot.send_message(message.chat.id, e, reply_markup=universal_reply_markup())
# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Помощь" ---------------------------------------------------------------------------------------------------------------------------------

@bot.message_handler(regexp='Помощь')
def cb_adverts(message):
  queue_message(
    destination_id=message.chat.id,
    message='По вопросам работы бота обращайтесь: \n (https://t.me/tNeymik) \n (https://t.me/plazmenni_rezak)',
    user_id=message.from_user.id
  )    
  pass
# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Установить токен" -----------------------------------------------------------------------------------------------------------------------
@bot.message_handler(regexp='Установить токен')
def cb_adverts(message):
    try:
        sent = bot.send_message(message.chat.id, 'Введите токен', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(sent,set_token_cmp_handler)
    except Exception as e:
        bot.send_message(message.chat.id, e, reply_markup=universal_reply_markup())

def set_token_cmp_handler(message):
    try:
        clear_token = message.text.replace('/set_token_cmp ', '').strip()
        db_queries.set_user_wb_cmp_token(telegram_user_id=message.from_user.id, wb_cmp_token=clear_token)
        
        bot.send_message(message.chat.id, 'Ваш токен установлен\!', reply_markup=universal_reply_markup(), parse_mode='MarkdownV2')

    except Exception as e:
        logger.error(e)
# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Список рекламных компаний" --------------------------------------------------------------------------------------------------------------
@bot.message_handler(regexp='Список рекламных компаний')
def cb_adverts(message):

    try:

      # msg = bot.send_message(message.chat.id, "Вайлдберис говно 🔄")
      list_adverts_handler(message)
      # bot.edit_message_text('Готово', msg.chat.id, msg.id)

    except Exception as e:
        traceback.print_exc() # Maxim molodec TODO print_exc in all Exceptions
        logger.error(e)
        bot.send_message(message.chat.id, e, reply_markup=universal_reply_markup())


def list_adverts_handler(message):

  user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
  user_wb_tokens = wb_queries.get_base_tokens(user)
  req_params = wb_queries.get_base_request_params(user_wb_tokens)
  

  page_number = 1
  user_atrevds_data = wb_queries.get_user_atrevds(req_params, page_number)

  result_msg = f'Список ваших рекламных компаний с cmp\.wildberries\.ru, страница: {page_number}\n\n'
  for advert in user_atrevds_data['adverts']:
    date_str = advert['startDate']
    stat = status_parser(advert['statusId'])

    if date_str != None:
      date_str = date_str[:10]
      date_str = re.sub('-', '\-', date_str)
    
    result_msg += f"*Имя компании: {advert['campaignName']}*\n"
    result_msg += f"\t ID Рекламной компании: {advert['id']}\n"
    result_msg += f"\t Имя категории: {advert['categoryName']}\n"
    result_msg += f"\t Дата начала: {date_str}\n"
    result_msg += f"\t Текущий статус: {stat}\n\n"

  page_size = 6
  total_count_adverts = user_atrevds_data['total_count']
  inline_keyboard = paginate_buttons(page_number, total_count_adverts, page_size, message.from_user.id)
  
  try:
    bot.send_message(message.chat.id, result_msg, reply_markup=inline_keyboard, parse_mode='MarkdownV2')
    # bot.edit_message_text("result_msg ✅", message.chat.id, message.message_id)
    # bot.edit_message_reply_markup(message.chat.id, message.id, reply_markup=inline_keyboard)
  except Exception as e:
    #   bot.send_message(message.chat.id, e, reply_markup=universal_reply_markup())
    logger.error(e)
# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Добавить рекламную компанию" ------------------------------------------------------------------------------------------------------------
@bot.message_handler(regexp='Добавить рекламную компанию')
def cb_adverts(message):
    try:
        msg_text = 'Введите данные в формате "<campaign_id> <max_budget> <place> <status>" в следующем сообщение.'
        sent = bot.send_message(message.chat.id, msg_text, reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(sent,add_advert_handler)
    except Exception as e:
        bot.send_message(message.chat.id, e)

def add_advert_handler(message):
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
            bot.send_message(message.chat.id, msg_text, reply_markup=universal_reply_markup())
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

        bot.send_message(message.chat.id, res_msg, reply_markup=universal_reply_markup(), parse_mode='MarkdownV2')
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то пошло не так', reply_markup=universal_reply_markup())
        logger.error(e)
# ------------------------------------------------------------------------------------------------------------------------------------------------

@bot.callback_query_handler(func=lambda x: re.match('page', x.data))
def kek(data):
    try:
      bot.edit_message_text('Вайлдберис старается 🔄', data.message.chat.id, data.message.id, parse_mode='MarkdownV2')
      type_of_callback, page_number, user_id = data.data.split(':') # parameters = [type_of_callback, page_number, user_id]
      page_number = int(page_number)
      user = db_queries.get_user_by_telegram_user_id(user_id)
      user_wb_tokens = wb_queries.get_base_tokens(user)
      req_params = wb_queries.get_base_request_params(user_wb_tokens)
      user_atrevds_data = wb_queries.get_user_atrevds(req_params, page_number)

      result_msg = f'Список ваших рекламных компаний с cmp\.wildberries\.ru, страница: {page_number}\n\n'
      for advert in user_atrevds_data['adverts']:
        date_str = advert['startDate']
        stat = status_parser(advert['statusId'])
        
        if date_str != None:
          date_str = date_str[:10]
          date_str = re.sub('-', '\-', date_str)
        
        result_msg += f"*Имя компании: {advert['campaignName']}*\n"
        result_msg += f"\t ID Рекламной компании: {advert['id']}\n"
        result_msg += f"\t Имя категории: {advert['categoryName']}\n"
        result_msg += f"\t Дата начала: {date_str}\n"
        result_msg += f"\t Текущий статус: {stat}\n\n"

      total_count = user_atrevds_data['total_count']
      page_size = 6
      inline_keyboard = paginate_buttons(page_number, total_count, page_size, user_id)

      bot.edit_message_text(result_msg, data.message.chat.id, data.message.id, parse_mode='MarkdownV2')
      bot.edit_message_reply_markup(data.message.chat.id, data.message.id , reply_markup=inline_keyboard)
      bot.answer_callback_query(data.id)
    except Exception as e:
        bot.send_message(data.message.chat.id, e)