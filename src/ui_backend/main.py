import telebot
from telebot import types
from fastapi import FastAPI

from typing import Union, Dict, Any
import re

import logging
logger = logging.getLogger(__name__)

from ui_backend.db.queries import db_queries
from wb_common.wb_queries import wb_queries

BOT_NAME = 'mp_pro_bot'
TOKEN = '5972133433:AAERP_hpf9p-zYjTigzEd-MCpQWGQNCvgWs'
WEBHOOK_URL = 'https://admp.pro/'# урл доменя

#Создание бота
bot = telebot.TeleBot(TOKEN)

app = FastAPI(openapi_url=None)

print('mp_pro_ui_telega service started!')

@app.on_event('startup')
def on_startup():
    webhook_info = bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        bot.set_webhook(url=WEBHOOK_URL)

@app.post('/')
async def webhook(update: Dict[str, Any]):
    update = types.Update.de_json(update)
    bot.process_new_updates([update])
    return 'ok'

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
    return f'Здравствуйте, {message}'


@msg_handler(commands=['set_token_cmp'])
def set_token_cmp(message):
    clear_token = message.text.replace('/set_token_cmp ', '').strip()
    db_queries.set_user_wb_cmp_token(telegram_user_id=message.from_user.id, wb_cmp_token=clear_token)
    return 'Ваш токен установлен\!'


@msg_handler(commands=['get_token_cmp'])
def getToken(message):

    token = db_queries.get_user_wb_cmp_token(telegram_user_id=message.from_user.id)
    token = re.sub('_', '\_', token)
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
      4: 'Готова к запуску',
      9: 'Активна',
      8: 'Отказана',
      11: 'Приостановлено',
    }

    view = wb_queries.get_user_atrevds(req_params)
    result_msg = ''

    for product in view:
        date_str = product['startDate']
        
        stat = status_dict.get(product['statusId'], 'Статус не известен')
        if date_str != None:
            date_str = date_str[:10]
            date_str = re.sub('-', '\-', date_str)
        
        # TODO Сделать вывод по страницам через кнопки tg бота и добавить сумму текущей ставки на рекламную компанию
        result_msg += f"*Имя компании: {product['campaignName']}*\n"
        result_msg += f"\t ID Рекламной компании: {product['id']}\n"
        result_msg += f"\t Имя категории: {product['categoryName']}\n"
        result_msg += f"\t Дата начала: {date_str}\n"
        result_msg += f"\t Текущий статус: {stat}\n\n"

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

    campaign_id = re.sub('/add_advert ', '', message_args[0])
    max_budget = re.sub('/add_advert ', '', message_args[1])
    place = re.sub('/add_advert ', '', message_args[2])
    status = re.sub('/add_advert ', '', message_args[3])

    add_result = db_queries.add_user_advert(user, status, campaign_id, max_budget, place)

    if add_result == 'UPDATED':
        return 'Ваша рекламная компания успешно обновлена\!'
    elif add_result == 'ADDED':
        return 'Ваша рекламная компания успешно добавлена\!'

    return 'Произошла ошибка\!'
    


@msg_handler(commands=['delete_advert'])
def delete_advert(message):
    user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
    campaign_id = int(re.sub('/delete_advert ', '', message.text))

    if not campaign_id:
        return 'Необходимо указать ID рекламной компании\!'

    delete_result = db_queries.delete_user_advert(user, campaign_id)

    if not delete_result:
        return f'Компания {campaign_id} не найдена\!'

    return f'Компания {campaign_id} удалена\!'

  
@msg_handler(commands=['my_auto_adverts'])
def my_auto_adverts(message):

    user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
    adverts = db_queries.get_user_adverts(user.id)

    result = ''

    for advert in adverts:
        result += f"{advert.campaign_id} \t Ставка: {advert.max_budget} \t Место: {advert.place} \t Статус: {advert.status}\n"
        result = re.sub('-', '\-', result)
        result = re.sub('_', '\_', result)
        result = re.sub('!', '\!', result)

    if not adverts:
        result = 'Вы ещё не добавили команий\! Используйте add\_advert'
    
    return result



@msg_handler(commands=['reset_base_tokens'])
def reset_base_tokens(message):
        user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
        tokens = wb_queries.reset_base_tokens(user)
        
        return str(tokens)

# TODO Сделать хелп команду

# TODO Сделать логер

# TODO Перейти на вебхуки

#Начало пулинга
# bot.polling(interval=3, none_stop=True)