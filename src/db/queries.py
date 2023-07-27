
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy.future import  select
from sqlalchemy import Integer, func, update, desc, cast
from sqlalchemy.sql.expression import bindparam
from os import environ
import traceback

from .models import GPT_Transaction, Stat_words, User, Advert, Subscription, Transaction, Action_history, User_analitics
from .engine import engine


from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)

statuses = ['async default', 'info', 'success', 'failure']
initiators = ['async default', 'ui_backend', 'bot_message_sender', 'wb_routines', 'user_automation']

class db_queries:
    
    async def create_user(telegram_user_id, telegram_chat_id, telegram_username):
        async with AsyncSession(engine) as session:
            user = User(
                telegram_user_id = telegram_user_id,
                telegram_chat_id = telegram_chat_id,
                telegram_username = telegram_username,
            )
            session.add(user)
            await session.commit()
            
            
    async def create_api_user(email, password):
        async with AsyncSession(engine) as session:
            user = User(
                email = email,
                password = password
            )
            session.add(user)
            await session.commit()
            return True


    async def add_user_analitcs(user_id, campaign_id, max_bid_company, max_budget_company, current_bet, economy, date_time):
        async with AsyncSession(engine) as session:
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
            await session.commit()


    async def get_user_by_id(user_id):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(User).where(User.id == int(user_id)))
            user = result.scalars().first()
            return user
            

    async def get_user_by_telegram_user_id(telegram_user_id):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(User).where(User.telegram_user_id == int(telegram_user_id)))

            return result.scalars().first()

        
    async def get_user_by_email(email):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(User).where(User.email == email))
            return result.scalars().one()
        

    async def set_user_wb_cmp_token(telegram_user_id, wb_cmp_token):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(User).where(User.telegram_user_id == int(telegram_user_id)))
            # logger.warn("HERE", result)
            user = result.scalars().first()
            
            if user is not None:
                user.wb_cmp_token = wb_cmp_token
                await session.commit()
            else:
                print(f"User with telegram_user_id {telegram_user_id} not found")
    
    
    async def set_user_wb_v3_main_token(telegram_user_id, wb_v3_main_token):
        async with AsyncSession(engine) as session:
            stmt = (
                update(User).
                where(User.telegram_user_id == int(telegram_user_id)).
                values(wb_v3_main_token=wb_v3_main_token)
        )
            await session.execute(stmt)
            await session.commit()
              
              
    async def get_user_wb_cmp_token(telegram_user_id):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(User).where(User.telegram_user_id == int(telegram_user_id)))
            user = (await session.scalars(result)).one()
            return user.wb_cmp_token
              
    
    async def set_user_x_supplier_id(telegram_user_id, x_supplier_id):
          async with AsyncSession(engine) as session:
              result = await session.execute(select(User).where(User.telegram_user_id == int(telegram_user_id)))
              user = result.scalars().first()
              user.x_supplier_id = x_supplier_id
              await session.commit()
              
    
    async def get_user_x_supplier_id(telegram_user_id):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(User).where(User.telegram_user_id == int(telegram_user_id)))
            user = result.scalars().first()
            return user.x_supplier_id
        
        
    async def set_user_public_api_token(telegram_user_id, public_api_token):
          async with AsyncSession(engine) as session:
              result = await session.execute(select(User).where(User.telegram_user_id == int(telegram_user_id)))
              user = result.scalars().one()
              user.public_api_token = public_api_token
              await session.commit()
              
              
    async def get_user_public_api_token(telegram_user_id):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(User).where(User.telegram_user_id == int(telegram_user_id)))
            user = result.scalars().one()
            return user.public_api_token


    async def add_user_advert(user,  campaign_id,  max_bid=None, status='ON', place=None, strategy=None):
        async with AsyncSession(engine) as session:
            
            campaign_id_int = int(campaign_id)
            result = await session.execute(select(Advert).where(Advert.user_id == user.id, Advert.campaign_id == int(campaign_id)))
            
            advert = result.scalars().first()
            
            if not advert:
                advert_budget = max_bid
                if advert_budget is None or advert_budget == '':
                    advert_budget = 0
                    status = 'OFF'

                if place is None:
                    place = 1

                advert = Advert(
                    max_bid = int(advert_budget), #(int())
                    user_id = int(user.id),
                    place = str(place), # maybe string
                    campaign_id = int(campaign_id),
                    status = str(status),
                    strategy = str(strategy),
                )
                session.add(advert)
                await session.commit()
                return 'ADDED'
            else:
                if max_bid is not None:
                    advert.max_budget = int(max_bid)

                if not max_bid and not advert.max_bid:
                    status = 'OFF'
                
                if place is not None:
                    advert.place = str(place)

                if strategy is not None:
                    advert.strategy = strategy

                advert.status = status
                await session.commit()
                return 'UPDATED'


    async def get_user_adverts_by_wb_ids(user_id, wb_ids):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(Advert).where(Advert.user_id == user_id, Advert.campaign_id.in_(wb_ids)))
            return result.scalars().all()


    async def delete_user_advert(user, campaign_id):
        async with AsyncSession(engine) as session:

            result = await session.execute(select(Advert).where(Advert.user_id == user.id, Advert.campaign_id == int(campaign_id)))
            
            advert = result.scalars().one()

            if advert:
                session.delete(advert)
                await session.commit()
                return True
            else:
                return False


    async def get_user_adverts(user_id):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(Advert).where(Advert.user_id == int(user_id)))
            return result.scalars().all()


    async def get_adverts_chunk():
        async with AsyncSession(engine) as session:
            dateNow = datetime.now()

            result = await session.execute(select(Advert).where(Advert.status == 'ON').order_by(Advert.time_updated).limit(100))
            campaigns = result.scalars().all()

            stmt = update(Advert).\
                where(Advert.id == bindparam('_id')).\
                values({
                    'time_updated': bindparam('time_updated')
                })

            await session.execute(stmt, 
                [
                {
                    '_id': campaign.id,
                    'time_updated': dateNow,
                } for campaign in campaigns
                ]
            )

            await session.commit()

            # campaign data is broken here

            for campaign in campaigns:
                await session.refresh(campaign)

            return campaigns
            
        
    async def get_sub(sub_id):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(Subscription).where(Subscription.id == int(sub_id)))
            sub = result.scalars().first()
            return sub
        

    async def get_sub_name(sub_name):
        async with AsyncSession(engine) as session:
            result = await session.execute(Subscription).filter(Subscription.title == sub_name).first()
            return session.scalars(result).first()
            
       
    async def get_all_sub():
        async with AsyncSession(engine) as session:
            result = await session.execute(select(Subscription).where(Subscription.title != 'Старт').order_by(Subscription.price))
            subscriptions = result.scalars().all()
            return subscriptions

        
    async def update_sub(user_id, sub_name, total):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(User).where(User.telegram_user_id == int(user_id)))
            user = result.scalars().first()
            
            if user:
                result = await session.execute(select(Subscription).where(Subscription.title == str(sub_name)))
                sub = result.scalars().first()
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
                await session.commit()
                return True
            else:
                return False
            
        
    # async def sub_list(user_id, sub_name):
    #     async with AsyncSession(engine) as session:
    #         user = session.execute(User).filter(User.telegram_user_id == user_id).first()
    #         sub = session.execute(Subscription).filter(Subscription.title == sub_name).first()
            
    #         if user:
    #             sub = session.execute(Subscription).filter(Subscription.title == sub_name).first()
    #             user.sub_start_date = datetime.now()
    #             user.sub_end_date = datetime.now() + timedelta(days=30)
    #             user.subscriptions_id = sub.id
    #             await session.commit()
    #             return True
    #         else:
    #             return False
            

        
    async def get_transaction(user_id, transaction_title):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(Transaction).where(Transaction.user_id == user_id, Transaction.title == transaction_title))
            return session.scalars(result).one()


    async def get_campaign_by_user_id_and_campaign_id(
        user_id, 
        campaign_id
    ):
        async with AsyncSession(engine) as session:
            result = session.execute(select(Advert).where( 
                (Advert.user_id == int(user_id)) and (Advert.campaign_id == int(campaign_id)) ))
            return session.scalars(result).one()
            
        return 'Not_working'
    
    
    async def add_action_history(action, action_description, telegram_user_id=None, user_id=None, status=None, initiator=None):
        if not initiator:
            initiator = environ.get('MONITORING_INITIATOR')

        async with AsyncSession(engine) as session:

            if not user_id and not telegram_user_id:
                return False

            execute_user_id = None

            if telegram_user_id is not None:
                result = await session.execute(select(User).where(User.telegram_user_id == int(telegram_user_id)))
                try:
                    user = result.scalars().one()
                except NoResultFound:
                    user = None
                
                if user:
                    execute_user_id = user.id
            else:
                execute_user_id = user_id

            if not execute_user_id:
                return False
            
            action = Action_history(
                user_id = execute_user_id,
                description = action_description,
                action = action,
                status = status if status in statuses else statuses[0],
                initiator = initiator if initiator in initiators else initiators[0],
            )
            session.add(action)
            await session.commit()
            return True

            
    async def show_action_history(user_id, action='date_time', download=False):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(User).where(User.telegram_user_id == user_id))
            user = result.scalars().first()
            
            if download:
                result = await session.execute(select(Action_history).where(Action_history.user_id == user.id).order_by(desc(Action_history.date_time)))
                return result.scalars().all()
            else:
                result = await session.execute(select(Action_history).where(Action_history.user_id == user.id).order_by(desc(Action_history.date_time)).limit(20))
                return result.scalars().all()
            # else:
            #     if download:
            #         result = await session.execute(select(Action_history).where(Action_history.user_id == user.id).filter(Action_history.action == action).order_by(desc(Action_history.date_time)))
            #         return result.scalars().all()
            #     else:
            #         result = await session.execute(select(Action_history).filter(Action_history.user_id == user.id).filter(Action_history.action == action).order_by(desc(Action_history.date_time)).limit(20))
            #         return result.scalars().all()
            
            
    async def get_filter_action_history():
        async with AsyncSession(engine) as session:
            result = await session.execute(select(Action_history.action.distinct()))
            return result.scalars().all()


    async def get_action_history_last_actions():
        async with AsyncSession(engine) as session:
            result = await session.execute(select(Action_history).order_by(Action_history.id.desc()).limit(3))
            return result.scalars().all()


    async def get_action_history_last_errors():
        async with AsyncSession(engine) as session:
            result = await session.execute(select(Action_history).where(Action_history.status=='failure').order_by(Action_history.id.desc()).limit(5))
            return result.scalars().all()
        

    async def get_action_history_initiator_succsess_count(initiator):
        succsses = {'err': 0, 'all_t': 0}
        async with AsyncSession(engine) as session:
            result1 = await session.execute(select(func.count(Action_history.id)).where(Action_history.initiator==initiator))
            succsses['all_t'] = result1.scalars().first()

            result2 = await session.execute(select(func.count(Action_history.id)).where(Action_history.initiator==initiator, Action_history.status=='failure'))
            succsses['err'] = result2.scalars().first()

        return succsses


    async def get_stat_words(campaing_id=None, status=None, types=None):
        async with AsyncSession(engine) as session:
            if types == "Change":
                result = await session.execute(select(Stat_words).where(Stat_words.type == types).where(Stat_words.status == status).order_by(desc(Stat_words.timestamp)))
                return session.scalars(result).first()
            if types != None:
                result = await session.execute(select(Stat_words).where(Stat_words.campaing_id == int(campaing_id)).where(Stat_words.type == types).where(Stat_words.status == status).order_by(Stat_words.timestamp))
                return session.scalars(result).all()
            
            if campaing_id != None and status == "Created" and types == None:
                result = await session.execute(select(Stat_words).where(Stat_words.campaing_id == int(campaing_id)).where(Stat_words.status == "Created"))
                return session.scalars(result).first()
    

    async def change_status_stat_words(campaing_id=None, status=None, types=None, words=None):
        async with AsyncSession(engine) as session:
            if types == "Change" and campaing_id != None and status != "Finished":
                get_word = session.execute(Stat_words).filter(Stat_words.type == types).filter(Stat_words.campaing_id == int(campaing_id)).first()
                if get_word:
                    get_word.word = words
                    get_word.timestamp = datetime.now()
                    await session.commit()
                else:
                    stat_word = Stat_words(
                        status = "Created",
                        campaing_id = int(campaing_id),
                        word = words,
                        type = types,
                    )
                    session.add(stat_word)
                    await session.commit()
                
                return 
            elif types == "Change" and campaing_id != None and status == "Finished":
                get_word = session.execute(Stat_words).filter(Stat_words.type == types).filter(Stat_words.campaing_id == int(campaing_id)).first()
                if get_word:
                    get_word.status = status
                    get_word.timestamp = datetime.now()
                    await session.commit()
                return
            get_word = session.execute(Stat_words).filter(Stat_words.campaing_id == int(campaing_id)).filter(Stat_words.word.in_(words)).all()
            for word in get_word:
                logger.warn(word)
                word.status = "Finished"
            await session.commit()

            
    async def add_stat_words(types=None, campaing_id=None, word=None):
        async with AsyncSession(engine) as session:
            stat_word = Stat_words(
                status = "Created",
                campaing_id = campaing_id,
                word = word,
                type = types,
            )
            session.add(stat_word)
            await session.commit()
            return True

            
    async def delete_stat_words(word=None):
        async with AsyncSession(engine) as session:
            obj = session.execute(select(Stat_words).where(Stat_words.word == word))
            obj = session.scalars(obj).one()
            if obj != None:
                session.delete(obj)
                await session.commit()
                return True
            else:
                return False
            
            
    async def remove_wb_v3_main_token(user_id):
        async with AsyncSession(engine) as session:
            user = await session.execute(select(User).where(User.id == int(user_id)))
            user = session.scalars(user).one()
            user.wb_v3_main_token = None
            await session.commit()
            
            
    async def get_user_tokens(user_id):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(GPT_Transaction).where(GPT_Transaction.user_id == int(user_id)))
            transactions = result.scalars().all()

            if transactions:
                result = await session.execute(select(func.sum(cast(GPT_Transaction.token_amount, Integer))).where(GPT_Transaction.user_id == int(user_id)))
                tokens = result.scalar_one()
                return tokens
            else:
                return 0
        
        
    async def edit_user_transaction(user_id, type, token_amount, request_amount):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(User).where(User.telegram_user_id == int(user_id)))
            user = result.scalars().one()
            
            add_tokens = GPT_Transaction(
                user_id = user.id,
                type = type,
                token_amount = token_amount,
                request_amount = request_amount
            )
            session.add(add_tokens)
            await session.commit()
            return True


    async def get_user_analitics_data(
    user_id, 
    campaign_id
    ):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(User_analitics).where( 
                (User_analitics.user_id == user_id) and (User_analitics.campaign_id == int(campaign_id))))
            return result.scalars().all()
            
        return 'User_analitcs data doesn`t exist'        
   
        
    async def get_user_gpt_requests(user_id):
        async with AsyncSession(engine) as session:
            result = await session.execute(select(GPT_Transaction).where(GPT_Transaction.user_id == int(user_id)))
            transactions = result.scalars().all()

            if transactions:
                result = await session.execute(select(func.sum(cast(GPT_Transaction.request_amount, Integer))).where(GPT_Transaction.user_id == int(user_id)))
                gtp_requests = result.scalar_one()
                return gtp_requests
            else:
                return 0