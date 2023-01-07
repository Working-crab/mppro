
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters


BOT_NAME = 'mp_pro_bot'
TOKEN = '5972133433:AAERP_hpf9p-zYjTigzEd-MCpQWGQNCvgWs'


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}, кстати ты знал? Лева - попа.')

async def button_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    button_test = KeyboardButton('test_popa_of_leva')
    keyboard = ReplyKeyboardMarkup([[button_test]])
    await update.message.reply_text('gays', reply_markup=keyboard)

async def show_all_command(update: Update):
    await app.bot.send_message(1009803952, 'Наше сообщение')



app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("showBtn", button_check))
app.add_handler(CommandHandler("start", hello))
app.add_handler(MessageHandler(filters.Regex(r'help'), show_all_command))

# @bot.message_handler(commands=['start']) #создаем команду InlineKeyboardButton
# def start(message):
#     markup = InlineKeyboardMarkup()
#     button1 = InlineKeyboardButton("Сайт Хабр", url='https://habr.com/ru/all/')
#     markup.from_button(button1)
#     app.send_message(message.chat.id, "Привет, {0.first_name}! Нажми на кнопку и перейди на сайт)".format(message.from_user), reply_markup=markup)kup)

app.run_polling()