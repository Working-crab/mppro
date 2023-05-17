from fastapi import FastAPI
from telebot import types
from fastapi.responses import RedirectResponse

import asyncio
from typing import Union, Dict, Any
from ui_backend.config import bot, WEBHOOK_URL
from db.queries import db_queries
import ui_backend.common as common
import ui_backend.commands as commands
import ui_backend.handlers as handlers
from gpt_common.gpt_queries import gpt_queries


app = FastAPI(openapi_url=None)


@app.on_event('startup')
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL)

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
        if 'subscription_name' in data['object']['metadata']:
            db_queries.update_sub(user_id=data['object']['metadata']['telegram_user_id'], sub_name=data['object']['metadata']['subscription_name'], total=int(float(total)))
            await bot.send_message(data['object']['metadata']['telegram_user_id'], f"Была подключена подписка: {data['object']['metadata']['subscription_name']}\nЕсли хотите узнать подробнее, нажмите - Платные услуги >>> Моя подписка")
        elif 'requests_amount' in data['object']['metadata']:
            db_queries.edit_user_transaction(user_id=data['object']['metadata']['telegram_user_id'], type="Buy", token_amount=data['object']['metadata']['requests_amount'] * 700, request_amount=data['object']['metadata']['requests_amount'])
            await bot.send_message(data['object']['metadata']['telegram_user_id'], f"Было успешно куплено: {data['object']['metadata']['requests_amount']} запросов\nЕсли хотите узнать сколько у вас сейчас запросов нажмите: Платные услуги >>> Мои запросы")
    return 'ok'



# public api

@app.post('/api/v1/search-campaign-depth-of-market')
async def search_campaign_depth_of_market(data: dict):
    data = common.get_search_result_message(data.get('keyword'))
    return { "data": data }

@app.post('/api/v1/gpt-generate-card-description')
async def gpt_generate_card_description(data: dict):
    data = gpt_queries.get_card_description(data.get('keyword'))
    return { "data": data }

  
@app.on_event("shutdown")
def shutdown_event():
  pass