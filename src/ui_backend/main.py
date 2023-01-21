
import telebot
import requests
import re

from src.ui_backend.db.queries import db_queries
from src.wb_common.wb_queries import wb_queries

BOT_NAME = 'mp_pro_bot'
TOKEN = '5972133433:AAERP_hpf9p-zYjTigzEd-MCpQWGQNCvgWs'

#Создание бота
bot = telebot.TeleBot(TOKEN)

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
        query = re.sub('/search ', '', message.text)
        r2 = requests.get(f'https://catalog-ads.wildberries.ru/api/v5/search?keyword={query}')
        item_dicts = r2.json()['adverts']
        item_dicts = sorted(item_dicts, key=lambda dict_item: dict_item.get('cpm'), reverse=True)[0:10]
        result_message = ''

        if len(item_dicts) == 0:
            return bot.send_message(message.chat.id, 'ставки неизвестны')
        else:
            for item_idex in range(len(item_dicts)):
                price = item_dicts[item_idex]['cpm']
                p_id = item_dicts[item_idex]['id']
                result_message += f'{item_idex + 1})  {price}р,  https://www.wildberries.ru/catalog/{p_id}/detail.aspx \n'
            bot.send_message(message.chat.id, result_message)

    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {e}')


@bot.message_handler(commands=['list_atrevds'])
def list_atrevds(message):
  try:
    user_cmp_token = db_queries.get_user_wb_cmp_token(telegram_user_id=message.from_user.id)

    cookies = {
      'WBToken': user_cmp_token,
      'x-supplier-id-external': 'f05df88e-0b40-462e-9d55-753712a8a59b'
    }

    headers = {
      'X-User-Id': '61712490',
      'Referer': 'https://cmp.wildberries.ru/campaigns/list/all',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.5.715 Yowser/2.5 Safari/537.36',
    }

    status_dict = {
      '4': 'Готова к запуску',
      '11': 'Приостановлено',
      '9': 'Активна',
    }

    user_atrevds = requests.get('https://cmp.wildberries.ru/backend/api/v3/atrevds?order=createDate', cookies=cookies, headers=headers)
    view = user_atrevds.json()['content']
    result_msg = ''

    for product in view:
        date_str = product['startDate']
        
        stat = status_dict[str(product['statusId'])]
        if date_str != None:
            date_str = date_str[:10]
        
        result_msg += f"{product['categoryName']}  {product['campaignName']}  {product['campaignId']}  {date_str} {stat}\n"
    

    # user_atrevds: parse me
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
        compagin_id = re.sub('/add_advert ', 'ЖОПА', message.text)
        max_budget = re.sub('/add_advert ', '', message.text)
        place = re.sub('/add_advert ', '', message.text)

        advert = db_queries.add_user_advert(user, compagin_id, max_budget, place)
        bot.send_message(message.chat.id, advert)
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {e}')

  
@bot.message_handler(commands=['get_adverts'])
def get_adverts(message):
    try:
        user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
        adverts = db_queries.get_user_adverts(user.id)
        
        bot.send_message(message.chat.id, adverts)
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


#Начало пулинга
bot.polling(interval=3, none_stop=True)