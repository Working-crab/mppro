
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy import desc
import traceback

from .models import User, Advert, Subscription, Transaction, Action_history
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



    def add_user_advert(user,  campaign_id,  max_budget, status='ON', place=1):
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
            traceback.print_exc()
            err_msg = f'Запрос не выполнен по причине: TypeError: {type(e).__name__}: {e}.'
            print(err_msg)
            raise ValueError(err_msg)



    def get_user_adverts_by_wb_ids(user_id, wb_ids):
        try:
            with Session(engine) as session:
                adverts_from_db = session.query(Advert).filter(Advert.user_id == user_id, Advert.campaign_id.in_(wb_ids)).all()
                return adverts_from_db
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
                return session.query(Advert).order_by(Advert.time_updated).limit(100).all() # .filter(Advert.time_updated >= date)
        except Exception as e:
            print(f'Запрос не выполнен по причине: TypeError: {type(e).__name__}: {e}.')
            

        
    def get_sub(sub_id):
        try:
            with Session(engine) as session:
                return session.query(Subscription).filter(Subscription.id == sub_id).first()
        except Exception as e:
            print(f'Запрос не выполнени по причине: TypeError: {type(e).__name__}: {e}.')
            

    def get_sub_name(sub_name):
            try:
                with Session(engine) as session:
                    return session.query(Subscription).filter(Subscription.title == sub_name).first()
            except Exception as e:
                print(f'Запрос не выполнени по причине: TypeError: {type(e).__name__}: {e}.')
            

       
    def get_all_sub():
        try:
            with Session(engine) as session:
                return session.query(Subscription).filter(Subscription.title != 'Trial')
        except Exception as e:
            print(f'Запрос не выполнени по причине: TypeError: {type(e).__name__}: {e}.')
            

        
    def update_sub(user_id, sub_name, total):
        try:
            with Session(engine) as session:
                user = session.query(User).filter(User.telegram_user_id == user_id).first()
                sub = session.query(Subscription).filter(Subscription.title == sub_name).first()
                user.sub_start_date = datetime.now()
                user.sub_end_date = datetime.now() + timedelta(days=30)
                
                if user:
                    sub = session.query(Subscription).filter(Subscription.title == sub_name).first()
                    user.sub_start_date = datetime.now()
                    user.sub_end_date = datetime.now() + timedelta(days=30)
                    user.subscriptions_id = sub.id
                    
                    transaction = Transaction(
                        title = sub.title,
                        description = "Была активирована подписка",
                        total = total,
                        user_id = user.id,
                        subscription_id = sub.id,
                    )
                    session.add(transaction)
                    session.commit()
                    return True
                else:
                    return False
                # user.subscriptions_id = sub.id
        except Exception as e:
            print(f'Запрос не выполнени по причине: TypeError: {type(e).__name__}: {e}.')
            

        
    def set_trial(user_id, sub_name):
        try:
            with Session(engine) as session:
                user = session.query(User).filter(User.telegram_user_id == user_id).first()
                sub = session.query(Subscription).filter(Subscription.title == sub_name).first()
                
                if user:
                    sub = session.query(Subscription).filter(Subscription.title == sub_name).first()
                    user.sub_start_date = datetime.now()
                    user.sub_end_date = datetime.now() + timedelta(days=7)
                    user.subscriptions_id = sub.id
                    
                    transaction = Transaction(
                        title = "Trial",
                        description = "Была активирована Пробная подписка",
                        total = 0,
                        user_id = user.id,
                        subscription_id = sub.id,
                    )
                    session.add(transaction)
                    session.commit()
                    return True
                else:
                    return False
                # user.subscriptions_id = sub.id
        except Exception as e:
            print(f'Запрос не выполнени по причине: TypeError: {type(e).__name__}: {e}.')
            

        
    def sub_list(user_id, sub_name):
        try:
            with Session(engine) as session:
                user = session.query(User).filter(User.telegram_user_id == user_id).first()
                sub = session.query(Subscription).filter(Subscription.title == sub_name).first()
                
                if user:
                    sub = session.query(Subscription).filter(Subscription.title == sub_name).first()
                    user.sub_start_date = datetime.now()
                    user.sub_end_date = datetime.now() + timedelta(days=30)
                    user.subscriptions_id = sub.id
                    session.commit()
                    return True
                else:
                    return False
                # user.subscriptions_id = sub.id
        except Exception as e:
            print(f'Запрос не выполнени по причине: TypeError: {type(e).__name__}: {e}.')
            

        
    def get_transaction(user_id, transaction_title):
        try:
            with Session(engine) as session:
                return session.query(Transaction).filter(Transaction.user_id == user_id, Transaction.title == transaction_title).first()
        except Exception as e:
            print(f'Запрос не выполнени по причине: TypeError: {type(e).__name__}: {e}.')
    


    def get_campaign_by_user_id_and_campaign_id(
        user_id, 
        campaign_id
    ):
        try:
            with Session(engine) as session:
                return session.query(Advert).filter( 
                    (Advert.user_id == user_id) and (Advert.campaign_id == campaign_id) ).first()
        except Exception as e:
            print(f'Запрос не выполнени по причине: TypeError: {type(e).__name__}: {e}.')

        return 'JOPA'
    
    
    def add_action_history(action, action_description, telegram_user_id=None, user_id=None):
        try:
            with Session(engine) as session:

                if not user_id and not telegram_user_id:
                    return False

                query_user_id = None

                if telegram_user_id != None:
                    user = session.query(User).filter(User.telegram_user_id == telegram_user_id).first()
                    if user:
                        query_user_id = user.id
                else:
                    query_user_id = user_id

                if not query_user_id:
                    return False
                
                action = Action_history(
                    user_id = query_user_id,
                    description = action_description,
                    action = action,
                )
                session.add(action)
                session.commit()
                return True
            
        except Exception as e:
            print(f'Запрос не выполнени по причине: TypeError: {type(e).__name__}: {e}.')
            
            
    def show_action_history(user_id, action='date_time', download=False):
        try:
            with Session(engine) as session:
                user = session.query(User).filter(User.telegram_user_id == user_id).first()
                if action == 'date_time':
                    if download:
                        return session.query(Action_history).filter(Action_history.user_id == user.id).order_by(desc(Action_history.date_time))
                    else:
                        return session.query(Action_history).filter(Action_history.user_id == user.id).order_by(desc(Action_history.date_time)).limit(20)
                else:
                    if download:
                        return session.query(Action_history).filter(Action_history.user_id == user.id).filter(Action_history.action == action).order_by(desc(Action_history.date_time))
                    else:
                        return session.query(Action_history).filter(Action_history.user_id == user.id).filter(Action_history.action == action).order_by(desc(Action_history.date_time)).limit(20)
        except Exception as e:
            print(f'Запрос не выполнени по причине: TypeError: {type(e).__name__}: {e}.')
            
            
    def get_filter_action_history():
        try:
            with Session(engine) as session:
                return session.query(Action_history.action.distinct())
        except Exception as e:
            print(f'Запрос не выполнени по причине: TypeError: {type(e).__name__}: {e}.')