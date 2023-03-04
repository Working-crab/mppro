from datetime import datetime
from .bot import bot
from telebot import types
from db.queries import db_queries
from wb_common.wb_queries import wb_queries
from cache_worker.cache_worker import cache_worker
from collections import namedtuple
Campaign = namedtuple('Campaign', ['campaign_id'])
import re

import math

from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)

def try_except_decorator(fn):
    
    def the_wrapper(message):
        try:
            sucsess_message = fn(message)
            bot.send_message(message.chat.id, sucsess_message, parse_mode='MarkdownV2')
            logger.info(f'{datetime.now()}: {message.from_user.id}: {message.text}: {sucsess_message}')
        except Exception as e:
            err_message = f'Произошла ошибка: {type(e).__name__}: {e}'
            bot.send_message(message.chat.id, err_message)
            logger.error(f'{datetime.now()}: {message.from_user.id}: {message.text}: {err_message}: {e}')

    return the_wrapper

def msg_handler(*args, **kwargs):
    def decorator(fn):
        return bot.message_handler(*args, **kwargs)(try_except_decorator(fn))
    return decorator


def universal_reply_markup(search=False):
  markup_inline = types.ReplyKeyboardMarkup(resize_keyboard=True)

  btn_search = types.KeyboardButton(text='🔎 Поиск 🔎')
  btn_list_adverts = types.KeyboardButton(text='📑 Список рекламных компаний 📑')
  btn_additionally = types.KeyboardButton(text='⚙️ Дополнительные опции ⚙️')

  markup_inline.add(btn_search, btn_list_adverts)
  markup_inline.add(btn_additionally)
  
  if search:
    btn_choose_city = types.KeyboardButton(text='Выбрать город 🏙️')
    markup_inline.add(btn_choose_city)
    
  
  # if cache_worker.get_user_dev_mode(user_id=user_id) != None:
  #   btn_get_logs = types.KeyboardButton(text='Показать логи человека')
  #   markup_inline.add(btn_get_logs)
    
  return markup_inline


def universal_reply_markup_additionally(user_id=None):
  markup_inline = types.ReplyKeyboardMarkup(resize_keyboard=True)

  btn_help = types.KeyboardButton(text='👨‍💻 Помощь 👨‍💻')
  btn_set_token_cmp = types.KeyboardButton(text='🔑 Установить токен 🔑')
  btn_get_logs = types.KeyboardButton(text='📋 История действий 📋')
  btn_add_adverts = types.KeyboardButton(text='📄 Добавить рекламную компанию 📄')
  btn_back = types.KeyboardButton(text='⏪ Назад ⏪')


  markup_inline.add(btn_help, btn_set_token_cmp, btn_add_adverts, btn_get_logs)
  markup_inline.add(btn_back)
    
  return markup_inline

  
  
def city_reply_markup():

    markup_inline = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn_moscow = types.KeyboardButton(text='Выбор: Москва')
    btn_kazan = types.KeyboardButton(text='Выбор: Казань')
    btn_krasnodar = types.KeyboardButton(text='Выбор: Краснодар')
    btn_piter = types.KeyboardButton(text='Выбор: Санкт–Петербург')

    markup_inline.add(btn_moscow, btn_kazan, btn_krasnodar, btn_piter)

    return markup_inline



def reply_markup_trial(trial):
    markup = types.InlineKeyboardMarkup()
    if not trial:
        markup.add(
            types.InlineKeyboardButton(text='Согласиться', callback_data='Trial_Yes'),
            types.InlineKeyboardButton(text='Отказаться', callback_data='Trial_No'),
            types.InlineKeyboardButton(text='Информация', callback_data='Trial_info'),
        )
    else:
        markup.add(
            types.InlineKeyboardButton(text='Информация', callback_data='Trial_info'),
        )
    return markup


def reply_markup_payment(user_data):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(text='Оплата через telegram', callback_data=f"Telegram {user_data}"),
        types.InlineKeyboardButton(text='Оплата через сайт', callback_data=f"Сайт {user_data}"),
    )
    return markup

def status_parser(status_id):
    status_dict = {
      4: 'Готова к запуску',
      9: 'Активна',
      8: 'Отказана',
      11: 'Приостановлено',
    }
    return status_dict.get(status_id, 'Статус не известен')
    

def get_reply_markup(markup_name):
  if markup_name in locals():
    return locals()[markup_name]()
  else:
    return universal_reply_markup()


def paginate_buttons(action, page_number, total_count_adverts, page_size, user_id):
  start_index = 0
  end_index = 0
  page_count = math.ceil(total_count_adverts/page_size)

  if page_count >= 6:  
    if(page_number <= 3):
      start_index = 1
      end_index = 6
    elif(page_number >= page_count-2):
      start_index = page_count-4
      end_index = page_count+1
    else:
      start_index = page_number - 2
      end_index = page_number + 3
  else:
    start_index = 1
    end_index = page_count + 1

  buttons_array = []
  inline_keyboard = types.InlineKeyboardMarkup()
  for i in range(start_index, end_index):
    button_label = i
    if i == page_number:
      button_label = f':{button_label}:'
    buttons_array.append(types.InlineKeyboardButton(f'{button_label}', callback_data=f'{action}:{i}:{user_id}'))

  inline_keyboard.row(*buttons_array)
  return inline_keyboard


# def action_paginate_buttons(page_number, total_count_action, page_action, user_id):
#   start_index = 0
#   end_index = 0
#   page_count = math.ceil(total_count_action/page_action)

#   if page_count >= 6:
#     if(page_number <= 3):
#       start_index = 1
#       end_index = 6
#     elif(page_number >= page_count-2):
#       start_index = page_count-4
#       end_index = page_count+1
#     else:
#       start_index = page_number - 2
#       end_index = page_number + 3
#   else:
#     if(page_number <= 3):
#       start_index = 1
#       end_index = page_count + 1

#   buttons_array = []
#   inline_keyboard = types.InlineKeyboardMarkup()
#   for i in range(start_index, end_index):
#     buttons_array.append(types.InlineKeyboardButton(f'{i}', callback_data=f'action:{i}:{user_id}'))

#   inline_keyboard.row(*buttons_array)
#   return inline_keyboard

# def paginate_buttons(user_id, content, items_per_page, page_num):
#   num_pages = len(content) // items_per_page
#   if len(content) % items_per_page != 0:
#       num_pages += 1

#   buttons = []
#   start_index = (page_num - 1) * items_per_page
#   end_index = start_index + items_per_page
#   for i in range(start_index, end_index):
#       if i < len(content):
#           buttons.append(types.InlineKeyboardButton(content[i], callback_data=f'page_history:{i}:{user_id}'))
#   return buttons


def get_bids_table(user_id, campaign_id):
  campaign = Campaign(campaign_id)
  campaign_user = db_queries.get_user_by_telegram_user_id(user_id)
  campaign_info = wb_queries.get_campaign_info(campaign_user, campaign)
  campaign_pluse_words = wb_queries.get_stat_words(campaign_user, campaign)

  check_word = campaign_info['campaign_key_word']
  if campaign_pluse_words['main_pluse_word']:
    check_word = campaign_pluse_words['main_pluse_word']

  current_bids_table = wb_queries.search_adverts_by_keyword(check_word)
  logger.info(current_bids_table)
  return current_bids_table[0]['price']


def escape_telegram_specials(string):
  return re.sub(r'([_*\[\]\(\)~`>#+-=|{}.!])', r'\\\1', string)

  
  
def logs_types_reply_markup(user_id, timestamp):

    markup_inline = types.InlineKeyboardMarkup()

    btn_wb_queries = types.InlineKeyboardButton(text='wb_queries', callback_data=f'logs: wb_queries user_id: {user_id} timestamp: {timestamp}')

    markup_inline.add(btn_wb_queries)

    return markup_inline

def advert_info_message_maker(adverts, page_number, **header):
  result_msg = f'Список ваших рекламных компаний с cmp\.wildberries\.ru, страница: {page_number}\n\n'
  if header:
    result_msg = header

  # /delete_adv
  lst_adverts = [i['id'] for i in adverts]
  logger.info(lst_adverts)
  
  for advert in adverts:
    date_str = advert['startDate']
    stat = status_parser(advert['statusId'])

    if date_str != None:
      date_str = date_str[:10]
      date_str = re.sub('-', '\-', date_str)
    
    result_msg += f"*Имя компании: {advert['campaignName']}*\n"
    result_msg += f"\t ID Рекламной компании: {advert['id']}\n"
    result_msg += f"\t Имя категории: {advert['categoryName']}\n"
    result_msg += f"\t Отслеживать РК: /add\_adv\_{advert['id']}\n" 
    result_msg += f"\t Текущий статус: {stat}\n\n"
  return result_msg