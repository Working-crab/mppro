
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select

from .models import User, Advert
from .engine import engine


class db_queries:

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



  def get_user_by_id(user_id):

      try:
          with Session(engine) as session:
              return session.query(User).filter(User.id == user_id).first()
      except Exception as e:
          print(f'Запрос не выполнени по причине: TypeError: {type(e).__name__}: {e}.')



  def get_user_by_telegram_user_id(telegram_user_id):

      try:
          with Session(engine) as session:
              return session.query(User).filter(User.telegram_user_id == telegram_user_id).first()
      except Exception as e:
          print(f'Запрос не выполнени по причине: TypeError: {type(e).__name__}: {e}.')



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


  def add_user_advert(user, status, campaign_id, max_budget, place):

      try:
          with Session(engine) as session:

              advert = session.query(Advert).filter(Advert.user_id == user.id, Advert.campaign_id == int(campaign_id)).first()

              if not advert:
                  advert = Advert(
                      max_budget = max_budget, #(int())
                      user_id = user.id,
                      place = place, # maybe string
                      campaign_id = int(campaign_id),
                      status = status
                  )
                  session.add(advert)
                  session.commit()
                  return 'ADDED'
              
              else:
                  advert.max_budget = max_budget
                  advert.place = place
                  advert.status = status
                  session.commit()
                  return 'UPDATED'
              
      except Exception as e:
          err_msg = f'Запрос не выполнен по причине: TypeError: {type(e).__name__}: {e}.'
          print(err_msg)
          raise ValueError(err_msg)



  def delete_user_advert(user, campaign_id):

      try:
          with Session(engine) as session:

              advert = session.query(Advert).filter(Advert.user_id == user.id, Advert.campaign_id == int(campaign_id)).first()

              if advert:
                  session.delete(advert)
                  session.commit()
                  return True
              else:
                  return False
              
      except Exception as e:
          err_msg = f'Запрос не выполнен по причине: TypeError: {type(e).__name__}: {e}.'
          print(err_msg)
          raise ValueError(err_msg)



  def get_user_adverts(user_id):

      try:
          with Session(engine) as session:
            return session.query(Advert).filter(Advert.user_id == user_id).all()

      except Exception as e:
          print(f'Запрос не выполнен по причине: TypeError: {type(e).__name__}: {e}.')


      
  def get_adverts_chunk():

      try:
          with Session(engine) as session:
            date = datetime.now() - timedelta(days=1)
            print(date)
            return session.query(Advert).filter(Advert.time_updated >= date).order_by(Advert.time_updated).limit(100).all()

      except Exception as e:
          print(f'Запрос не выполнен по причине: TypeError: {type(e).__name__}: {e}.')