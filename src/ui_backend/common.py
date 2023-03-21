from datetime import datetime
from .bot import syncBot
from telebot import types
from db.queries import db_queries
from wb_common.wb_queries import wb_queries
from unittest import mock
from cache_worker.cache_worker import cache_worker
from collections import namedtuple
from .bot import bot

Campaign = namedtuple('Campaign', ['campaign_id'])
import re

import math

from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)

from ui_backend.message_queue import queue_message_sync
from ui_backend import mq_campaign_info

def try_except_decorator(fn):
    
    def the_wrapper(message):
        try:
            sucsess_message = fn(message)
            queue_message_sync(
              destination_id = message.chat.id,
              message = sucsess_message,
              request_message = message.text,
              parse_mode = 'MarkdownV2'
            )
            logger.info(f'{datetime.now()}: {message.from_user.id}: {message.text}: {sucsess_message}')
        except Exception as e:
            err_message = f'Произошла ошибка: {type(e).__name__}: {e}'
            queue_message_sync(
              destination_id = message.chat.id,
              request_message = message.text,
              error = err_message,
              message = 'На стороне сервера произошла ошибка! Обратитесь к разработчику или попробуйте позже',
              parse_mode = 'MarkdownV2'
            )
            logger.error(f'{datetime.now()}: {message.from_user.id}: {message.text}: {err_message}: {e}')

    return the_wrapper

def msg_handler(*args, **kwargs):
    def decorator(fn):
        return syncBot.message_handler(*args, **kwargs)(try_except_decorator(fn))
    return decorator


def universal_reply_markup(search=False):
  markup_inline = types.ReplyKeyboardMarkup(resize_keyboard=True)

  btn_search = types.KeyboardButton(text='🔎 Поиск 🔎')
  btn_list_adverts = types.KeyboardButton(text='📑 Список рекламных компаний 📑')
  btn_my_sub = types.KeyboardButton(text='💻 Моя подписка 💻')
  btn_additionally = types.KeyboardButton(text='⚙️ Дополнительные опции ⚙️')
  

  markup_inline.add(btn_search, btn_list_adverts, btn_my_sub)
  markup_inline.add(btn_additionally)
  
  if search:
    btn_choose_city = types.KeyboardButton(text='Выбрать город 🏙️')
    markup_inline.add(btn_choose_city)
    
  
  # if cache_worker.get_user_dev_mode(user_id=user_id) != None:
  #   btn_get_logs = types.KeyboardButton(text='Показать логи человека')
  #   markup_inline.add(btn_get_logs)
    
  return markup_inline


def adv_settings_reply_markup(telegram_user_id):
  user_session = cache_worker.get_user_session(telegram_user_id)
  markup_inline = types.ReplyKeyboardMarkup(resize_keyboard=True)

  btn_add_budget = types.KeyboardButton(text='Изменить максимальную ставку')
  btn_show_plus_word = types.KeyboardButton(text='Показать Плюс слова')
  btn_show_minus_word = types.KeyboardButton(text='Показать Минус слова')
  btn_back = types.KeyboardButton(text='⏪ Назад ⏪')
  
  
  logger.info(user_session)
  
  markup_inline.add(btn_add_budget, btn_show_plus_word, btn_show_minus_word)
  
  btn_switch_status = types.KeyboardButton(text='Изменить статус')
  if user_session.get('adv_fixed'):
    btn_switch_off_word = types.KeyboardButton(text='Выключить Фиксированные фразы')
    markup_inline.add(btn_switch_off_word, btn_switch_status)
  else:
    btn_switch_on_word = types.KeyboardButton(text='Включить Фиксированные фразы')
    markup_inline.add(btn_switch_on_word, btn_switch_status)
  
  
  markup_inline.add(btn_back)
  
    
  return markup_inline

def adv_settings_words_reply_markup(which_word):
  markup_inline = types.ReplyKeyboardMarkup(resize_keyboard=True)

  btn_add_word = types.KeyboardButton(text=f'Добавить {which_word} слово')
  # btn_add_word = types.KeyboardButton(text=f'Удалить {which_word}')
  btn_back = types.KeyboardButton(text='⏪ Назад ⏪')

  markup_inline.add(btn_add_word)
  markup_inline.add(btn_back)
    
  return markup_inline


def switch_status_reply_markup(status, campaing_id):
  markup_inline = types.InlineKeyboardMarkup()
  
  status_parse = status_parser(status)
  
  if status_parse == "Приостановлено":
    markup_inline.add(
      types.InlineKeyboardButton(text='Изменить на Активно', callback_data=f'status:change:active:{campaing_id}'),
      )
  elif status_parse == "Активна":
    markup_inline.add(
      types.InlineKeyboardButton(text='Изменить на Приостановлено', callback_data=f'status:change:pause:{campaing_id}'),
      )
  
  return markup_inline


def action_history_reply_markup():
  markup_inline = types.ReplyKeyboardMarkup(resize_keyboard=True)

  btn_action_filter = types.KeyboardButton(text='Выбрать фильтрацию')
  btn_download_actions = types.KeyboardButton(text='Загрузить историю действий')
  btn_back = types.KeyboardButton(text='⏪ Назад ⏪')

  markup_inline.add(btn_action_filter, btn_download_actions)
  markup_inline.add(btn_back)
    
  return markup_inline


def action_history_filter_reply_markup(action):
  markup_inline = types.InlineKeyboardMarkup()
  
  filters = db_queries.get_filter_action_history()
  buttons_array = []
  # logger.info(filters)
  markup_inline.add(types.InlineKeyboardButton(f'Все', callback_data=f'{action}:date_time'))
  for filter in filters:
    logger.info(filter[0])
    buttons_array.append(types.InlineKeyboardButton(f'{filter[0]}', callback_data=f'{action}:{filter[0]}'))
  
  markup_inline.row(*buttons_array)
  
  return markup_inline


def universal_reply_markup_additionally(user_id=None):
  markup_inline = types.ReplyKeyboardMarkup(resize_keyboard=True)

  btn_help = types.KeyboardButton(text='👨‍💻 Помощь 👨‍💻')
  btn_set_token_cmp = types.KeyboardButton(text='🔑 Установить токен 🔑')
  btn_get_logs = types.KeyboardButton(text='📋 История действий 📋')
  # btn_add_adverts = types.KeyboardButton(text='📄 Добавить рекламную компанию 📄')
  btn_back = types.KeyboardButton(text='⏪ Назад ⏪')


  markup_inline.add(btn_help, btn_set_token_cmp, btn_get_logs)
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
        # types.InlineKeyboardButton(text='Оплата через telegram', callback_data=f"Оплата Telegram {user_data}"),
        types.InlineKeyboardButton(text='Оплата через сайт', callback_data=f"Оплата Сайт {user_data}"),
    )
    return markup

def status_parser(status_id):
  status_dict = {
    4: 'Готова к запуску',
    9: 'Активна',
    8: 'Отказана',
    7: 'Показы завершены',
    11: 'Приостановлено',
  }
  return status_dict.get(status_id, 'Не найден')
  

def status_parser_priority_map(status_id):
  status_dict = {
    4: 5,
    9: 1,
    8: 4,
    7: 3,
    11: 2,
  }
  return status_dict.get(status_id, 99)
    

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
      button_label = f'-{button_label}-'
    buttons_array.append(types.InlineKeyboardButton(f'{button_label}', callback_data=f'{action}:{i}:{user_id}'))

  inline_keyboard.row(*buttons_array)
  return inline_keyboard


def get_first_place(user_id, campaign):
  campaign_user = db_queries.get_user_by_telegram_user_id(user_id)
  campaign_info = wb_queries.get_campaign_info(campaign_user, campaign)
  campaign_pluse_words = wb_queries.get_stat_words(campaign_user, campaign)

  check_word = campaign_info['campaign_key_word']
  if campaign_pluse_words['main_pluse_word']:
    check_word = campaign_pluse_words['main_pluse_word']

  current_bids_table = wb_queries.search_adverts_by_keyword(check_word)
  
  logger.info("current_bids_table")
  logger.info(current_bids_table)

  return current_bids_table[0]['price'] + 1


def escape_telegram_specials(string):
  return re.sub(r'([_*\[\]\(\)~`>#+-=|{}.!])', r'\\\1', string)

  
def logs_types_reply_markup(user_id, timestamp):

    markup_inline = types.InlineKeyboardMarkup()

    btn_wb_queries = types.InlineKeyboardButton(text='wb_queries', callback_data=f'logs: wb_queries user_id: {user_id} timestamp: {timestamp}')

    markup_inline.add(btn_wb_queries)

    return markup_inline

def advert_info_message_maker(adverts, page_number, page_size, user):
  adverts = sorted(adverts, key=lambda x: status_parser_priority_map(x['statusId']))
  
  if page_number != 1:
    adverts = adverts[(page_size*(page_number-1)):page_size*page_number]
  else:
    adverts = adverts[page_number-1:page_size]
  

  lst_adverts_ids = [i['id'] for i in adverts]
  db_adverts = db_queries.get_user_adverts_by_wb_ids(user.id, lst_adverts_ids)
  id_to_db_adverts = {x.campaign_id: x for x in db_adverts}
  lst_adverts_ids = [i.campaign_id for i in db_adverts]

  result_msg = f'Список ваших рекламных компаний с cmp\.wildberries\.ru, страница: {page_number}\n\n'
  for advert in adverts:
    stat = status_parser(advert['statusId'])

    campaign = mock.Mock()
    campaign.campaign_id = advert['id']

    budget_string = ''
    try:
      # first_place_price = get_first_place(user.telegram_user_id, campaign)
      budget = wb_queries.get_budget(user, campaign)
      budget = budget.get("Бюджет компании")
    except Exception as e:
      logger.info(e)

    if budget is not None:
      budget_string = f"\t Бюджет компании {budget}\n"
    else:
      budget_string = f"\t ВБ не вернул бюджет компании\!\n"

    add_delete_str = ''
    bot_status = ''
    if advert['id'] in lst_adverts_ids:
      db_advert = id_to_db_adverts.get(advert['id'])
      if (db_advert):
          bot_status     += f"\t Отслеживается\!"
          add_delete_str += f"\t Перестать отслеживать РК: /delete\_adv\_{advert['id']}\n"
          add_delete_str += f"\t Максимальная ставка: {db_advert.max_budget}\n"
    else:
      bot_status     += f"\t Не отслеживается\!"
      add_delete_str += f"\t Отслеживать РК: /add\_adv\_{advert['id']}\n"

    add_delete_str += f"\t Настроить РК: /adv\_settings\_{advert['id']}\n"

    campaign_link = f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{advert['id']}"
    
    result_msg += f"*Имя компании: {advert['campaignName']}*\n"
    result_msg += f"\t ID: [{advert['id']}]({campaign_link}) Статус: {stat}\n"

    result_msg += budget_string

    result_msg += bot_status
    # TODO Текущая ставка
    result_msg += add_delete_str
    # TODO Текущие ставки на 1-2 месте по рекламному слову
    result_msg += f"\n"
  return result_msg

# campaign_link = f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{advert['id']}"
# result_msg += f"\t ID: [{advert['id']}]({campaign_link}) Статус: {stat}\n"

async def test_adverts_list(adverts, page_number, page_size, chat_id, user):
  adverts = sorted(adverts, key=lambda x: status_parser_priority_map(x['statusId']))
  
  if page_number != 1:
    adverts = adverts[(page_size*(page_number-1)):page_size*page_number]
  else:
    adverts = adverts[page_number-1:page_size]

  msg = bot.send_message(chat_id, 'Вайлдберис старается 🔄', parse_mode='MarkdownV2')
  

  lst_adverts_ids = [i['id'] for i in adverts]
  data = campaign_query_info_maker(lst_adverts_ids, user, msg.id)
  data.set(page_number)

  await mq_campaign_info.queue_message_async(data)




def campaign_query_info_maker(lst_adverts_ids, user, message_id) -> dict:
  list_with_need_query = []
  for advert_id in lst_adverts_ids:
    obj = {
      "aid": advert_id,
      "msg_id": message_id,
      "campaign_budget":{
        "fn": 'wrapper_get_budget',
        "kwargs": {"user_id": user.id, "campaign_id": advert_id},
        "status": "active"
      },
      "first_place_price":{
        "fn": 'get_first_place',
        "fn_place": 'ui_backend.common',
        "kwargs": {"user_id": user.id, "campaign_id": advert_id},
        "status": "active"
      },
    }
    list_with_need_query.append(obj)
  return list_with_need_query

def wrapper_get_budget(user_id, campaign_id):
  campaign = mock.Mock()
  campaign.campaign_id = campaign_id
  user = db_queries.get_user_by_id(user_id)

  wb_queries.get_budget(user, campaign)

def get_first_place(user_id, campaign_id):
  get_first_place(user_id, campaign_id)