import telebot
import requests
import re

from src.ui_backend.db.queries import create_user, set_user_wb_cmp_token, get_user_wb_cmp_token

BOT_NAME = 'mp_pro_bot'
TOKEN = '5972133433:AAERP_hpf9p-zYjTigzEd-MCpQWGQNCvgWs'

#Создание бота
bot = telebot.TeleBot(TOKEN)

#Команды бота
@bot.message_handler(commands=['start'])
def start(message):
    create_user(telegram_user_id=message.from_user.id, telegram_chat_id=message.chat.id, telegram_username=message.from_user.username)
    bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}')


@bot.message_handler(commands=['set_token_cmp'])
def addToken(message):
    try:
        set_user_wb_cmp_token(telegram_user_id=message.from_user.id, wb_main_token=message.text.replace('/addToken', '').strip())
        bot.send_message(message.chat.id, f'Ваш токе был отправлен {message.from_user.first_name}')
    except Exception as e:
        bot.send_message(f'Произошла ошибка: {e}')


@bot.message_handler(commands=['get_token_cmp'])
def getToken(message):
    try:
        token = get_user_wb_cmp_token(telegram_user_id=message.from_user.id)
        bot.send_message(message.chat.id, f'Ваш токе был получен, Токен: {token}')
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




#Начало пулинга
bot.polling(interval=3, none_stop=True)