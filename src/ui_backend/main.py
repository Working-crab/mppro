
import json
import telebot
import requests
import re

from ui_backend.db.queries import db_queries
from wb_common.wb_queries import wb_queries

BOT_NAME = 'mp_pro_bot'
TOKEN = '5972133433:AAERP_hpf9p-zYjTigzEd-MCpQWGQNCvgWs'

#Создание бота
bot = telebot.TeleBot(TOKEN)

def try_except_decorator(fn):
    
    def the_wrapper(message):
        try:
            bot.send_message(message.chat.id, fn(message))
        except Exception as e:
            bot.send_message(message.chat.id, f'Произошла ошибка: {type(e).__name__}: {e}')

    return the_wrapper

#Команды бота
@bot.message_handler(commands=['start'])
def start(message):
    db_queries.create_user(telegram_user_id=message.from_user.id, telegram_chat_id=message.chat.id, telegram_username=message.from_user.username)
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}')


@bot.message_handler(commands=['set_token_cmp'])
def set_token_cmp(message):
    try:
        clear_token = message.text.replace('/set_token_cmp ', '').strip()
        db_queries.set_user_wb_cmp_token(telegram_user_id=message.from_user.id, wb_cmp_token=clear_token)
        bot.send_message(message.chat.id, f'Ваш токен установлен!')
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {e}')


@bot.message_handler(commands=['get_token_cmp'])
def getToken(message):
    try:
        token = db_queries.get_user_wb_cmp_token(telegram_user_id=message.from_user.id)
        bot.send_message(message.chat.id, f'Ваш токен: {token}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {e}')


@bot.message_handler(commands=['search'])
def search(message):
    try:
        keyword = re.sub('/search ', '', message.text)
        item_dicts = wb_queries.search_adverts_by_keyword(keyword)
        result_message = ''

        if len(item_dicts) == 0:
            return bot.send_message(message.chat.id, 'ставки неизвестны')
        else:
            for item_idex in range(len(item_dicts)):
                price = item_dicts[item_idex]['price']
                p_id = item_dicts[item_idex]['p_id']
                # TODO Сделать вывод по-красивше
                result_message += f'{item_idex + 1})  {price}р,  https://www.wildberries.ru/catalog/{p_id}/detail.aspx \n'
            bot.send_message(message.chat.id, result_message)

    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {e}')


@bot.message_handler(commands=['list_atrevds'])
def list_atrevds(message):
  try:
    user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
    user_wb_tokens = wb_queries.get_base_tokens(user)
    req_params = wb_queries.get_base_request_params(user_wb_tokens)

    status_dict = { # TODO УБРАТЬ ЭТОТ СРАМ!
      '4': 'Готова к запуску',
      '9': 'Активна',
      '8': 'Отказана',
      '11': 'Приостановлено',
    }

    # TODO Вынести запрос в wb_queries
    user_atrevds = requests.get('https://cmp.wildberries.ru/backend/api/v3/atrevds?order=createDate', cookies=req_params['cookies'], headers=req_params['headers'])
    view = user_atrevds.json()['content']
    result_msg = ''

    for product in view:
        date_str = product['startDate']
        
        stat = status_dict.get(product['statusId'], 'Статус не известен')
        if date_str != None:
            date_str = date_str[:10]
        
        # TODO Сделать вывод по-красивше
        result_msg += f"{product['id']} \t {product['categoryName']} \t {product['campaignName']} \t {product['campaignId']} \t {date_str} {stat}\n"
    

    bot.send_message(message.chat.id, result_msg)

  except Exception as e:
      bot.send_message(message.chat.id, f'Произошла ошибка: {e}')


@bot.message_handler(commands=['add_advert'])
def add_advert(message):
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
          bot.send_message(message.chat.id, f'Для использования команды используйте формат: /add_advert <campaign_id> <max_budget> <place> <status>')
          return

        compagin_id = re.sub('/add_advert ', '', message_args[0])
        max_budget = re.sub('/add_advert ', '', message_args[1])
        place = re.sub('/add_advert ', '', message_args[2])
        status = re.sub('/add_advert ', '', message_args[3])

        db_queries.add_user_advert(user, status, compagin_id, max_budget, place)
        bot.send_message(message.chat.id, 'Ваша рекламная компания успешно добавлена!')
        
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {e}')

  
@bot.message_handler(commands=['get_adverts'])
def get_adverts(message):
    try:
        user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
        adverts = db_queries.get_user_adverts(user.id)

        result = json.dumps(adverts)

        if not adverts:
          result = 'Вы ещё не добавили нам команий! Используйте add_advert'
        
        bot.send_message(message.chat.id, result)
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {e}')



@bot.message_handler(commands=['reset_base_tokens'])
def reset_base_tokens(message):
    try:
        user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
        tokens = wb_queries.reset_base_tokens(user)
        
        bot.send_message(message.chat.id, str(tokens))
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {e}')

@bot.message_handler(commands=['test'])
@try_except_decorator
def print_test(message):
    if len(message.text.split()) > 1:
        return message
    else:
        raise Exception('Ахуеть какая ебейшая ошибка и сообщение пиздатое и правильное')

# TODO Сделать хелп команду

# TODO Сделать общий абстрактный декоратор

#Начало пулинга
bot.polling(interval=3, none_stop=True)