import telebot
from telebot.async_telebot import AsyncTeleBot
from yookassa import Configuration
import os
from common.appLogger import appLogger
# import locale

# logger.warn("LOCALE")
# locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")

if os.path.isfile('src/ui_backend/config_local.py'):
    from ui_backend import config_local
    TOKEN = config_local.TOKEN
    BOT_NAME = config_local.BOT_NAME
    PAYMENT_TOKEN = config_local.PAYMENT_TOKEN
    Configuration.account_id = config_local.yookassa_account_id
    Configuration.secret_key = config_local.yookassa_secret_key
    WEBHOOK_URL = config_local.WEBHOOK_URL
    GPT_TOKEN = config_local.GPT_TOKEN
    GPT_MODEL_NAME = config_local.GPT_MODEL_NAME
else:
    from ui_backend import config_template
    TOKEN = config_template.TOKEN
    BOT_NAME = config_template.BOT_NAME
    PAYMENT_TOKEN = config_template.PAYMENT_TOKEN
    Configuration.account_id = config_template.yookassa_account_id
    Configuration.secret_key = config_template.yookassa_secret_key
    WEBHOOK_URL = config_template.WEBHOOK_URL
    GPT_TOKEN = config_template.GPT_TOKEN
    GPT_MODEL_NAME = config_template.GPT_MODEL_NAME
    
    
bot = AsyncTeleBot(TOKEN)
syncBot = telebot.TeleBot(TOKEN)
