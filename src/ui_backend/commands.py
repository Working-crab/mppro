import re
from ui_backend.common import msg_handler, universal_reply_markup, reply_markup_trial, reply_markup_payment, status_parser
from db.queries import db_queries
from wb_common.wb_queries import wb_queries
from ui_backend.app import bot
from telebot.types import LabeledPrice
from ui_backend.bot import *
from yookassa import Payment
import uuid


# PAYMENT_TOKEN = '390540012:LIVE:30668'


@msg_handler(commands=['get_token_cmp'])
def getToken(message):

  token = db_queries.get_user_wb_cmp_token(telegram_user_id=message.from_user.id)
  token = re.sub('_', '\_', token)
  token = re.sub('-', '\-', token)
  return token

# Команды бота -------------------------------------------------------------------------------------------------------
@bot.message_handler(commands=['start'])
def start(message):
    get_user = db_queries.get_user_by_telegram_user_id(telegram_user_id=message.from_user.id)
    if not get_user:
        db_queries.create_user(telegram_user_id=message.from_user.id, telegram_chat_id=message.chat.id, telegram_username=message.from_user.username)
        markup_inline = universal_reply_markup()
        bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}, вы зарегистрировались в *{bot.get_me().username}*', parse_mode='Markdown', reply_markup=markup_inline)
        bot.send_message(message.chat.id, f'Так как вы только зарегистрировались, предлагаем Вам *Trial* подписку на нашего бота', parse_mode='Markdown', reply_markup=reply_markup_trial(trial=False))
    else:
        bot.send_message(message.chat.id, f'Вы уже зарегистрированы')
        markup_inline = universal_reply_markup()
        bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}', reply_markup=markup_inline)

        

@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
    if call.data == "Trial_Yes":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Активируем Вам подписку, а пока можете посмотреть что она предоставляет: Информация\nИли /trial - Информация", reply_markup=reply_markup_trial(trial=True))
        db_queries.set_trial(user_id=call.message.chat.id, sub_name='Trial')
    if call.data == "Trial_No":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f'Хорошо, но если вы всё же захотите активировать подписку, введите команду /trial', parse_mode='Markdown')
    if call.data == "Trial_info":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='`Trial` подписка предоставляет: "Функционал"', parse_mode='Markdown')
    
    
    #Обработка кнопок покупки подписки
    if "Telegram" in call.data:
        try:    
            sub_name = call.data.replace('Telegram ', '')
            sub = db_queries.get_sub_name(sub_name=sub_name)
            product_price = [LabeledPrice(label=sub.title, amount=sub.price * 100)]
            bot.send_invoice(call.message.chat.id,
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
            bot.send_message(call.message.chat.id, e)
    
    if "Сайт" in call.data:
        try:
            sub_name = call.data.replace('Сайт ', '')
            sub = db_queries.get_sub_name(sub_name=sub_name)
            # product_price = [LabeledPrice(label=sub.title, amount=sub.price * 100)]
            # user = db_queries.get_user_by_telegram_user_id(message.chat.id)
            
            idempotence_key = str(uuid.uuid4())
            payment = Payment.create({
                "amount": {
                    "value": sub.price,
                    "currency": "RUB"
                },
                "payment_method_data": {
                    "type": "bank_card"
                },
                "confirmation": {
                "type": "redirect",
                "return_url": f"https://t.me/mp_pro_bot"
                },
                "capture": True,
                "metadata": {
                    'telegram_user_id': f'{call.message.chat.id}',
                    'subscription_name': f'{sub.title}'},
                }, idempotence_key)
        
        
            confirmation_url = payment.confirmation.confirmation_url
            bot.send_message(call.message.chat.id, confirmation_url)
        except Exception as e:
            bot.send_message(call.message.chat.id, e)

        
@bot.message_handler(commands=['trial'])
def trial(message):
    user = db_queries.get_user_by_telegram_user_id(message.chat.id)
    transaction = db_queries.get_transaction(user_id=user.id, transaction_title="Trial")
    if user.subscriptions_id == None:
        if transaction:
            bot.send_message(message.chat.id, f'У вас уже была активирована Пробная подписка', parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, f'Информация о пробной подписке\nКнопка *Согласиться* активирует Вам подписку', reply_markup=reply_markup_trial(trial=False), parse_mode='Markdown')
    else:    
        sub = db_queries.get_sub(sub_id=user.subscriptions_id)
        if sub.title != 'Trial':
            bot.send_message(message.chat.id, f'У вас сейчас не пробная подписка', parse_mode='Markdown')
        elif sub.title == 'Trial':
            bot.send_message(message.chat.id, f'Нажмите на `Информация` чтобы узнать, что дает пробная подписка', reply_markup=reply_markup_trial(trial=True), parse_mode='Markdown')
    


@msg_handler(commands=['set_token_cmp'])
def set_token_cmp(message):
    clear_token = message.text.replace('/set_token_cmp ', '').strip()
    db_queries.set_user_wb_cmp_token(telegram_user_id=message.from_user.id, wb_cmp_token=clear_token)
    return 'Ваш токен установлен\!'


@msg_handler(commands=['search'])
def search(message):
        keyword = re.sub('/search ', '', message.text)
        item_dicts = wb_queries.search_adverts_by_keyword(keyword)
        result_message = ''

        if len(item_dicts) == 0:
            return 'ставки неизвестны'#Максим добавь чтобы при неправильном ввроде перекидывало на /start
        else:
            for item_idex in range(len(item_dicts)):
                price = item_dicts[item_idex]['price']
                p_id = item_dicts[item_idex]['p_id']
                result_message += f'{item_idex + 1}\\)  {price}р,  [ссылка на товар](https://www.wildberries.ru/catalog/{p_id}/detail.aspx) \n' 
            return result_message



@msg_handler(commands=['list_atrevds'])
def list_atrevds(message):
    user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
    user_wb_tokens = wb_queries.get_base_tokens(user)
    req_params = wb_queries.get_base_request_params(user_wb_tokens)

    view = wb_queries.get_user_atrevds(req_params)
    result_msg = ''

    for product in view:
        date_str = product['startDate']
        
        stat = status_parser(product['statusId'])
        if date_str != None:
            date_str = date_str[:10]
            date_str = re.sub('-', '\-', date_str)
        
        result_msg += f"*Имя компании: {product['campaignName']}*\n"
        result_msg += f"\t ID Рекламной компании: {product['id']}\n"
        result_msg += f"\t Имя категории: {product['categoryName']}\n"
        result_msg += f"\t Дата начала: {date_str}\n"
        result_msg += f"\t Текущий статус: {stat}\n\n"

    return result_msg


@msg_handler(commands=['add_advert'])
def add_advert(message):
    """
    Команда для запсии в бд информацию о том, что юзер включает рекламную компанию
    TO wOrKeD:
    (индентификатор, бюджет, место которое хочет занять)
    записать это в бд
    """
    user = db_queries.get_user_by_telegram_user_id(message.from_user.id)

    #(индентификатор, бюджет, место которое хочет занять)args*
    message_args = re.sub('/add_advert ', '', message.text).split(sep=' ', maxsplit=4)
    if len(message_args) != 4:
        bot.send_message(message.chat.id, f'Для использования команды используйте формат: /add_advert <campaign_id> <max_budget> <place> <status>')
        return

    campaign_id = re.sub('/add_advert ', '', message_args[0])
    max_budget = re.sub('/add_advert ', '', message_args[1])
    place = re.sub('/add_advert ', '', message_args[2])
    status = re.sub('/add_advert ', '', message_args[3])

    add_result = db_queries.add_user_advert(user, status, campaign_id, max_budget, place)
    
    if add_result == 'UPDATED':
        return 'Ваша рекламная компания успешно обновлена\!'
    elif add_result == 'ADDED':
        return 'Ваша рекламная компания успешно добавлена\!'

    return 'Произошла ошибка\!'
    


@msg_handler(commands=['delete_advert'])
def delete_advert(message):
    user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
    campaign_id = int(re.sub('/delete_advert ', '', message.text))

    if not campaign_id:
        return 'Необходимо указать ID рекламной компании\!'

    delete_result = db_queries.delete_user_advert(user, campaign_id)

    if not delete_result:
        return f'Компания {campaign_id} не найдена\!'

    return f'Компания {campaign_id} удалена\!'

  
@msg_handler(commands=['my_auto_adverts'])
def my_auto_adverts(message):

    user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
    adverts = db_queries.get_user_adverts(user.id)

    result = ''

    for advert in adverts:
        result += f"{advert.campaign_id} \t Ставка: {advert.max_budget} \t Место: {advert.place} \t Статус: {advert.status}\n"
        result = re.sub('-', '\-', result)
        result = re.sub('_', '\_', result)
        result = re.sub('!', '\!', result)

    if not adverts:
        result = 'Вы ещё не добавили команий\! Используйте add\_advert'
    
    return result



@msg_handler(commands=['reset_base_tokens'])
def reset_base_tokens(message):
    user = db_queries.get_user_by_telegram_user_id(message.from_user.id)
    tokens = wb_queries.reset_base_tokens(user)
    
    return str(tokens)



@bot.message_handler(commands=['buy'])
def buy_subscription(message):
    try:
        sub_list = db_queries.get_all_sub()
        if PAYMENT_TOKEN.split(':')[1] == 'LIVE':
            for sub in sub_list:
                bot.send_message(message.chat.id, f'Подписка - {sub.title}\nЦена - {sub.price}\nОписание - {sub.description}\n\nХотите ли вы оплатить через telegram?\nЕсли - Да, нажмите на кнопку `Оплата через телеграм`\nЕсли через сайт, нажмите на кнопку `Оплата через сайт`', reply_markup=reply_markup_payment(user_data=f"{sub.title}"))
    except Exception as e:
        bot.send_message(message.chat.id, e)
        
            

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                " try to pay again in a few minutes, we need a small rest.")
    
    
@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    total = message.successful_payment.total_amount / 100
    bot.send_message(message.chat.id,
                     'Была подключена подписка: {}\nЕсли хотите узнать подробнее - введите /show_active_sub'.format(message.successful_payment.invoice_payload))

    
    db_queries.update_sub(user_id=message.chat.id, sub_name=message.successful_payment.invoice_payload, total=total)


@bot.message_handler(commands=['show_active_sub'])
def show_active_sub(message):
    user = db_queries.get_user_by_telegram_user_id(message.chat.id)
    sub = db_queries.get_sub(sub_id=user.subscriptions_id)
    if user.subscriptions_id != None:
        bot.send_message(message.chat.id, 'Подключен: `{}`\nСрок действия с `{}` по `{}`'.format(sub.title, user.sub_start_date.strftime('%d/%m/%Y'), user.sub_end_date.strftime('%d/%m/%Y')))
    else:
        bot.send_message(message.chat.id, 'У вас не подключено никаких платных подписок')