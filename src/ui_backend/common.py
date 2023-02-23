from datetime import datetime
from .bot import bot
import logging
from telebot import types

import math

logging.basicConfig(filename="logs/loger_user_actions.log")
logger = logging.getLogger(__name__)

def try_except_decorator(fn):
    
    def the_wrapper(message):
        try:
            sucsess_message = fn(message)
            bot.send_message(message.chat.id, sucsess_message)
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


def universal_reply_markup():

    markup_inline = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn_help = types.KeyboardButton(text='Помощь')
    btn_search = types.KeyboardButton(text='Поиск')
    btn_set_token_cmp = types.KeyboardButton(text='Установить токен')

    btn_list_adverts = types.KeyboardButton(text='Список рекламных компаний')
    btn_add_adverts = types.KeyboardButton(text='Добавить рекламную компанию')

    markup_inline.add(btn_help, btn_search, btn_set_token_cmp, btn_list_adverts, btn_add_adverts)

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


def paginate_buttons(page_number, total_count_adverts, page_size, user_id):
  start_index = 0
  end_index = 0
  page_count = math.ceil(total_count_adverts/page_size)

  if(page_number <= 3):
    start_index = 1
    end_index = 6
  elif(page_number >= page_count-2):
    start_index = page_count-4
    end_index = page_count+1
  else:
    start_index = page_number - 2
    end_index = page_number + 3

  buttons_array = []
  inline_keyboard = types.InlineKeyboardMarkup()
  for i in range(start_index, end_index):
    buttons_array.append(types.InlineKeyboardButton(f'{i}', callback_data=f'page:{i}:{user_id}'))

  inline_keyboard.row(*buttons_array)
  return inline_keyboard