
import json
import telebot
import requests
import re
import logging
logger = logging.getLogger(__name__)

from ui_backend.db.queries import db_queries
from wb_common.wb_queries import wb_queries

BOT_NAME = 'mp_pro_bot'
TOKEN = '5972133433:AAERP_hpf9p-zYjTigzEd-MCpQWGQNCvgWs'

#Создание бота
bot = telebot.TeleBot(TOKEN)

def try_except_decorator(fn):
    
    def the_wrapper(message):
        try:
            logger.info(f'{message.from_user.id}: {message.text}')
            bot.send_message(message.chat.id, fn(message)) # , parse_mode='MarkdownV2'
        except Exception as e:
            logger.error(e)
            bot.send_message(message.chat.id, f'Произошла ошибка: {type(e).__name__}: {e}')

    return the_wrapper

def msg_handler(*args, **kwargs):
    def decorator(fn):
        return bot.message_handler(*args, **kwargs)(try_except_decorator(fn))
    return decorator


#Команды бота
@msg_handler(commands=['start'])
def start(message):
    db_queries.create_user(telegram_user_id=message.from_user.id, telegram_chat_id=message.chat.id, telegram_username=message.from_user.username)
    return f'Здравствуйте, {message.from_user.first_name}'


@msg_handler(commands=['set_token_cmp'])
def set_token_cmp(message):
    clear_token = message.text.replace('/set_token_cmp ', '').strip()
    db_queries.set_user_wb_cmp_token(telegram_user_id=message.from_user.id, wb_cmp_token=clear_token)
    return 'Ваш токен установлен!'


@msg_handler(commands=['get_token_cmp'])
def getToken(message):

    token = db_queries.get_user_wb_cmp_token(telegram_user_id=message.from_user.id)
    return token


@msg_handler(commands=['search'])
def search(message):
        keyword = re.sub('/search ', '', message.text)
        item_dicts = wb_queries.search_adverts_by_keyword(keyword)
        result_message = ''

        if len(item_dicts) == 0:
            return 'ставки неизвестны'
        else:
            for item_idex in range(len(item_dicts)):
                price = item_dicts[item_idex]['price']
                p_id = item_dicts[item_idex]['p_id']
                # TODO Сделать вывод по-красивше
                result_message += f'{item_idex + 1}\\)  {price}р,  [ссылка на товар](https://www.wildberries.ru/catalog/{p_id}/detail.aspx) \n' 
            return result_message



@msg_handler(commands=['list_atrevds'])
def list_atrevds(message):
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
    

    return result_msg


@msg_handler(commands=['add_advert'])
def add_advert(message):
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
        bot.send_message(message.chat.id, f'Для использования команды используйте формат: /add_advert <campaign_id> <max_budget> <place> <status>')
        return

    compagin_id = re.sub('/add_advert ', '', message_args[0])
    max_budget = re.sub('/add_advert ', '', message_args[1])
    place = re.sub('/add_advert ', '', message_args[2])
    status = re.sub('/add_advert ', '', message_args[3])

    db_queries.add_user_advert(user, status, compagin_id, max_budget, place)
    return 'Ваша рекламная компания успешно добавлена!'
    

  
@msg_handler(commands=['get_adverts'])
def get_adverts(message):

    user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
    adverts = db_queries.get_user_adverts(user.id)

    result = json.dumps(adverts)

    if not adverts:
        result = 'Вы ещё не добавили нам команий! Используйте add_advert'
    
    return result



@msg_handler(commands=['reset_base_tokens'])
def reset_base_tokens(message):
        user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
        tokens = wb_queries.reset_base_tokens(user)
        
        return str(tokens)

# TODO Сделать хелп команду

# TODO Сделать общий абстрактный декоратор

# TODO Перейти на вебхуки

#Начало пулинга
bot.polling(interval=3, none_stop=True)