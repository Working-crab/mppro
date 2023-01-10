import telebot
from src.ui_backend.db.queries import create_user, add_wb_token


BOT_NAME = 'mp_pro_bot'
TOKEN = '5972133433:AAERP_hpf9p-zYjTigzEd-MCpQWGQNCvgWs'

#Создание бота
bot = telebot.TeleBot(TOKEN)

#Методы бота
@bot.message_handler(commands=['start'])
def start(message):
    create_user(telegram_user_id=message.from_user.id, telegram_chat_id=message.chat.id, telegram_username=message.from_user.username)
    bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}')

@bot.message_handler(commands=['addToken'])
def addToken(message):
    try:
        add_wb_token(telegram_user_id=message.from_user.id, wb_main_token=message.text.replace('/addToken', '').strip())
        bot.send_message(message.chat.id, f'Ваш токе был отправлен {message.from_user.first_name}')
    except Exception as e:
        bot.send_message(f'Произошла ошибка: {e}')


#Начало пулинга
bot.polling(interval=3, none_stop=True)