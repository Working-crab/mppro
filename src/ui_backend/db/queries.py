from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import User
from .engine import engine


def create_user(telegram_user_id, telegram_chat_id, telegram_username):

    try:
        with Session(engine) as session:
            user = User(
                telegram_user_id = telegram_user_id,
                telegram_chat_id = telegram_chat_id,
                telegram_username = telegram_username,
            )
            session.add(user)
            session.commit()
    except Exception as e:
        print(f'Запрос не выполнени по причине: TypeError: {type(e).__name__}: {e}.')

def add_wb_token(telegram_user_id, wb_main_token):

    try:
        with Session(engine) as session:
            user = select(User).where(User.telegram_user_id == telegram_user_id)
            user = session.scalars(user).one()
            user.wb_main_token = wb_main_token
            session.commit()
    except Exception as e:
        print(f'Запрос не выполнен по причине: TypeError: {type(e).__name__}: {e}.')

def get_user_wb_token(telegram_user_id):

    try:
        with Session(engine) as session:
            user = select(User).where(User.telegram_user_id == telegram_user_id)
            user = session.scalars(user).one()
            return user.wb_main_token
    except Exception as e:
        print(f'Запрос не выполнен по причине: TypeError: {type(e).__name__}: {e}.')

def set_user_wb_cmp_token(telegram_user_id, wb_cmp_token):

    try:
        with Session(engine) as session:
            user = select(User).where(User.telegram_user_id == telegram_user_id)
            user = session.scalars(user).one()
            user.wb_cmp_token = wb_cmp_token
            session.commit()
    except Exception as e:
        print(f'Запрос не выполнен по причине: TypeError: {type(e).__name__}: {e}.')

def get_user_wb_cmp_token(telegram_user_id):

    try:
        with Session(engine) as session:
            user = select(User).where(User.telegram_user_id == telegram_user_id)
            user = session.scalars(user).one()
            return user.wb_cmp_token
    except Exception as e:
        print(f'Запрос не выполнен по причине: TypeError: {type(e).__name__}: {e}.')