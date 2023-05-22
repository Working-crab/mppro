from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

from telebot import types
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer

import asyncio
from typing import Union, Dict, Any
from ui_backend.config import bot, WEBHOOK_URL
from db.queries import db_queries
import ui_backend.common as common
import ui_backend.commands as commands
import ui_backend.handlers as handlers
from gpt_common.gpt_queries import gpt_queries

from ui_backend.auth import authenticate_user, UserIn, pwd_context, create_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

app = FastAPI() # openapi_url=None fix on the end TODO

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
            db_queries.edit_user_transaction(user_id=data['object']['metadata']['telegram_user_id'], type="Buy", token_amount=int(data['object']['metadata']['requests_amount']) * 700, request_amount=int(data['object']['metadata']['requests_amount']))
            await bot.send_message(data['object']['metadata']['telegram_user_id'], f"Было успешно куплено: {data['object']['metadata']['requests_amount']} запросов\nЕсли хотите узнать сколько у вас сейчас запросов нажмите: Платные услуги >>> Мои запросы")
    return 'ok'


# public api

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/api/v1/login", response_model=Token)
async def login_for_access_token(email: str, password: str):
    db_user = db_queries.get_user_by_email(email)
    if db_user == None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not registered",
        )
        
    user = authenticate_user(db_user, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/v1/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserIn):
    try:
        if db_queries.get_user_by_email(user.email) != None:
            raise HTTPException(status_code=400, detail="Email is taken")
        hashed_password = pwd_context.hash(user.password)
        user = db_queries.create_api_user(email=user.email, password=hashed_password)
        return True
    except:
        return False

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