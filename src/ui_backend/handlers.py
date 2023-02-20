from ui_backend.app import bot
from ui_backend.common import universal_reply_markup, status_parser
import re
from datetime import datetime
from telebot import types
from db.queries import db_queries
from wb_common.wb_queries import wb_queries
import traceback

import time

# from ui_backend.message_queue import queue_message

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
            bot.send_message(message.chat.id, 'Такой товар не найден', reply_markup=universal_reply_markup(message.chat.id))
        else:
            for item_idex in range(len(item_dicts)):
                price = item_dicts[item_idex]['price']
                p_id = item_dicts[item_idex]['p_id']
                result_message += f'\\[{item_idex + 1}\\]   *{price}₽*,  [{p_id}](https://www.wildberries.ru/catalog/{p_id}/detail.aspx) 🛍\n'
            bot.send_message(message.chat.id, result_message, reply_markup=universal_reply_markup(message.from_user.id), parse_mode='MarkdownV2')
    except Exception as e:
        bot.send_message(message.chat.id, e, reply_markup=universal_reply_markup(message.chat.id))
# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Помощь" ---------------------------------------------------------------------------------------------------------------------------------

@bot.message_handler(regexp='Помощь')
def cb_adverts(message):
  # queue_message(
  #   destination_id=message.chat.id,
  #   message='По вопросам работы бота обращайтесь: \n (https://t.me/tNeymik) \n (https://t.me/plazmenni_rezak)',
  #   user_id=message.from_user.id
  # )    
  pass
# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Установить токен" -----------------------------------------------------------------------------------------------------------------------
@bot.message_handler(regexp='Установить токен')
def cb_adverts(message):
    try:
        sent = bot.send_message(message.chat.id, 'Введите токен', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(sent,set_token_cmp_handler)
    except Exception as e:
        bot.send_message(message.chat.id, e, reply_markup=universal_reply_markup(message.from_user.id))

def set_token_cmp_handler(message):
    try:
        clear_token = message.text.replace('/set_token_cmp ', '').strip()
        db_queries.set_user_wb_cmp_token(telegram_user_id=message.from_user.id, wb_cmp_token=clear_token)
        
        bot.send_message(message.chat.id, 'Ваш токен установлен\!', reply_markup=universal_reply_markup(message.from_user.id), parse_mode='MarkdownV2')

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
  

  page = 1
  view = wb_queries.get_user_atrevds(req_params, page)
  result_msg = ''

  inline_keyboard = types.InlineKeyboardMarkup()
  button1 = types.InlineKeyboardButton('1',callback_data='page:1')
  button2 = types.InlineKeyboardButton('2',callback_data='page:2')
  button3 = types.InlineKeyboardButton('3',callback_data='page:3')
  button4 = types.InlineKeyboardButton('4',callback_data='page:4')
  button5 = types.InlineKeyboardButton('5',callback_data='page:5')
  inline_keyboard.row(button1, button2, button3, button4, button5)

  for product in view:
      date_str = product['startDate']
      
      stat = status_parser(product['statusId'])
      if date_str != None:
          date_str = date_str[:10]
          date_str = re.sub('-', '\-', date_str)
      
      result_msg += f"*Имя компании: {product['campaignName']}*\n"
      result_msg += f"\t ID Рекламной компании: {product['id']}\n"
      result_msg += f"\t Имя категории: {product['categoryName']}\n"
      result_msg += f"\t Дата начала: {date_str}\n"
      result_msg += f"\t Текущий статус: {stat}\n\n"

  try:
    bot.send_message(message.chat.id, result_msg, reply_markup=universal_reply_markup(message.from_user.id))
    # bot.edit_message_text("result_msg ✅", message.chat.id, message.message_id)
    # bot.edit_message_reply_markup(message.chat.id, message.id, reply_markup=inline_keyboard)
  except Exception as e:
    #   bot.send_message(message.chat.id, e, reply_markup=universal_reply_markup(message.from_user.id))
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
            bot.send_message(message.chat.id, msg_text, reply_markup=universal_reply_markup(message.from_user.id))
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

        bot.send_message(message.chat.id, res_msg, reply_markup=universal_reply_markup(message.from_user.id), parse_mode='MarkdownV2')
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то пошло не так', reply_markup=universal_reply_markup(message.from_user.id))
        logger.error(e)
# ------------------------------------------------------------------------------------------------------------------------------------------------

@bot.callback_query_handler(func=lambda x: re.match('page', x.data))
def kek(data):
    try:
        bot.answer_callback_query(data.id)
        bot.send_message(data.message.chat.id, re.sub('page:', '', data.data)) 
    except Exception as e:
        bot.send_message(data.message.chat.id, e)