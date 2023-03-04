import telebot
from telebot.async_telebot import AsyncTeleBot
from yookassa import Configuration

# Configuration.account_id = 980339 #Тест версия
# Configuration.secret_key = 'test_Ue2xPoNd6OaYiH2jogyGl1H0PenP_xB993f3nqTyxj4' #Тест версия

Configuration.account_id = 978902 #Боевой
Configuration.secret_key = 'live_l0GbasWj_Beak-mP0iScmjYPCEUuUtua6FpyyGlM6zQ' #Боевой

BOT_NAME = 'mp_pro_bot'
TOKEN = '5972133433:AAERP_hpf9p-zYjTigzEd-MCpQWGQNCvgWs'
PAYMENT_TOKEN = '390540012:LIVE:30668' #Боевой
# PAYMENT_TOKEN = '381764678:TEST:49601' #Тест
bot = AsyncTeleBot(TOKEN)
syncBot = telebot.TeleBot(TOKEN)
