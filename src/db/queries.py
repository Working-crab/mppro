
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import Integer, func, select, update, desc, cast
from sqlalchemy.sql.expression import bindparam
from os import environ
import traceback

from .models import GPT_Transaction, Stat_words, User, Advert, Subscription, Transaction, Action_history, User_analitics
from .engine import engine


from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)

statuses = ['default', 'info', 'success', 'failure']
initiators = ['default', 'ui_backend', 'bot_message_sender', 'wb_routines', 'user_automation']

class db_queries:
    
    def create_user(telegram_user_id, telegram_chat_id, telegram_username):
        with Session(engine) as session:
            user = User(
                telegram_user_id = telegram_user_id,
                telegram_chat_id = telegram_chat_id,
                telegram_username = telegram_username,
            )
            session.add(user)
            session.commit()
            
            
    def create_api_user(email, password):
        with Session(engine) as session:
            user = User(
                email = email,
                password = password
            )
            session.add(user)
            session.commit()
            return True


    def add_user_analitcs(user_id, campaign_id, max_bid_company, max_budget_company, current_bet, economy, date_time):
        with Session(engine) as session:
            user_analitics = User_analitics(
                user_id = user_id,
                campaign_id = campaign_id,
                max_bid_company = max_bid_company,
                max_budget_company = max_budget_company,
                current_bet = current_bet,
                economy = economy,
                date_time = date_time
            )
            session.add(user_analitics)
            session.commit()



    def get_user_by_id(user_id):
        with Session(engine) as session:
            return session.query(User).filter(User.id == user_id).first()



    def get_user_by_telegram_user_id(telegram_user_id):
        with Session(engine) as session:
            return session.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        
        
    def get_user_by_email(email):
        with Session(engine) as session:
            return session.query(User).filter(User.email == email).first()


    def set_user_wb_cmp_token(telegram_user_id, wb_cmp_token):
        with Session(engine) as session:
            user = select(User).where(User.telegram_user_id == telegram_user_id)
            user = session.scalars(user).one()
            user.wb_cmp_token = wb_cmp_token
            session.commit()
    
    
    def set_user_wb_v3_main_token(telegram_user_id, wb_v3_main_token):
          with Session(engine) as session:
              user = select(User).where(User.telegram_user_id == telegram_user_id)
              user = session.scalars(user).one()
              user.wb_v3_main_token = wb_v3_main_token
              session.commit()
              
              
    def get_user_wb_cmp_token(telegram_user_id):
        with Session(engine) as session:
            user = select(User).where(User.telegram_user_id == telegram_user_id)
            user = session.scalars(user).one()
            return user.wb_cmp_token
              
    
    def set_user_x_supplier_id(telegram_user_id, x_supplier_id):
          with Session(engine) as session:
              user = select(User).where(User.telegram_user_id == telegram_user_id)
              user = session.scalars(user).one()
              user.x_supplier_id = x_supplier_id
              session.commit()
              
    
    def get_user_x_supplier_id(telegram_user_id):
        with Session(engine) as session:
            user = select(User).where(User.telegram_user_id == telegram_user_id)
            user = session.scalars(user).one()
            return user.x_supplier_id


    def add_user_advert(user,  campaign_id,  max_bid=None, status='ON', place=None):
        with Session(engine) as session:

            advert = session.query(Advert).filter(Advert.user_id == user.id, Advert.campaign_id == int(campaign_id)).first()

            if not advert:
                advert_budget = max_bid
                if advert_budget is None:
                    advert_budget = 0
                    status = 'OFF'

                if place is None:
                    place = 1

                advert = Advert(
                    max_bid = advert_budget, #(int())
                    user_id = user.id,
                    place = place, # maybe string
                    campaign_id = int(campaign_id),
                    status = status
                )
                session.add(advert)
                session.commit()
                return 'ADDED'
            else:
                if max_bid is not None:
                    advert.max_budget = max_bid

                if not max_bid and not advert.max_bid:
                    status = 'OFF'
                
                if place is not None:
                    advert.place = place

                advert.status = status
                session.commit()
                return 'UPDATED'



    def get_user_adverts_by_wb_ids(user_id, wb_ids):
        with Session(engine) as session:
            return session.query(Advert).filter(Advert.user_id == user_id, Advert.campaign_id.in_(wb_ids)).all()


    def delete_user_advert(user, campaign_id):
        with Session(engine) as session:

            advert = session.query(Advert).filter(Advert.user_id == user.id, Advert.campaign_id == int(campaign_id)).first()

            if advert:
                session.delete(advert)
                session.commit()
                return True
            else:
                return False



    def get_user_adverts(user_id):
        with Session(engine) as session:
            return session.query(Advert).filter(Advert.user_id == user_id).all()

   

    def get_adverts_chunk():
        with Session(engine) as session:
            dateNow = datetime.now()

            campaigns = session.query(Advert).order_by(Advert.time_updated).filter(Advert.status == 'ON').limit(100).all() # .filter(Advert.time_updated >= date)

            stmt = update(Advert).\
                where(Advert.id == bindparam('_id')).\
                values({
                    'time_updated': bindparam('time_updated')
                })

            session.execute(stmt, 
                [
                {
                    '_id': campaign.id,
                    'time_updated': dateNow,
                } for campaign in campaigns
                ]
            )

            return campaigns
            

        
    def get_sub(sub_id):
        with Session(engine) as session:
            return session.query(Subscription).filter(Subscription.id == sub_id).first()
            

    def get_sub_name(sub_name):
        with Session(engine) as session:
            return session.query(Subscription).filter(Subscription.title == sub_name).first()
            

       
    def get_all_sub():
        with Session(engine) as session:
            return session.query(Subscription).filter(Subscription.title != 'Старт').order_by(Subscription.price)
        

        
    def update_sub(user_id, sub_name, total):
        with Session(engine) as session:
            user = session.query(User).filter(User.telegram_user_id == user_id).first()
            
            if user:
                sub = session.query(Subscription).filter(Subscription.title == str(sub_name)).first()
                user.sub_start_date = datetime.now()
                user.sub_end_date = datetime.now() + timedelta(days=30)
                user.subscriptions_id = sub.id
                
                transaction = Transaction(
                    title = sub.title,
                    description = f"Была активирована {sub.title} подписка",
                    total = total,
                    user_id = user.id,
                    subscription_id = sub.id,
                )
                
                if sub.requests_get is None:
                    requests_get = 0
                else:
                    requests_get = sub.requests_get
                
                token_transaction = GPT_Transaction(
                    user_id = user.id,
                    type = "Активация подписки",
                    request_amount = requests_get,
                    token_amount = 700 * requests_get
                )
                
                session.add(transaction)
                session.add(token_transaction)
                session.commit()
                return True
            else:
                return False
            
        
    # def sub_list(user_id, sub_name):
    #     with Session(engine) as session:
    #         user = session.query(User).filter(User.telegram_user_id == user_id).first()
    #         sub = session.query(Subscription).filter(Subscription.title == sub_name).first()
            
    #         if user:
    #             sub = session.query(Subscription).filter(Subscription.title == sub_name).first()
    #             user.sub_start_date = datetime.now()
    #             user.sub_end_date = datetime.now() + timedelta(days=30)
    #             user.subscriptions_id = sub.id
    #             session.commit()
    #             return True
    #         else:
    #             return False
            

        
    def get_transaction(user_id, transaction_title):
        with Session(engine) as session:
            return session.query(Transaction).filter(Transaction.user_id == user_id, Transaction.title == transaction_title).first()



    def get_campaign_by_user_id_and_campaign_id(
        user_id, 
        campaign_id
    ):
        with Session(engine) as session:
            return session.query(Advert).filter( 
                (Advert.user_id == user_id) and (Advert.campaign_id == campaign_id) ).first()
        return 'Not_working'
    
    
    def add_action_history(action, action_description, telegram_user_id=None, user_id=None, status=None, initiator=None):

        if not initiator:
            initiator = environ.get('MONITORING_INITIATOR')

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
                status = status if status in statuses else statuses[0],
                initiator = initiator if initiator in initiators else initiators[0],
            )
            session.add(action)
            session.commit()
            return True
            

            
    def show_action_history(user_id, action='date_time', download=False):
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

            
            
    def get_filter_action_history():
        with Session(engine) as session:
            return session.query(Action_history.action.distinct())



    def get_last_actions():
        with Session(engine) as session:
            return session.query(Action_history).order_by(Action_history.id.desc()).limit(3)



    def get_last_errors():
        with Session(engine) as session:
            return session.query(Action_history).where(Action_history.status=='failure').order_by(Action_history.id.desc()).limit(3)
        


    def get_initiator_succsess_count(initiator):
        succsses = {'err': 0, 'all_t': 0}
        with Session(engine) as session:
            succsses['all_t'] = session.query(Action_history).where(Action_history.initiator==initiator).count()
            succsses['err'] = session.query(Action_history).where(Action_history.initiator==initiator and Action_history.status=='failure').count()
        return succsses



    def get_stat_words(campaing_id=None, status=None, types=None):
        with Session(engine) as session:
            if types == "Change":
                return session.query(Stat_words).filter(Stat_words.type == types).filter(Stat_words.status == status).order_by(desc(Stat_words.timestamp)).first()
            if types != None:
                return session.query(Stat_words).filter(Stat_words.campaing_id == campaing_id).filter(Stat_words.type == types).filter(Stat_words.status == status).order_by(Stat_words.timestamp).all()
            if campaing_id != None and status == "Created" and types == None:
                return session.query(Stat_words).filter(Stat_words.campaing_id == campaing_id).filter(Stat_words.status == "Created").first()
    


    def change_status_stat_words(campaing_id=None, status=None, types=None, words=None):
        with Session(engine) as session:
            if types == "Change" and campaing_id != None and status != "Finished":
                get_word = session.query(Stat_words).filter(Stat_words.type == types).filter(Stat_words.campaing_id == campaing_id).first()
                if get_word:
                    get_word.word = words
                    get_word.timestamp = datetime.now()
                    session.commit()
                else:
                    stat_word = Stat_words(
                        status = "Created",
                        campaing_id = campaing_id,
                        word = words,
                        type = types,
                    )
                    session.add(stat_word)
                    session.commit()
                
                return 
            elif types == "Change" and campaing_id != None and status == "Finished":
                get_word = session.query(Stat_words).filter(Stat_words.type == types).filter(Stat_words.campaing_id == campaing_id).first()
                if get_word:
                    get_word.status = status
                    get_word.timestamp = datetime.now()
                    session.commit()
                return
            get_word = session.query(Stat_words).filter(Stat_words.campaing_id == campaing_id).filter(Stat_words.word.in_(words)).all()
            for word in get_word:
                logger.warn(word)
                word.status = "Finished"
            session.commit()


            
    def add_stat_words(types=None, campaing_id=None, word=None):
        with Session(engine) as session:
            stat_word = Stat_words(
                status = "Created",
                campaing_id = campaing_id,
                word = word,
                type = types,
            )
            session.add(stat_word)
            session.commit()
            return True


            
    def delete_stat_words(word=None):
        with Session(engine) as session:
            obj = session.query(Stat_words).filter(Stat_words.word == word).first()
            if obj != None:
                session.delete(obj)
                session.commit()
                return True
            else:
                return False
            
            
    def remove_wb_v3_main_token(user_id):
        with Session(engine) as session:
            user = session.query(User).filter(User.id == user_id).first()
            user.wb_v3_main_token = None
            session.commit()
            
            
    def get_user_tokens(user_id):
        with Session(engine) as session:
            if session.query(GPT_Transaction).filter(GPT_Transaction.user_id == user_id).first() is not None:
                tokens = session.query(func.sum(cast(GPT_Transaction.token_amount, Integer))).filter(GPT_Transaction.user_id == user_id).scalar()
                return tokens
            else:
                return 0
        
        
    def edit_user_transaction(user_id, type, token_amount, request_amount):
        with Session(engine) as session:
            user = session.query(User).filter(User.telegram_user_id == user_id).first()
            
            add_tokens = GPT_Transaction(
                user_id = user.id,
                type = type,
                token_amount = token_amount,
                request_amount = request_amount
            )
            session.add(add_tokens)
            session.commit()
            return True

    def get_user_analitics_data(
    user_id, 
    campaign_id
    ):
        with Session(engine) as session:
            return session.query(User_analitics).filter( 
                (User_analitics.user_id == user_id) and (User_analitics.campaign_id == campaign_id) ).all()
        return 'User_analitcs data doesn`t exist'        
   
        
    def get_user_gpt_requests(user_id):
        with Session(engine) as session:
            if session.query(GPT_Transaction).filter(GPT_Transaction.user_id == user_id).first() is not None:
                gtp_requests = session.query(func.sum(cast(GPT_Transaction.request_amount, Integer))).filter(GPT_Transaction.user_id == user_id).scalar()
                return gtp_requests
            else:
                return 0