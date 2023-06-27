import re
from ui_backend.common import universal_reply_markup, reply_markup_trial, reply_markup_payment
from db.queries import db_queries
from cache_worker.cache_worker import cache_worker
from wb_common.wb_queries import wb_queries
from ui_backend.app import bot
from telebot.types import LabeledPrice
from ui_backend.config import *
from yookassa import Payment
import uuid
from ui_backend.config import WEBHOOK_URL

from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)


# Команды бота -------------------------------------------------------------------------------------------------------
@bot.message_handler(commands=['start'])
async def start(message):
    get_user = db_queries.get_user_by_telegram_user_id(telegram_user_id=message.from_user.id)
    if not get_user:
        db_queries.create_user(telegram_user_id=message.from_user.id, telegram_chat_id=message.chat.id, telegram_username=message.from_user.username)
        markup_inline = universal_reply_markup(user_id=message.from_user.id)

        # queue_message_sync(
        #   message
        # )

        await bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}, вы зарегистрировались в *{await bot.get_me().username}*', parse_mode='Markdown', reply_markup=markup_inline)
        await bot.send_message(message.chat.id, f'Так как вы только зарегистрировались, предлагаем Вам *Старт* подписку на нашего бота', parse_mode='Markdown', reply_markup=reply_markup_trial(trial=False))
    else:
        await bot.send_message(message.chat.id, f'Вы уже зарегистрированы')
        
        markup_inline = universal_reply_markup()
        await bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}', reply_markup=markup_inline)


# Обработка Старт подписки ----------------------------------------------------------------------------------------------------
@bot.callback_query_handler(func=lambda x: re.match('Trial', x.data))
async def trial(call):
    if call.data == "Trial_Yes":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Активируем Вам подписку, а пока можете посмотреть что она предоставляет: Информация\nИли /trial - Информация", reply_markup=reply_markup_trial(trial=True))
        db_queries.update_sub(user_id=call.message.chat.id, sub_name='Старт', total=0)
    if call.data == "Trial_No":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f'Хорошо, но если вы всё же захотите активировать подписку, введите команду /trial', parse_mode='Markdown')
    if call.data == "Trial_info":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='`Старт` подписка предоставляет: "Функционал"', parse_mode='Markdown')


# Обработка Оплаты ----------------------------------------------------------------------------------------------------
@bot.callback_query_handler(func=lambda x: re.match('payment', x.data))
async def payment_func(call):
    #Обработка кнопок покупки подписки
    if "telegram" in call.data:
        try:    
            purchase = call.data.split(':')[2]
            if purchase == "subscription":
                sub_name = call.data.split(':')[3]
                sub = db_queries.get_sub_name(sub_name=sub_name)
                product_price = [LabeledPrice(label=sub.title, amount=sub.price * 100)]
                await bot.send_invoice(call.message.chat.id,
                                title=sub.title,
                                description=sub.description,
                                invoice_payload=sub.title,
                                provider_token=PAYMENT_TOKEN,
                                currency='rub',
                                prices=product_price,
                                start_parameter='one-month-sub',
                                is_flexible=False,
                                )
        except Exception as e:
            await bot.send_message(call.message.chat.id, e)
    
    if "site" in call.data:
        try:
            price = 0
            payment_dict = {
                "amount": {
                    "value": price,
                    "currency": "RUB"
                },
                "payment_method_data": {
                    "type": "bank_card"
                },
                "confirmation": {
                "type": "redirect",
                "return_url": f"{WEBHOOK_URL}"
                },
                "capture": True,
                }
            
            idempotence_key = str(uuid.uuid4())
            purchase = call.data.split(':')[2]
            if purchase == "subscription":
                sub_name = call.data.split(":")[3]
                sub = db_queries.get_sub_name(sub_name=sub_name)
                price = sub.price
                payment_dict['amount']['value'] = price
                payment_dict['metadata'] = {
                    'telegram_user_id': f'{call.message.chat.id}',
                    'subscription_name': f'{sub.title}',
                    }
                # product_price = [LabeledPrice(label=sub.title, amount=sub.price * 100)]
                # user = db_queries.get_user_by_telegram_user_id(message.chat.id)
            elif purchase == "requests":
                amount, price = call.data.split(":")[3:]
                
                payment_dict['amount']['value'] = price
                payment_dict['metadata'] = {
                    'telegram_user_id': f'{call.message.chat.id}',
                    'requests_amount': f'{amount}',
                    }
            
            idempotence_key = str(uuid.uuid4())
            
            payment = Payment.create(payment_dict, idempotence_key)
            
            confirmation_url = payment.confirmation.confirmation_url
            await bot.send_message(call.message.chat.id, confirmation_url)
                
        except Exception as e:
            await bot.send_message(call.message.chat.id, e)
            
            
# Показать логи человека -------------------------------------------------------------------------------------
@bot.callback_query_handler(func=lambda x: re.match('logs:', x.data))
async def payment_func(call):
    if "wb_queries" in call.data:
        search_user_id = call.data.split()[3]
        timestamp = call.data.split()[5] + " " + call.data.split()[6]
        await bot.send_message(call.message.chat.id, f'Идет поиск по: {search_user_id}\nВремя: {timestamp}')
        


@bot.message_handler(commands=['trial'])
async def trial(message):
    user = db_queries.get_user_by_telegram_user_id(message.chat.id)
    transaction = db_queries.get_transaction(user_id=user.id, transaction_title="Старт")
    if user.subscriptions_id == None:
        if transaction:
            await bot.send_message(message.chat.id, f'У вас уже была активирована Стартовая подписка', parse_mode='Markdown')
        else:
            await bot.send_message(message.chat.id, f'Информация о Стартовой подписке\nКнопка *Согласиться* активирует Вам подписку', reply_markup=reply_markup_trial(trial=False), parse_mode='Markdown')
    else:    
        sub = db_queries.get_sub(sub_id=user.subscriptions_id)
        if sub.title != 'Старт':
            await bot.send_message(message.chat.id, f'У вас сейчас не Стартовая подписка', parse_mode='Markdown')
        elif sub.title == 'Старт':
            await bot.send_message(message.chat.id, f'Нажмите на `Информация` чтобы узнать, что дает Стартовая подписка', reply_markup=reply_markup_trial(trial=True), parse_mode='Markdown')




@bot.message_handler(regexp='/delete_adv')
async def delete_user_advert(message):
  bot_message_text = message.text
  adv_id = re.sub('/delete_adv_', '', bot_message_text)
  user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
  db_queries.delete_user_advert(user, adv_id)

  deletion_message = f'Компания с id {adv_id} перестала отслеживаться'
  action_message = f'Отслеживание компании'
  db_queries.add_action_history(user_id=user.id, action_description=deletion_message, action=action_message)
  await bot.send_message(message.chat.id, deletion_message)


@bot.message_handler(commands=['buy'])
async def buy_subscription(message):
    try:
        sub_list = db_queries.get_all_sub()
        if PAYMENT_TOKEN.split(':')[1] == 'LIVE':
            for sub in sub_list:
                await bot.send_message(message.chat.id, f'Подписка - {sub.title}\nЦена - {sub.price}\nОписание - {sub.description}\n\nХотите ли вы оплатить через telegram?\nЕсли - Да, нажмите на кнопку `Оплата через телеграм`\nЕсли через сайт, нажмите на кнопку `Оплата через сайт`', reply_markup=reply_markup_payment(purchase="subscription", user_data=f"{sub.title}"))
    except Exception as e:
        await bot.send_message(message.chat.id, e)



@bot.pre_checkout_query_handler(func=lambda query: True)
async def checkout(pre_checkout_query):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                " try to pay again in a few minutes, we need a small rest.")


@bot.message_handler(content_types=['successful_payment'])
async def got_payment(message):
    total = message.successful_payment.total_amount / 100
    await bot.send_message(message.chat.id,
                     'Была подключена подписка: {}\nЕсли хотите узнать подробнее, нажмите - Моя подписка'.format(message.successful_payment.invoice_payload))


    db_queries.update_sub(user_id=message.chat.id, sub_name=message.successful_payment.invoice_payload, total=total)


@bot.message_handler(commands=['show_active_sub'])
async def show_active_sub(message):
    user = db_queries.get_user_by_telegram_user_id(message.chat.id)
    sub = db_queries.get_sub(sub_id=user.subscriptions_id)
    if user.subscriptions_id != None:
        await bot.send_message(message.chat.id, 'Подключен: `{}`\nСрок действия с `{}` по `{}`'.format(sub.title, user.sub_start_date.strftime('%d/%m/%Y'), user.sub_end_date.strftime('%d/%m/%Y')))
    else:
        await bot.send_message(message.chat.id, 'У вас не подключено никаких платных подписок')
        
        
        
@bot.message_handler(commands=['enable_dev_mode'])
async def enabled_dev_mode(message):
    try:
        cache_worker.set_user_dev_mode(user_id=message.from_user.id)
        await bot.send_message(message.chat.id, 'Здравствуйте, Вы включили режим разработчика', reply_markup=universal_reply_markup(user_id=message.from_user.id))
    except Exception as e:
        await bot.send_message(message.chat.id, e)

@bot.message_handler(commands=['disable_dev_mode'])
async def disabled_dev_mode(message):
    try:
        if cache_worker.delete_user_dev_mode(user_id=message.from_user.id):
            await bot.send_message(message.chat.id, 'Вы успешно выключили режим разработчика', reply_markup=universal_reply_markup(user_id=message.from_user.id))
        else:
            await bot.send_message(message.chat.id, 'Произошла ошибка при отключении режима разработчика', reply_markup=universal_reply_markup(user_id=message.from_user.id))
    except Exception as e:
        await bot.send_message(message.chat.id, e)
