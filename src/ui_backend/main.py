import telebot
import requests
import re
import json

from src.ui_backend.db.queries import create_user, set_user_wb_cmp_token, get_user_wb_cmp_token

BOT_NAME = 'mp_pro_bot'
TOKEN = '5972133433:AAERP_hpf9p-zYjTigzEd-MCpQWGQNCvgWs'

#Создание бота
bot = telebot.TeleBot(TOKEN)

#Команды бота
@bot.message_handler(commands=['start'])
def start(message):
    create_user(telegram_user_id=message.from_user.id, telegram_chat_id=message.chat.id, telegram_username=message.from_user.username)
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}')


@bot.message_handler(commands=['set_token_cmp'])
def set_token_cmp(message):
    try:
        clear_token = message.text.replace('/set_token_cmp ', '').strip()
        set_user_wb_cmp_token(telegram_user_id=message.from_user.id, wb_cmp_token=clear_token)
        bot.send_message(message.chat.id, f'Ваш токен установлен!')
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {e}')


@bot.message_handler(commands=['get_token_cmp'])
def getToken(message):
    try:
        token = get_user_wb_cmp_token(telegram_user_id=message.from_user.id)
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
    user_cmp_token = get_user_wb_cmp_token(telegram_user_id=message.from_user.id)
    cookies = {'WBToken': user_cmp_token,'x-supplier-id-external': 'f05df88e-0b40-462e-9d55-753712a8a59b'}
    headers={
        'X-User-Id': '61712490', 
        'Referer': 'https://cmp.wildberries.ru/campaigns/list/all',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.5.715 Yowser/2.5 Safari/537.36',
    }

    user_atrevds = requests.get('https://cmp.wildberries.ru/backend/api/v3/atrevds?order=createDate', cookies=cookies, headers=headers)


    # user_atrevds: parse me
    bot.send_message(message.chat.id, json.dumps(user_atrevds.json()['content'][0], indent=4, ensure_ascii=False))

  except Exception as e:
      bot.send_message(message.chat.id, f'Произошла ошибка: {e}')


#Начало пулинга
bot.polling(interval=3, none_stop=True)