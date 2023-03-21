from fastapi import FastAPI
from telebot import types
from fastapi.responses import RedirectResponse

import asyncio
from typing import Union, Dict, Any
from .bot import bot
from db.queries import db_queries
import ui_backend.common
import ui_backend.commands
import ui_backend.handlers

from ui_backend.message_queue import main as message_queue
from ui_backend.mq_campaign_info import main as mq_campaign_info


app = FastAPI(openapi_url=None)
WEBHOOK_URL = 'https://admp.pro/'# урл домена


@app.on_event('startup')
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL)
    asyncio.create_task(message_queue(asyncio.get_event_loop()))
    asyncio.create_task(mq_campaign_info(asyncio.get_event_loop()))

@app.post('/')
async def webhook(update: Dict[str, Any]):
    update = types.Update.de_json(update)
    await bot.process_new_updates([update])
    return 'ok'

@app.get('/')
async def telegram_bot_redirect():
    return RedirectResponse(url='https://t.me/mp_pro_bot')


@app.post("/payment")
async def webhook(data: dict):
    # process the incoming data
    if data['object']['status'] == "succeeded":
        total = data['object']['amount']['value']
        db_queries.update_sub(user_id=data['object']['metadata']['telegram_user_id'], sub_name=data['object']['metadata']['subscription_name'], total=int(float(total)))
        await bot.send_message(data['object']['metadata']['telegram_user_id'], f"Была подключена подписка: {data['object']['metadata']['subscription_name']}\nЕсли хотите узнать подробнее, нажмите - Моя подписка")
    return 'ok'

  
@app.on_event("shutdown")
def shutdown_event():
  pass
  # if message_queue_connection:
  #   message_queue_connection.close()