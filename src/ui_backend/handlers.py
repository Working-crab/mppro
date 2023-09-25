import asyncio
import pandas as pd
from PIL import Image
import re
from unittest import mock
from user_analitics.graphic_analitic import graphics_analitics
from ui_backend.app import bot
from ui_backend.common import (edit_token_reply_markup, format_requests_count, 
  management_tokens_reply_markup, paid_requests_inline_markup, paid_service_reply_markup, status_parser, 
  switch_status_reply_markup, universal_reply_markup, paginate_buttons, city_reply_markup, 
  escape_telegram_specials, logs_types_reply_markup, universal_reply_markup_additionally, 
  advert_info_message_maker, reply_markup_payment, adv_settings_reply_markup, action_history_reply_markup, 
  action_history_filter_reply_markup, adv_settings_words_reply_markup, fixed_word_switch, check_sub, 
  paid_requests_inline_markup, advert_strategy_reply_markup, statistics_reply_markup, ADV_STRATS)
from telebot import types
from db.queries import db_queries
from wb_common.wb_queries import wb_queries
from wb_common.wb_api_queries import wb_api_queries
from monorepository_communication.wb_scraper_api_queries import get_csv_statistics_search_words
from datetime import datetime, timedelta
from cache_worker.cache_worker import cache_worker
from kafka_dir.general_publisher import queue_message_async
from create_table_engine.main_class import Create_table
import copy
from gpt_common.gpt_queries import gpt_queries
import json
import uuid

import io

from ui_backend.config import *
from yookassa import Payment

import traceback
from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)

#Пример для создания истории действий
#await db_queries.add_action_history(user_id=message.chat.id, action=f"Какое-то событие")
INCREASE = 10
# all messages handler
@bot.message_handler(func=lambda command: True)
async def message_handler(message):

  log_uuid = uuid.uuid4()

  try:
    telegram_user_id = message.from_user.id
    user_session = cache_worker.get_user_session(telegram_user_id)

    await db_queries.add_action_history(
      telegram_user_id=telegram_user_id,
      action="message",
      action_description=f"message uuid: '{log_uuid}' message from: '{message.chat.id}' message text: '{message.text}'",
      status="info"
    )
    
    # user = db_queries.get_user_by_telegram_user_id(telegram_user_id)
    # if user.subscriptions_id == None:
    #   if 
    #   await queue_message_async(
    #     topic = 'telegram_message_sender',
    #     destination_id = message.chat.id,
    #     message = 'У вас недостаточно прав для использования бота. Активируйте Стартовую подписку - /trial или Купите подписку!'
    #   )
    #   return
    
    logger.warn(f'telegram_user_id {telegram_user_id}')
    # logger.warn(user_session)

    message.user_session = user_session
    message.user_session_old = copy.deepcopy(user_session)
    message.user_session_step_set = False

    user_step = user_session.get('step', 'База')

    possible_actions = step_map.get(user_step, {})
    
    user_action = None
    if hasattr(message, 'callback_data'):
      for key in callback_map:
        if re.search(key, message.callback_data):
          user_action = callback_map[key]
          break
    else:
      for key in possible_actions:
        if re.search(key, message.text):
          user_action = possible_actions[key]
          break
    
    try:
      user = await db_queries.get_user_by_telegram_user_id(telegram_user_id)
      if user.subscriptions_id != None:
        sub = await db_queries.get_sub(user.subscriptions_id)
        if type(user_action) == dict:
          if sub.access_level < user_action['access_level']:
            await queue_message_async(
            topic = 'telegram_message_sender',
            destination_id = message.chat.id,
            message = 'У вас недостаточно прав для использования бота. Активируйте Стартовую подписку - /trial или Купите подписку!'
            )
            return
          else:
            user_action = user_action['action']
      else:
        if type(user_action) == dict:
          if user_action['access_level'] != 0:  
            await queue_message_async(
            topic = 'telegram_message_sender',
            destination_id = message.chat.id,
            message = 'У вас недостаточно прав для использования бота. Активируйте Стартовую подписку - /trial или Купите подписку!'
            )
            return
          else:
            user_action = user_action['action']
          
    except Exception as e:
      logger.warn('step_map_access_level error')
      logger.warn(e)

    # logger.warn(f"user_step {str(message.text)}")
    
    user_action_default = possible_actions.get('default')
    if user_action:
      await user_action(message)
    elif user_action_default:
      await user_action_default(message)
      

    if not message.user_session_step_set:
      set_user_session_step(message, 'База')

    update_user_session(message)

    await db_queries.add_action_history(
      telegram_user_id=telegram_user_id,
      action="message",
      action_description=f"message uuid: '{log_uuid}' message from: '{message.chat.id}' message text: '{message.text}' user action: '{user_action}'",
      status="success"
    )


  except Exception as e:
    traceback.print_exc()
    logger.error(e)
    logger.warn(f"EXCEPTION {str(e)}")

    await db_queries.add_action_history(
      telegram_user_id=telegram_user_id,
      action="message",
      action_description=f"message uuid: '{log_uuid}' message from: '{message.chat.id}' message text: '{message.text}' message error: '{str(e)}'",
      status="failure"
    )

    set_user_session_step(message, 'База')
    update_user_session(message)

    if str(e) == 'Неверный токен!':
      await queue_message_async(
        topic = 'telegram_message_sender',
        destination_id = message.chat.id,
        message = 'Произошла ошибка валидации токена! Возможно срок его действия истек, попробуйте перезагрузить токен!'
      )
      return
    
    if 'Произошла ошибка' in str(e):
      await queue_message_async(
        topic = 'telegram_message_sender',
        destination_id = message.chat.id,
        message = 'Произошла ошибка в формировании запроса, обратитесь к Разработчику'
      )
      return
    
    if "Read timed out" in str(e):
      await queue_message_async(
        topic = 'telegram_message_sender',
        destination_id = message.chat.id,
        message = 'WB сейчас перегружен, попробуйте еще раз позже'
      )
      return
    
    if "Ошибка установки нового токена" in str(e):
      await queue_message_async(
        topic = 'telegram_message_sender',
        destination_id = message.chat.id,
        message = 'Произошла ошибка установки нового токена! Так как уже существует WildAuthNewV3 токен, ему отдается приоритет'
      )
      return
    
    if "wb_query" in str(e):
      if "Неверный токен!" in str(e):
        await queue_message_async(
        topic = 'telegram_message_sender',
        destination_id = message.chat.id,
        message = 'Произошла ошибка валидации токена! Возможно срок его действия истек, попробуйте перезагрузить токен!'
        )
        return
      
      if "Неверный токен Public API!" in str(e):
        await db_queries.remove_public_api_token(message.chat.id)
        await queue_message_async(
        topic = 'telegram_message_sender',
        destination_id = message.chat.id,
        message = 'Произошла ошибка валидации Публичного АПИ Токена! Возможно срок его действия истек, попробуйте перезагрузить токен!'
        )
        return
      
      if "'User' object has no attribute 'update_v3_main_token'" in str(e):
        await queue_message_async(
        topic = 'telegram_message_sender',
        destination_id = message.chat.id,
        message = 'Произошла ошибка валидации токена! Попробуйте загрузить токен еще раз!'
        )
        return
      
      if "x_supplier_id Отсутствует!" in str(e):
        await queue_message_async(
          topic = 'telegram_message_sender',
          destination_id = message.chat.id,
          message = 'Произошла ошибка! x_supplier_id Отсутствует, добавьте изначально его'
        )
        return
      
      if "EOF" in str(e):
        await queue_message_async(
          topic = 'telegram_message_sender',
          destination_id = message.chat.id,
          message = 'Произошла ошибка на стороне WB, попробуйте еще раз'
        )
        return      
      # or "wb_cmp_token" in str(e)
      if "update_v3_main_token" in str(e) or "wb_cmp_token" in str(e):
        await db_queries.remove_wb_v3_main_token(str(e).split(":")[1])
        await queue_message_async(
          topic = 'telegram_message_sender',
          destination_id = message.chat.id,
          message = 'Произошла ошибка с WildAuthNewV3 Token, токен был сброшен'
        )
        return
    
      else:
        await queue_message_async(
          topic = 'telegram_message_sender',
          destination_id = message.chat.id,
          message = 'Произошла ошибка при обращению к Wildberries, попробуйте позже'
        )
        return
    
      

    await queue_message_async(
      topic = 'telegram_message_sender',
      destination_id = message.chat.id,
      message = 'На стороне сервера произошла ошибка, обратитесь к разработчику или попробуйте позже'
    )


# all callbacks query handler
@bot.callback_query_handler(func=lambda m: True)
async def callback_query_handler(data):
  message = data.message
  message.callback_data = data.data
  message.callback_id = data.id
  message.from_user = data.from_user
  await message_handler(message)


# Ветка "Поиск" --------------------------------------------------------------------------------------------------------

async def search_adverts(message):
  await bot.send_message(message.chat.id, 'Введите ключевое слово', reply_markup=types.ReplyKeyboardRemove())
  set_user_session_step(message, 'Search_adverts')
        
async def search_next_step_handler(message, after_city_choose=False):
  telegram_user_id = message.from_user.id
  keyword = None

  if after_city_choose:
    keyword = message.user_session.get('search_last')
  else:
    keyword = message.text
      
  await db_queries.add_action_history(telegram_user_id=telegram_user_id, action="Поиск", action_description=f"Поиск по запросу: '{keyword}'")
  
  city = message.user_session.get('search_city')
  if city == None:
    city = "Москва"
  
  user = await db_queries.get_user_by_telegram_user_id(telegram_user_id)
  
  proccesing = await bot.send_message(message.chat.id, 'Обработка запроса...')
  item_dicts = await wb_queries.search_adverts_by_keyword(keyword, telegram_user_id)
  result_message = ''
  position_ids = []
  
  chat_id_proccessing = proccesing.chat.id
  message_id_proccessing = proccesing.message_id
  
  if len(item_dicts) == 0:
    await bot.delete_message(chat_id_proccessing, message_id_proccessing)
    await bot.send_message(message.chat.id, 'Такой товар не найден', reply_markup=universal_reply_markup())
    return

  for item_idex in range(len(item_dicts)):
    position_ids.append(str(item_dicts[item_idex]['p_id']))
    pos = item_dicts[item_idex].get('wb_search_position')
    price = item_dicts[item_idex]['price']
    p_id = item_dicts[item_idex]['p_id']
    
    result_message += f'*{item_idex + 1}*  \\({pos}\\)   *{price}₽*,  [{p_id}](https://www.wildberries.ru/catalog/{p_id}/detail.aspx) 🔄 \n'
  
  await bot.delete_message(chat_id_proccessing, message_id_proccessing)
  message_to_update = await bot.send_message(message.chat.id, result_message, reply_markup=universal_reply_markup(), parse_mode='MarkdownV2')


  result_message = f'Текущие рекламные ставки по запросу: *{keyword}*\nГород доставки: *{city}*\n\n'
  adverts_info = await wb_queries.get_products_info_by_wb_ids(position_ids, city, telegram_user_id)

  for item_idex in range(len(item_dicts)):

    product_id = item_dicts[item_idex]['p_id']
    price = item_dicts[item_idex]['price']
    pos = item_dicts[item_idex].get('wb_search_position')
    message_string = f'\\[{item_idex + 1}\\]  *{price}₽*,  [{product_id}](https://www.wildberries.ru/catalog/{product_id}/detail.aspx)'
    advert_info = adverts_info.get(product_id)
    position_index = f'*{item_idex + 1}*'

    if advert_info:
      product_name = escape_telegram_specials(advert_info.get('name')[:30]) if advert_info.get('name')[:30] else product_id
      product_time = f'{advert_info.get("time2")}ч' if advert_info.get('time2') else ''
      product_category_name = escape_telegram_specials(advert_info.get('category_name')) if advert_info.get('category_name') else ''
      message_string = f'{position_index} \t \\({pos}\\) \t *{price}₽*, \t {product_category_name} \t {product_time} \t [{product_name}](https://www.wildberries.ru/catalog/{product_id}/detail.aspx)'
    else:
      message_string += ' возможно нет в наличии'

    result_message += f'{message_string}\n'

  if result_message:
    await bot.delete_message(message_to_update.chat.id, message_to_update.message_id)
    await bot.send_message(message.chat.id, result_message, reply_markup=universal_reply_markup(search=True), parse_mode='MarkdownV2')
    message.user_session['search_last'] = keyword



async def choose_city(message):
  city = message.user_session.get('search_city')
  if city == None:
    city = "Москва"
  
  await bot.send_message(message.chat.id, f'Выберите город из предоставленных на панели\nУ вас стоит: *{city}*', reply_markup=city_reply_markup(), parse_mode='MarkdownV2')
        
        
async def choose_city_handler(message):
  city = message.text.split()[1]
  message.user_session['search_city'] = city
  await search_next_step_handler(message, after_city_choose=True)

# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Помощь" ---------------------------------------------------------------------------------------------------------------------------------

async def help(message):
  await queue_message_async(
    topic = 'telegram_message_sender',
    destination_id = message.chat.id,
    message = 'По вопросам работы бота обращайтесь: \n (https://t.me/Ropejamp) \n (https://t.me/plazmenni_rezak)'
  )

async def misSpell(message):
  await queue_message_async(
    topic = 'telegram_message_sender',
    destination_id = message.chat.id,
    message = 'Для работы с ботом используйте меню',
  )

# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Установить токен" -----------------------------------------------------------------------------------------------------------------------
@check_sub(['*'])
async def management_tokens(message, sub_name): 
  await bot.send_message(message.chat.id, f'Выберите тип токена для просмотра статуса\nРекомендации:\nСначала нужно поставить x_supplier_id, для правильной работоспособности, после поставить любой другой токен', reply_markup=management_tokens_reply_markup(sub_name=sub_name))
  set_user_session_step(message, 'Manage_tokens')


async def token_cmp_handler(message):
  try:
    user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
    user_wb_tokens = await wb_queries.get_base_tokens(user, check="cmp_token")
  except Exception as e:
    logger.warn(e)
    await bot.send_message(message.chat.id, f'WBToken *Не найден* либо *Просрочен*\nНапишите новый токен, если хотите добавить/исправить токен', parse_mode="MarkdownV2", reply_markup=edit_token_reply_markup())
    return set_user_session_step(message, 'Wb_cmp_token_edit')
  
  if user_wb_tokens:  
    await bot.send_message(message.chat.id, f'WBToken: {user_wb_tokens["wb_cmp_token"]}\nНа данный момент он Активен\nНапишите новый токен, если хотите изменить', reply_markup=edit_token_reply_markup())
  set_user_session_step(message, 'Wb_cmp_token_edit')
  
  
async def x_supplier_id_handler(message):
  user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  try:
    x_supplier_id = user.x_supplier_id
  except:
    x_supplier_id = None
  
  if x_supplier_id:  
    await bot.send_message(message.chat.id, f'x_supplier_id: {x_supplier_id}\nНапишите новый id, если хотите изменить', reply_markup=edit_token_reply_markup())
  else:
    await bot.send_message(message.chat.id, f'x_supplier_id *Не найден* либо *Просрочен*\nНапишите новый id, если хотите добавить/исправить id', parse_mode="MarkdownV2", reply_markup=edit_token_reply_markup())
    return set_user_session_step(message, 'x_supplier_id_edit')
  set_user_session_step(message, 'x_supplier_id_edit')
  

async def set_x_supplier_id_handler(message):
  clear_id = message.text.replace('/set_x_supplier_id ', '').strip()
  user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  
  logger.warn(clear_id)
  await bot.send_message(message.chat.id, f'Ваш id установлен\!')
  
  await db_queries.set_user_x_supplier_id(telegram_user_id=message.from_user.id, x_supplier_id=clear_id)  
  await db_queries.add_action_history(user_id=user.id, action="x_supplier_id", action_description=f"Был установлен x_supplier_id: '{clear_id}'")


async def set_token_cmp_handler(message):
  clear_token = message.text.replace('/set_token_cmp ', '').strip()
  user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)

  try:
    await wb_queries.reset_base_tokens(user, token_cmp=clear_token)
  except Exception as e:
    if str(e) == 'Неверный токен!':
      await bot.send_message(message.chat.id, 'Неверный токен\!', reply_markup=universal_reply_markup())
      return
    raise e


  await db_queries.set_user_wb_cmp_token(telegram_user_id=message.from_user.id, wb_cmp_token=clear_token)
  await bot.send_message(message.chat.id, 'Ваш токен установлен\!', reply_markup=universal_reply_markup(), parse_mode='MarkdownV2')
  await db_queries.add_action_history(user_id=user.id, action="Токен", action_description=f"Был установлен cmp Token: '{clear_token}'")
  
@check_sub(['Разработчик'])
async def get_wb_token(message, sub_name):
  await bot.send_message(message.chat.id, 'Получаю ВБ токен', reply_markup=universal_reply_markup(), parse_mode='MarkdownV2')
  users_with_tokens = await db_queries.get_work_wb_token()
  
  result = None
  for user_with_token in users_with_tokens:
    result = await wb_queries.reset_base_tokens(user_with_token, check='cmp_token', force_check=True)  
    if result != None:
      await bot.send_message(message.chat.id, escape_telegram_specials(f"telegram_user_id: {user_with_token.telegram_user_id}\nusername: {user_with_token.telegram_username}\n\nwb_cmp_token: {result['wb_cmp_token']}\n x_supplier_id: {result['x_supplier_id']}"), parse_mode='MarkdownV2')
      break
    logger.warn(result)
  logger.warn(result)
  
  
'''
async def wb_v3_main_token_handler(message):
  try:
    user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
    user_wild_auth_v3_token = await wb_queries.get_base_tokens(user, check=True)
  except Exception as e:
    logger.warn(e)
    await bot.send_message(message.chat.id, f'WildAuthNewV3 *Не найден* либо *Просрочен*\nНапишите новый токен, если хотите добавить/исправить токен', parse_mode="MarkdownV2", reply_markup=edit_token_reply_markup())
    return set_user_session_step(message, 'Wb_v3_main_token_edit')
  
  if user_wild_auth_v3_token["wb_v3_main_token"] == None or user_wild_auth_v3_token["wb_v3_main_token"] == "":
    await bot.send_message(message.chat.id, f'WildAuthNewV3 *Не найден* либо *Просрочен*\nНапишите новый токен, если хотите добавить/исправить токен', parse_mode="MarkdownV2", reply_markup=edit_token_reply_markup())
    return set_user_session_step(message, 'Wb_v3_main_token_edit')
  else:
    await bot.send_message(message.chat.id, f'WildAuthNewV3: {user_wild_auth_v3_token["wb_v3_main_token"]}\nНа данный момент он Активен\nНапишите новый токен, если хотите изменить', reply_markup=edit_token_reply_markup())
  set_user_session_step(message, 'Wb_v3_main_token_edit')


async def set_wb_v3_main_token_handler(message):
  clear_token = message.text.replace('/set_wb_v3_main_token ', '').strip()
  user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)

  logger.warn(clear_token)
  try:
    await wb_queries.reset_base_tokens(user, token_cmp=None, token_main_v3=clear_token)
  except Exception as e:
    if str(e) == 'Неверный токен!':
      await bot.send_message(message.chat.id, 'Неверный токен\!', reply_markup=universal_reply_markup())
      return
    raise e

  await db_queries.set_user_wb_v3_main_token(telegram_user_id=message.from_user.id, wb_v3_main_token=clear_token)
  await bot.send_message(message.chat.id, 'Ваш токен установлен\!', reply_markup=universal_reply_markup(), parse_mode='MarkdownV2')
  await db_queries.add_action_history(user_id=user.id, action="Токен", action_description=f"Был установлен V3 Main Token: '{clear_token}'")
'''

async def public_api_token_handler(message):
  try:
    user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
    user_public_api_token = await wb_queries.get_base_tokens(user, check="public_api_token")
  except Exception as e:
    logger.warn(e)
    await bot.send_message(message.chat.id, f'Public API Token *Не найден* либо *Просрочен*\nНапишите новый токен, если хотите добавить/исправить токен', parse_mode="MarkdownV2", reply_markup=edit_token_reply_markup())
    return set_user_session_step(message, 'public_api_token_edit')
  
  if user_public_api_token["public_api_token"] == None or user_public_api_token["public_api_token"] == "":
    await bot.send_message(message.chat.id, f'Public API Token *Не найден* либо *Просрочен*\nНапишите новый токен, если хотите добавить/исправить токен', parse_mode="MarkdownV2", reply_markup=edit_token_reply_markup())
    return set_user_session_step(message, 'public_api_token_edit')
  else:
    await bot.send_message(message.chat.id, f'Public API Token: {user_public_api_token["public_api_token"]}\nНа данный момент он Активен\nНапишите новый токен, если хотите изменить', reply_markup=edit_token_reply_markup())
  set_user_session_step(message, 'public_api_token_edit')
    

async def set_public_api_token(message):
  clear_token = message.text.replace('/set_public_api_token ', '').strip()
  user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)

  logger.warn(clear_token)
  try:
    await wb_queries.reset_base_tokens(user, public_api_token=clear_token)
  except Exception as e:
    if str(e) == 'Неверный токен!':
      await bot.send_message(message.chat.id, 'Неверный токен\!', reply_markup=universal_reply_markup())
      return
    raise e

  # message.user_session['update_v3_main_token'] = str(datetime.now())
  await db_queries.set_user_public_api_token(telegram_user_id=message.from_user.id, public_api_token=clear_token)
  await bot.send_message(message.chat.id, 'Ваш токен установлен\!', reply_markup=universal_reply_markup(), parse_mode='MarkdownV2')
  await db_queries.add_action_history(user_id=user.id, action="Токен", action_description=f"Был установлен Public API Token: '{clear_token}'")


# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Список рекламных компаний" --------------------------------------------------------------------------------------------------------------
async def list_adverts(message):
  await list_adverts_handler(message)

async def list_adverts_handler(message):
  """Функия которая формирует и отправляет рекламные компании пользователя"""

  proccesing = await bot.send_message(message.chat.id, 'Обработка запроса...')

  user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  # user_wb_tokens = await wb_queries.get_base_tokens(user)
  # req_params = await wb_queries.get_base_request_params(user_wb_tokens)
  
  page_number = 1
  
  user_atrevds_data = await wb_queries.get_user_atrevds(pagesize=page_number, user=user)
  
  page_size = 6
  logger.info(len(user_atrevds_data['adverts']))
  result_msg = await advert_info_message_maker(user_atrevds_data['adverts'], page_number=page_number, page_size=page_size, user=user)

  total_count_adverts = user_atrevds_data['total_count']
  action = "page"
  inline_keyboard = paginate_buttons(action, page_number, total_count_adverts, page_size, message.from_user.id)

  chat_id_proccessing = proccesing.chat.id
  message_id_proccessing = proccesing.message_id
  await bot.delete_message(chat_id_proccessing, message_id_proccessing)
  
  # result_msg = result_msg.replace('>', '\\>')

  await bot.send_message(message.chat.id, result_msg, reply_markup=inline_keyboard, parse_mode='MarkdownV2')



async def adv_list_pagination(message):
  await bot.edit_message_text('Вайлдберис старается 🔄', message.chat.id, message.id, parse_mode='MarkdownV2')
  type_of_callback, page_number, user_id = message.callback_data.split(':') # parameters = [type_of_callback, page_number, user_id]
  page_number = int(page_number)
  logger.warn(f"before {user_id}")
  user = await db_queries.get_user_by_telegram_user_id(telegram_user_id=user_id)
  logger.warn(f"user {user}")
  
  # user_atrevds_data = await wb_queries.get_user_atrevds(req_params, page_number=1)
  user_atrevds_data = await wb_queries.get_user_atrevds(user=user)

  page_size = 6
  result_msg = await advert_info_message_maker(user_atrevds_data['adverts'], page_number=page_number, page_size=page_size, user=user)

  total_count = user_atrevds_data['total_count']
  action = "page"
  inline_keyboard = paginate_buttons(action, page_number, total_count, page_size, user_id)

  await bot.edit_message_text(result_msg, message.chat.id, message.id, parse_mode='MarkdownV2')
  await bot.edit_message_reply_markup(message.chat.id, message.id , reply_markup=inline_keyboard)
  await bot.answer_callback_query(message.callback_id)


# ------------------------------------------------------------------------------------------------------------------------------------------------

# Ветка "Показать логи человека" -----------------------------------------------------------------------------------------------------------------
        
async def search_logs_next_step_handler(message):
  search_logs = re.sub('/search_id ', '', message.text)
  search_user_id = search_logs.split()[0]
  timestamp = search_logs.split()[1] + " " + search_logs.split()[2]
  await bot.send_message(message.chat.id, f"user_id: {search_user_id}\ntimestamp: {timestamp}\nВыберите какой тип логов Вас интерисует", reply_markup=logs_types_reply_markup(user_id=search_user_id, timestamp=timestamp))

        
# ------------------------------------------------------------------------------------------------------------------------------------------------

# Дополнительные опции ---------------------------------------------------------------------------------------------------------------------------

async def menu_additional_options(message):
  await bot.send_message(message.chat.id, "Вы перешли в раздел *Дополнительные опции*", parse_mode='MarkdownV2', reply_markup=universal_reply_markup_additionally())


async def menu_back(message):
  await bot.send_message(message.chat.id, "Добро пожаловать *Назад* 🤓", parse_mode='MarkdownV2', reply_markup=universal_reply_markup())
    

async def menu_back_word(message):
  await bot.send_message(message.chat.id, "Добро пожаловать *Назад* 🤓", parse_mode='MarkdownV2', reply_markup=adv_settings_reply_markup(message.from_user.id))


async def menu_back_selected_token(message):
  await bot.send_message(message.chat.id, "Добро пожаловать *Назад* 🤓", parse_mode='MarkdownV2', reply_markup=management_tokens_reply_markup())
  set_user_session_step(message, 'Manage_tokens')
  
  
  
async def menu_back_token(message):
  await bot.send_message(message.chat.id, "Добро пожаловать *Назад* 🤓", parse_mode='MarkdownV2', reply_markup=universal_reply_markup_additionally())
    

# ------------------------------------------------------------------------------------------------------------------------------------------------

# История действий -------------------------------------------------------------------------------------------------------------------------------
async def show_action_history(message):
  page_number = 1
  page_action = 5
  action_history = await db_queries.show_action_history(message.chat.id)
  total_count_action = len(action_history)
  
  action = "Нет"
  result_message = f'Список Ваших последних действий в боте\nФильтр: {action}\nCтраница: {page_number}\n\n'
  i = 1
  if total_count_action == 0:
    return await bot.send_message(message.chat.id, 'Нет истории действий', reply_markup=universal_reply_markup())
  else:
    if page_number == 1:
      action_history = action_history[page_number-1:page_action]
  
  for action in action_history:
    result_message += f'[{i}]-----------------------------\nДата: {(action.date_time + timedelta(hours=3)).strftime("%m/%d/%Y, %H:%M:%S")}\n\nДействие: {action.description}\n-----------------------------\n\n'
    i+=1

  action = "action"
  inline_keyboard = paginate_buttons(action, page_number, total_count_action, page_action, message.from_user.id)
  await bot.send_message(message.chat.id, result_message, reply_markup=inline_keyboard)
  await bot.send_message(message.chat.id, 'На панеле снизу Вы можете загрузить свою историю', reply_markup=action_history_reply_markup())


async def load_action_page_info(message):
  await bot.edit_message_text('Информация загружается 🔄', message.chat.id, message.id)
  type_of_callback, page_number, user_id = message.callback_data.split(':') # parameters = [type_of_callback, page_number, user_id]
    
  page_number = int(page_number)
  page_action = 5
  action = "Нет"
  if type_of_callback == "action_filter":
    action = cache_worker.get_action_history_filter(message.chat.id)
    action_history = await db_queries.show_action_history(message.chat.id, action=action)
  else:
    action_history = await db_queries.show_action_history(message.chat.id)
  result_message = f'Список Ваших последних действий в боте\nФильтр: {action}\nCтраница: {page_number}\n\n'
  total_count_action = len(action_history)
  
  if page_number != 1:
    action_history = action_history[(page_action*(page_number-1)):page_action*page_number]
    i = (5 * page_number)-4
  else:
    action_history = action_history[page_number-1:page_action]
    i = (5 * page_number)-4
    
  for action in action_history:
    result_message += f'[{i}]-----------------------------\nДата: {(action.date_time + timedelta(hours=3)).strftime("%m/%d/%Y, %H:%M:%S")}\n\nДействие: {action.description}\n-----------------------------\n\n'
    i+=1
  
  if type_of_callback == "action_filter":
    action = "action_filter"
  else:
    action = "action"
  inline_keyboard = paginate_buttons(action, page_number, total_count_action, page_action, user_id)      

  await bot.answer_callback_query(message.callback_id)
  await bot.edit_message_text(result_message, message.chat.id, message.id)
  await bot.edit_message_reply_markup(message.chat.id, message.id , reply_markup=inline_keyboard)
  
# ------------------------------------------------------------------------------------------------------------------------------------------------

# ---- История действий // КНОПКИ -------------------------------------------------------------------------------------------------------------------

async def action_history_filter(message):
  markup = await action_history_filter_reply_markup(action="filter:action")
  await bot.send_message(message.chat.id, 'Выберите фильтрацию', reply_markup=markup)
  
  
async def action_page_filter(message):
  action = message.callback_data.split(':')[2] # parameters = [type_of_callback, page_number, user_id]
  # await bot.edit_message_text(action, data.message.chat.id, data.message.id)
  
  cache_worker.set_action_history_filter(user_id=message.chat.id, filter=action)
  
  page_number = 1
  page_action = 5
  action_history = await db_queries.show_action_history(message.chat.id, action=action)
  total_count_action = len(action_history)
  
  
  result_message = f'Список Ваших последних действий в боте\nФильтр: {action}\nCтраница: {page_number}\n\n'
  i = 1
  if total_count_action == 0:
    return await bot.send_message(message.chat.id, 'Нет истории действий', reply_markup=universal_reply_markup())
  else:
    if page_number == 1:
      action_history = action_history[page_number-1:page_action]
  
  for action in action_history:
    result_message += f'[{i}]-----------------------------\nДата: {(action.date_time + timedelta(hours=3)).strftime("%m/%d/%Y, %H:%M:%S")}\n\nДействие: {action.description}\n-----------------------------\n\n'
    i+=1

  action = "action_filter"
  
  inline_keyboard = paginate_buttons(action, page_number, total_count_action, page_action, message.from_user.id)
  await bot.edit_message_text(result_message, message.chat.id, message.id, reply_markup=inline_keyboard)
  
  
async def action_history_download(message):
  await bot.send_message(message.chat.id, "Подготовка файла к установке", )
  # action = data.data.split(':')[2] # parameters = [type_of_callback, page_number, user_id]
  action_history = await db_queries.show_action_history(message.chat.id, download=True)
  
  result_message = ""
  i = 1
  for action in action_history:
    result_message += f'[{i}]-----------------------------\nДата: {(action.date_time + timedelta(hours=3)).strftime("%m/%d/%Y, %H:%M:%S")}\n\nДействие: {action.description}\n-----------------------------\n\n'
    i+=1
    
  file = io.BytesIO(result_message.encode('utf-8'))
  file.name = "action_history.txt"
  # await bot.delete_message(message.chat.id, message.id)
  
  await bot.send_document(chat_id=message.chat.id, document=file, caption="Файл готов")


# ------------------------------------------------------------------------------------------------------------------------------------------------

# --- правка ставки компании --------------------------------------------------------------------------------------------
@check_sub(['Старт', 'Победитель', 'Мастер', 'Чемпион'])
async def send_message_for_advert_bid(message, adv_id, sub_name):
  logger.warn("HERE, NOW")
  user = await db_queries.get_user_by_telegram_user_id(message.chat.id)
  adverts_count = await db_queries.get_user_adverts(user.id)
  my_sub = await db_queries.get_sub(user.subscriptions_id)
  
  if len(adverts_count) > my_sub.tracking_advertising:
    return await bot.send_message(message.chat.id, "К сожалению, вы не можете отслеживать больше РК", parse_mode = 'MarkdownV2')
  
  campaign_link = f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{adv_id}"
  result_msg = f'Укажите максимальную ставку для РК с id [{adv_id}]({campaign_link}) в рублях' #f"\t ID: [{advert['id']}]({campaign_link}) Статус: {stat}\n"
  await bot.send_message(message.chat.id, result_msg, parse_mode = 'MarkdownV2') 
  set_user_session_step(message, 'Add_advert')
  


# ------------------------------------------------------------------------------------------------------------------------------------------------

# --- правка места компании --------------------------------------------------------------------------------------------

async def send_message_for_advert_place(message, adv_id):
  campaign_link = f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{adv_id}"
  result_msg = f'Укажите предпочитаемое место для РК с id [{adv_id}]({campaign_link}) \n Бот будет держать это место' #f"\t ID: [{advert['id']}]({campaign_link}) Статус: {stat}\n"
  await bot.send_message(message.chat.id, result_msg, parse_mode = 'MarkdownV2') 
  set_user_session_step(message, 'Set_advert_place')
  

# ------------------------------------------------------------------------------------------------------------------------------------------------


# --- правка данных компании --------------------------------------------------------------------------------------------


async def send_message_for_advert_combined(message, adv_id):
  campaign_link = f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{adv_id}"
  result_msg = f'Укажите предпочитаемое место или диапазон мест через тире в формате 2\-4 для РК с id [{adv_id}]({campaign_link}) \n Бот будет держать это место в рамках максимальной ставки'
  await bot.send_message(message.chat.id, result_msg, parse_mode = 'MarkdownV2') 
  set_user_session_step(message, 'Set_advert_place')


# ------------------------------------------------------------------------------------------------------------------------------------------------


# --- добавление компании --------------------------------------------------------------------------------------------

async def add_advert(message):
  user_text = message.text
  adv_id = re.sub('/add_adv_', '', user_text)
  message.user_session['add_adv_id'] = adv_id
  await send_message_advert_strategy(message, adv_id)


@check_sub(['Старт', 'Победитель', 'Мастер', 'Чемпион'])
async def send_message_advert_strategy(message, adv_id, sub_name):
  user = await db_queries.get_user_by_telegram_user_id(message.chat.id)
  adverts_count = await db_queries.get_user_adverts(user.id)
  my_sub = await db_queries.get_sub(user.subscriptions_id)
  
  if len(adverts_count) > my_sub.tracking_advertising:
    return await bot.send_message(message.chat.id, "К сожалению, вы не можете отслеживать больше РК", parse_mode = 'MarkdownV2')
  
  campaign_link = f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{adv_id}"
  result_msg = f'''Выберите стратегию для РК с id [{adv_id}]({campaign_link})
    "{ADV_STRATS['strategy_hold_the_position']}" держит выбранную позицию за минимальную необходимую ставку
    "{ADV_STRATS['strategy_hold_the_bid']}" держит наилучшую позицию в пределах указанной максимальной ставки
    "{ADV_STRATS['strategy_combined']}" держит позицию или диапазон позиций в пределах максимальной ставки с отключением кампании при выходе за пределы максимальной ставки
    "{ADV_STRATS['strategy_combined_always_online']}" держит позицию или диапазон позиций в пределах максимальной ставки или наилучшую позицию в пределах максимальной ставки ниже диапазона
  '''
  await bot.send_message(message.chat.id, result_msg, parse_mode = 'MarkdownV2', reply_markup=advert_strategy_reply_markup(adv_id))

  set_user_session_step(message, 'choice_advert_strategy')


async def choice_advert_strategy(message):
  advert_strategy, adv_id = message.callback_data.split(':')
  message.user_session['advert_strategy'] = advert_strategy
  message.user_session['adv_settings_id'] = adv_id
  if advert_strategy == 'strategy_hold_the_position':
    await send_message_for_advert_place(message, adv_id)
  elif advert_strategy == 'strategy_hold_the_bid':
    await send_message_for_advert_bid(message, adv_id)
  elif advert_strategy == 'strategy_combined':
    await send_message_for_advert_combined(message, adv_id)
  elif advert_strategy == 'strategy_combined_always_online':
    await send_message_for_advert_combined(message, adv_id)


async def add_advert_with_define_id(message):
  user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  adv_id = message.user_session.get('add_adv_id')
  advert_strategy = message.user_session.get('advert_strategy')
  logger.warn(f"Here, and {message.text}")
  if adv_id == None:
    adv_id = message.user_session.get('adv_settings_id')
  user_number_value = re.sub(r'[^0-9]', '', message.text)
  logger.warn(user_number_value)
  await db_queries.add_user_advert(user, adv_id, max_bid=user_number_value, status='ON', strategy=advert_strategy)
  logger.warn("yes")
  await bot.send_message(message.chat.id, f'РК с id {adv_id} отслеживается с максимальной ставкой {user_number_value}')
  message.user_session['add_adv_id'] = None
    

# --- Настройки компании --------------------------------------------------------------------------------------------

async def adv_settings(message):
  user_text = message.text
  adv_id = re.sub('/adv_settings_', '', user_text)
  message.user_session['adv_settings_id'] = adv_id
  
  campaign = mock.Mock()
  campaign.campaign_id = adv_id
  campaign_user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  
  fixed = await wb_queries.get_fixed(campaign_user, campaign)
  
  message.user_session['adv_fixed'] = fixed['fixed']
  
  await bot.send_message(message.chat.id, f'Ниже представлена панель, для возможных действий с компанией {adv_id}', reply_markup=adv_settings_reply_markup(message.from_user.id))

@check_sub(['Старт', 'Победитель', 'Мастер', 'Чемпион'])
async def adv_settings_bid(message, sub_name):
  adv_id = message.user_session.get('adv_settings_id')
  await send_message_for_advert_bid(message, adv_id)


async def adv_settings_place(message):
  adv_id = message.user_session.get('adv_settings_id')
  await send_message_for_advert_place(message, adv_id)


async def set_advert_place_with_define_id(message):
  user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  adv_id = message.user_session.get('adv_settings_id')
  advert_strategy = message.user_session.get('advert_strategy')
  user_number_value = None
  user_number_values = re.findall(r'\d+-?\d*', message.text)
  logger.warn(f"user_number_values {user_number_values}")
  if len(user_number_values) > 0:
    user_number_value = user_number_values[0]
  await db_queries.add_user_advert(user, adv_id, None, status='ON', place=user_number_value, strategy=advert_strategy)
  await bot.send_message(message.chat.id, f'РК с id {adv_id} отслеживается на предпочитаемом месте {user_number_value}')
  message.user_session['add_adv_id'] = None
  if advert_strategy and 'strategy_combined' in advert_strategy:
    await send_message_for_advert_bid(message, adv_id)


async def adv_settings_get_plus_word(message):
  
  campaign = mock.Mock()
  adv_id = message.user_session.get('adv_settings_id')
  campaign.campaign_id = adv_id
  campaign_user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  
  words = await wb_queries.get_stat_words(user=campaign_user, campaign=campaign)
  
  if len(words['fixed']) == 0:
    check_new = True
  else:
    check_new = False
  
  result_message = f'*Плюс слова*\n\n'
  for plus_word in words['pluses'][:30]:
    result_message += plus_word + "\n"  
  
  if check_new:
    result_message = f'Список *Плюс слов*, которые на данный момент не активны и будут добавлены после появления \"Ключевых фраз\", автоматически, если компания отслеживается:\n\n'
    
    db_words = await db_queries.get_stat_words(types="plus", status="Created", campaing_id=adv_id)
    for plus_word in db_words:
      result_message += plus_word.word + "\n"  
    
    message.user_session['step'] = "new_get_word"
    set_user_session_step(message, "new_get_word")
  else:
    message.user_session['step'] = "get_word"
    set_user_session_step(message, "get_word")
    
  if "error" in words:
    result_message += words['error']
  
  await bot.send_message(message.chat.id, escape_telegram_specials(result_message), parse_mode="MarkdownV2", reply_markup=adv_settings_words_reply_markup(which_word="Плюс", new=check_new))
  

async def new_adv_settings_add_plus_word(message):
  await bot.send_message(message.chat.id, "Для предотвращения проблем с Wildberries, слово будет добавлено, после появления \"Ключевых фраз\", автоматически")
  await bot.send_message(message.chat.id, "Введите плюс слово")
  set_user_session_step(message, 'new_add_plus_word')
  

async def new_add_plus_word_next_step_handler(message):
  keyword = message.text

  adv_id = message.user_session.get('adv_settings_id')  
  pluse_word = keyword.lower()
  
  await db_queries.add_stat_words(types="plus", campaing_id=adv_id, word=pluse_word)
  await bot.send_message(message.chat.id, f"Слово {keyword.lower()} было добавлено")
    
  set_user_session_step(message, "new_get_word")
  

async def adv_settings_add_plus_word(message):
  await bot.send_message(message.chat.id, "Введите плюс слово")
  set_user_session_step(message, 'add_plus_word')
  
  
async def add_plus_word_next_step_handler(message):
  keyword = message.text

  campaign = mock.Mock()
  adv_id = message.user_session.get('adv_settings_id')
  campaign.campaign_id = adv_id
  campaign_user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  
  words = await wb_queries.get_stat_words(user=campaign_user, campaign=campaign)
  
  pluse_word = [word.lower() for word in words['pluses']]
  pluse_word.append(keyword.lower())
  
  try:
    await wb_queries.add_word(campaign_user, campaign, plus_word=pluse_word)
    await bot.send_message(message.chat.id, f"Слово {keyword.lower()} было добавлено")
  except:
    await bot.send_message(message.chat.id, f"На стороне WB произошла ошибка")
    
  set_user_session_step(message, "get_word")
  

async def new_adv_settings_delete_word(message):
  await bot.send_message(message.chat.id, "Введите слово/фразу, которое хотите удалить")
  set_user_session_step(message, 'new_delete_word')


async def new_delete_word_next_step_handler(message):
  keyword = message.text
  
  deleted = await db_queries.delete_stat_words(word=keyword)
  
  if deleted:
    await bot.send_message(message.chat.id, f"Слово/фраза {keyword.lower()} было удалено")
  else:
    await bot.send_message(message.chat.id, f"Не удалось найти слово/фразу в списке")
    
  set_user_session_step(message, "new_get_word")
  

async def adv_settings_get_minus_word(message):
  campaign = mock.Mock()
  adv_id = message.user_session.get('adv_settings_id')
  campaign.campaign_id = adv_id
  campaign_user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  
  words = await wb_queries.get_stat_words(user=campaign_user, campaign=campaign)
  
  if len(words['fixed']) == 0:
    check_new = True
  else:
    check_new = False  
  
  result_message = f'*Минус слова*\n\n'
  for minus_word in words['minuses'][:30]:
    result_message += minus_word + "\n"
    
  if result_message == f'*Минус слова*\n\n' and not check_new:
    result_message = "Нет минус слов"
    
  if check_new:
    db_words = await db_queries.get_stat_words(status="Created", campaing_id=adv_id, types="minus")
    result_message = f'Список *Минус слов*, которые на данный момент не активны и будут добавлены после появления \"Ключевых фраз\", автоматически, если компания отслеживается:\n\n'
    for minus_word in db_words:
      result_message += minus_word.word + "\n"  
    
    message.user_session['step'] = "new_get_word"
    set_user_session_step(message, "new_get_word")
  else:
    message.user_session['step'] = "get_word"
    set_user_session_step(message, "get_word")
    
  if "error" in words:
    result_message += words['error']
    
  await bot.send_message(message.chat.id, escape_telegram_specials(result_message), parse_mode="MarkdownV2", reply_markup=adv_settings_words_reply_markup(which_word="Минус", new=check_new))
  

async def new_adv_settings_add_minus_word(message):
  await bot.send_message(message.chat.id, "Для предотвращения проблем с Wildberries, слово будет добавлено, после появления \"Ключевых фраз\", автоматически")
  await bot.send_message(message.chat.id, "Введите минус слово")
  await bot.send_message(message.chat.id, "При добавлении Минус Фраз, нужно выключить \'*Фиксированные фразы*\'", parse_mode="MarkdownV2")
  set_user_session_step(message, 'new_add_minus_word')
  
async def new_add_minus_word_next_step_handler(message):
  # await bot.send_message(message.chat.id, "При добавлении Минус Фраз, будут выключены \'*Плюс слова*\'\nЕсли хотите отменить действие, введите: Отмена", parse_mode="MarkdownV2")
  
  keyword = message.text
  
  if keyword == "Отмена":
    return await bot.send_message(message.chat.id, "Вы вписали Отмена", parse_mode="MarkdownV2", reply_markup=adv_settings_reply_markup(message.from_user.id))
  
  adv_id = message.user_session.get('adv_settings_id')
  minus_word = keyword.lower()
  
  try:
    await db_queries.add_stat_words(types="minus", campaing_id=adv_id, word=minus_word)
    await bot.send_message(message.chat.id, f"Слово {keyword.lower()} было добавлено")
  except:
    await bot.send_message(message.chat.id, f"Произошла ошибка")
    
  set_user_session_step(message, "new_get_word")
  
  
async def adv_settings_add_minus_word(message):
  await bot.send_message(message.chat.id, "Введите минус слово")
  await bot.send_message(message.chat.id, "При добавлении Минус Фраз, нужно выключить \'*Фиксированные фразы*\'", parse_mode="MarkdownV2")
  set_user_session_step(message, 'add_minus_word')
  
async def add_minus_word_next_step_handler(message):
  # await bot.send_message(message.chat.id, "При добавлении Минус Фраз, будут выключены \'*Плюс слова*\'\nЕсли хотите отменить действие, введите: Отмена", parse_mode="MarkdownV2")
  
  keyword = message.text
  
  if keyword == "Отмена":
    return await bot.send_message(message.chat.id, "Вы вписали Отмена", parse_mode="MarkdownV2", reply_markup=adv_settings_reply_markup(message.from_user.id))
  
  campaign = mock.Mock()
  adv_id = message.user_session.get('adv_settings_id')
  campaign.campaign_id = adv_id
  campaign_user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  words = await wb_queries.get_stat_words(user=campaign_user, campaign=campaign)
  
  minus_word = [word.lower() for word in words['minuses']]
  minus_word.append(keyword.lower())
  
  try:
    await wb_queries.add_word(campaign_user, campaign, excluded_word=minus_word)
    await bot.send_message(message.chat.id, f"Слово {keyword.lower()} было добавлено")
  except:
    await bot.send_message(message.chat.id, f"На стороне WB произошла ошибка")
    
  set_user_session_step(message, "get_word")
  
  
async def adv_settings_delete_plus_word(message):
  await bot.send_message(message.chat.id, "Введите Плюс слово/фразу, которое хотите удалить")
  set_user_session_step(message, 'delete_plus_word')


async def delete_plus_word_next_step_handler(message):
  keyword = message.text

  campaign = mock.Mock()
  adv_id = message.user_session.get('adv_settings_id')
  campaign.campaign_id = adv_id
  campaign_user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  
  words = await wb_queries.get_stat_words(user=campaign_user, campaign=campaign)
  pluse_word = []
  check = False
  for word in words['pluses']:
    if word == keyword:
      check = True
      continue
    else:
      pluse_word.append(word)
  
  try:
    if check:
      await wb_queries.add_word(campaign_user, campaign, plus_word=pluse_word)
      await bot.send_message(message.chat.id, f"Слово/фраза {keyword.lower()} было удалено")
    else:
      await bot.send_message(message.chat.id, f"Не удалось найти слово/фразу в списке")  
  except:
    await bot.send_message(message.chat.id, f"На стороне WB произошла ошибка")
    
  set_user_session_step(message, "get_word")
  

async def adv_settings_delete_minus_word(message):
  await bot.send_message(message.chat.id, "Введите Минус слово/фразу, которое хотите удалить")
  set_user_session_step(message, 'delete_minus_word')


async def delete_minus_word_next_step_handler(message):
  keyword = message.text

  campaign = mock.Mock()
  adv_id = message.user_session.get('adv_settings_id')
  campaign.campaign_id = adv_id
  campaign_user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  if campaign_user.public_api_token:
    words = await wb_api_queries.get_stat_words(user=campaign_user, campaign=campaign)
  else:
    words = await wb_queries.get_stat_words(user=campaign_user, campaign=campaign)
  
  minus_word = []
  check = False
  for word in words['minuses']:
    if word == keyword:
      check = True
      continue
    else:
      minus_word.append(word)
  
  try:
    if check:
      await wb_queries.add_word(campaign_user, campaign, excluded_word=minus_word)
      await bot.send_message(message.chat.id, f"Слово/фраза {keyword.lower()} было удалено")
    else:
      await bot.send_message(message.chat.id, f"Не удалось найти слово/фразу в списке")  
  except:
    await bot.send_message(message.chat.id, f"На стороне WB произошла ошибка")
    
  set_user_session_step(message, "get_word")
  

async def adv_settings_switch_fixed_word(message):
  campaign = mock.Mock()
  adv_id = message.user_session.get('adv_settings_id')
  campaign.campaign_id = adv_id
  campaign_user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  words = await wb_queries.get_stat_words(user=campaign_user, campaign=campaign)
    
  if words['fixed_status']:
    await bot.send_message(message.chat.id, f"Фиксированные фразы на данный момент: *Включены*", parse_mode="MarkdownV2", reply_markup=fixed_word_switch(fixed_status=True))
  else:
    await bot.send_message(message.chat.id, f"Фиксированные фразы на данный момент: *Выключены*", parse_mode="MarkdownV2", reply_markup=fixed_word_switch(fixed_status=False))
    
  set_user_session_step(message, 'fixed_word_status')
  
  
async def adv_settings_switch_on_word(message):
  message.user_session['adv_fixed'] = True
  update_user_session(message)
  campaign = mock.Mock()
  adv_id = message.user_session.get('adv_settings_id')
  campaign.campaign_id = adv_id
  campaign_user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  
  words = await wb_queries.get_stat_words(user=campaign_user, campaign=campaign)
  
  proccesing = await bot.send_message(message.chat.id, 'Обработка запроса...')
  chat_id_proccessing = proccesing.chat.id
  message_id_proccessing = proccesing.message_id
  
  
  if len(words['fixed']) == 0:
    switch = await db_queries.change_status_stat_words(campaing_id=adv_id, types="Change", words="On")
    await bot.delete_message(chat_id_proccessing, message_id_proccessing)
    await bot.send_message(message.chat.id, f"Фиксированные фразы будут *включены* автоматически, когда появяться \"Ключевые слова\", автоматически, если компания отслеживается", parse_mode="MarkdownV2", reply_markup=adv_settings_reply_markup(message.from_user.id))
  else:
    try:      
      switch = await wb_queries.switch_word(user=campaign_user, campaign=campaign, switch="true")
      words = await wb_queries.get_stat_words(user=campaign_user, campaign=campaign)
        
      await bot.delete_message(chat_id_proccessing, message_id_proccessing)
      if words['fixed_status']:
        await bot.send_message(message.chat.id, f"Фиксированные фразы были *Включены*", parse_mode="MarkdownV2", reply_markup=adv_settings_reply_markup(message.from_user.id))
      else:
        await bot.send_message(message.chat.id, f"Произошла ошибка и Фиксированные фразы не были *Включены*, попробуйте еще раз", parse_mode="MarkdownV2", reply_markup=fixed_word_switch(fixed_status=False))
    except Exception as e:
      logger.warn(f"error {e}")
      await bot.send_message(message.chat.id, f"Произошла ошибка при изменении статуса фиксированных фраз, попробуйте еще раз", parse_mode="MarkdownV2", reply_markup=adv_settings_reply_markup(message.from_user.id))
    
  
async def adv_settings_switch_off_word(message):
  message.user_session['adv_fixed'] = False
  update_user_session(message)
  campaign = mock.Mock()
  adv_id = message.user_session.get('adv_settings_id')
  campaign.campaign_id = adv_id
  campaign_user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  
  words = await wb_queries.get_stat_words(user=campaign_user, campaign=campaign)
  
  proccesing = await bot.send_message(message.chat.id, 'Обработка запроса...')
  chat_id_proccessing = proccesing.chat.id
  message_id_proccessing = proccesing.message_id
  
  if len(words['fixed']) == 0:
    switch = await db_queries.change_status_stat_words(campaing_id=adv_id, types="Change", words="Off")
    await bot.delete_message(chat_id_proccessing, message_id_proccessing)
    await bot.send_message(message.chat.id, f"Фиксированные фразы будут *выключены* автоматически, когда появяться \"Ключеваые слова\", автоматически, если компания отслеживается", parse_mode="MarkdownV2", reply_markup=adv_settings_reply_markup(message.from_user.id))
  else:
    try:
      switch = await wb_queries.switch_word(user=campaign_user, campaign=campaign, switch="false")
      words = await wb_queries.get_stat_words(user=campaign_user, campaign=campaign)
      await bot.delete_message(chat_id_proccessing, message_id_proccessing)
      if not words['fixed_status']:
        await bot.send_message(message.chat.id, f"Фиксированные фразы были *Выключены*", parse_mode="MarkdownV2", reply_markup=adv_settings_reply_markup(message.from_user.id))
      else:
        await bot.send_message(message.chat.id, f"Произошла ошибка и Фиксированные фразы не были *Выключены*, попробуйте еще раз", parse_mode="MarkdownV2", reply_markup=fixed_word_switch(fixed_status=True))
    except Exception:
      await bot.send_message(message.chat.id, f"Произошла ошибка при изменении статуса фиксированных фраз, попробуйте еще раз", parse_mode="MarkdownV2", reply_markup=adv_settings_reply_markup(message.from_user.id))
    
  
async def adv_settings_switch_status(message):
  proccesing = await bot.send_message(message.chat.id, 'Обработка запроса...')
  
  campaign = mock.Mock()
  adv_id = message.user_session.get('adv_settings_id')
  campaign.campaign_id = adv_id
  campaign_user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  
  
  status = await wb_queries.get_campaign_info(campaign_user, campaign)
  budget = await wb_queries.get_budget(campaign_user, campaign)
  # except:
  #   return await bot.send_message(message.chat.id, f"Произошла ошибка при получении *Статуса* на стороне WB, попробуйте позже", parse_mode="MarkdownV2")
  logger.warn(status)
  status_parse = status_parser(status['status'])
  
  chat_id_proccessing = proccesing.chat.id
  message_id_proccessing = proccesing.message_id
  await bot.delete_message(chat_id_proccessing, message_id_proccessing)
  
  if status_parse == "Приостановлено":
    if budget['Бюджет компании'] == 0:
      await bot.send_message(message.chat.id, f"На данный момент статус компании: *{status_parse}*\nЧтобы изменить статус пополните бюджет", parse_mode="MarkdownV2")
    else:
      await bot.send_message(message.chat.id, f"На данный момент статус компании: *{status_parse}*\nВы можете изменить статус на *Активно*, кнопкой ниже", parse_mode="MarkdownV2", reply_markup=switch_status_reply_markup(status=status['status'], campaing_id=adv_id))
  elif status_parse == "Активна":
    await bot.send_message(message.chat.id, f"На данный момент статус компании: *{status_parse}*\nВы можете изменить статус на *Приостановлено*, кнопкой ниже", parse_mode="MarkdownV2", reply_markup=switch_status_reply_markup(status=status['status'], campaing_id=adv_id))


async def change_adv_status(message):
  await bot.edit_message_text("Изменение статуса...", message.chat.id, message.id)
  change_to = message.callback_data.split(':')[2]
  campaign = mock.Mock()
  adv_id = message.callback_data.split(':')[3]
  campaign.campaign_id = adv_id
  user_id = message.chat.id
  campaign_user = await db_queries.get_user_by_telegram_user_id(user_id)
  
  await wb_queries.switch_status(campaign_user, campaign, status=change_to)
  
  if change_to == "pause":
    await bot.edit_message_text("Статус был успешно изменён на *Приостановлено*", message.chat.id, message.id, parse_mode="MarkdownV2")
    
  elif change_to == "active":
    await bot.edit_message_text("Статус был успешно изменён на *Активно*", message.chat.id, message.id, parse_mode="MarkdownV2")


async def adv_settings_add_budget(message):
  campaign = mock.Mock()
  adv_id = message.user_session.get('adv_settings_id')
  campaign.campaign_id = adv_id
  
  campaign_user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  budget = await wb_queries.get_budget(campaign_user, campaign)
  budget = budget['Бюджет компании']
  
  await bot.send_message(message.chat.id, f'Текущий бюджет: {budget} ₽\nid рекламной компании: [{adv_id}](https://cmp.wildberries.ru/campaigns/list/all/edit/search/{adv_id})\nВведите сумму пополенения бюджета или нажмите "Назад"', parse_mode="MarkdownV2")
  set_user_session_step(message, 'add_budget')
  
  
async def add_budget_next_step_handler(message):
  keyword = message.text  
  
  amount = int(keyword)
  
  campaign = mock.Mock()
  
  adv_id = message.user_session.get('adv_settings_id')
  campaign.campaign_id = adv_id
  
  campaign_user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  budget = await wb_queries.get_budget(campaign_user, campaign)
  budget = budget['Бюджет компании']
  await asyncio.sleep(2)
  
  if amount <= 499:
    return await bot.send_message(message.chat.id, f'Невозможно пополнить бюджет компании менее, чем на 499 ₽', parse_mode="MarkdownV2")
  if amount % 50 != 0:
    return await bot.send_message(message.chat.id, f'Невозможно пополнить бюджет компании, сумма не кратна 50', parse_mode="MarkdownV2")
  
  try:
    check = await wb_queries.add_budget(campaign_user, campaign, amount)
    budget2 = await wb_queries.get_budget(campaign_user, campaign)
    logger.warn("After check")
    budget2 = budget2['Бюджет компании']
    logger.warn("After budget")
    if budget2 == None:
      return await bot.send_message(message.chat.id, f'WB не вернул бюджет, попробуйте посмотреть изменение бюджета, нажав повторно кнопку \"Пополнить бюджет\"', parse_mode="MarkdownV2")
    else:
      if budget == budget2:
        return await bot.send_message(message.chat.id, f'Не удалось пополнить бюджет рекламной компании, попробуйте еще раз', parse_mode="MarkdownV2")
      else:
        return await bot.send_message(message.chat.id, f'Был успешно пополнен бюджет компании на {amount} ₽\nТекущий бюджет: {budget2} ₽', parse_mode="MarkdownV2")
  except Exception as e:
    logger.warn("HERE")
    traceback.print_exc()
    logger.warn(e)
    await bot.send_message(message.chat.id, f'На стороне вб произошла ошибка, попробуйте ещё раз чуть позже', parse_mode="MarkdownV2")
    
    

# Подписка и запросы -----------------------------------------------------------------------------------------------------------------------

async def show_paid_services(message):
  await bot.send_message(message.chat.id, "Здравствуйте, здесь Вы можете купить *подписку* или *запросы* для ChatGPT", parse_mode="MarkdownV2", reply_markup=paid_service_reply_markup())
  set_user_session_step(message, 'paid_service')
  
  
async def show_my_requests(message):
  set_user_session_step(message, 'paid_service')
  user = await db_queries.get_user_by_telegram_user_id(message.chat.id)
  gpt_requests = await db_queries.get_user_gpt_requests(user_id=user.id)
  
  gpt_requests = 0 if gpt_requests == None else gpt_requests
    # цена запроса с огр на длинну 255 символов(которые вводит юзер) + * кол во на 2 + * 100 умножить(свободный)
  await bot.send_message(message.chat.id, f'На данный момент у вас: {format_requests_count(gpt_requests)}, нажав на кнопку под сообщением, вы можете купить определенное количество запросов', reply_markup=paid_requests_inline_markup())
    

async def paid_service(message):
  user = await db_queries.get_user_by_telegram_user_id(message.chat.id)
  
  action, action_type, amount =  message.callback_data.split(":")
  amount = int(amount)
  if amount == 100:
    price = amount * INCREASE * 0.9
  else:
    price = amount * INCREASE
  
  if action_type == "requests":
    await bot.send_message(message.chat.id, f'Вы выбрали покупку запросов\nКоличество: {amount}\n Цена: {price} ₽', reply_markup=reply_markup_payment(purchase=action_type, user_data=f"{amount}:{price}"))
  

async def show_my_sub(message):
  set_user_session_step(message, 'paid_service')
  user = await db_queries.get_user_by_telegram_user_id(message.chat.id)
  if user.subscriptions_id:
    my_sub = await db_queries.get_sub(sub_id=user.subscriptions_id)
    await bot.send_message(message.chat.id, 'Подключен: `{}`\nОписание: `{}`\nСрок действия с `{}` по `{}`'.format(my_sub.title, my_sub.description, user.sub_start_date.strftime('%d/%m/%Y'), user.sub_end_date.strftime('%d/%m/%Y')), reply_markup=paid_service_reply_markup())
    
    sub_list = await db_queries.get_all_sub()
    max_access_level = max([sub.access_level for sub in sub_list])
    if max_access_level > my_sub.access_level:
      await bot.send_message(message.chat.id, 'Вы можете обновиться на более крутую подписку', reply_markup=paid_service_reply_markup())
      
      for sub in sub_list:
        if sub.title == my_sub.title or sub.access_level < my_sub.access_level:
          continue
        await bot.send_message(message.chat.id, f'Подписка - {sub.title}\nЦена - {sub.price}\nОписание - {sub.description}', reply_markup=reply_markup_payment(purchase="subscription", user_data=f"{sub.title}")) # \n\nНа данный момент доступная оплата через сайт, нажмите на кнопку `Оплата через сайт`, чтобы оплатить через сайт
  else:
    await bot.send_message(message.chat.id, 'У вас не подключено никаких платных подписок\nНиже предоставлены варианты для покупки: ')
    sub_list = await db_queries.get_all_sub()
    for sub in sub_list:
      await bot.send_message(message.chat.id, f'Подписка - {sub.title}\nЦена - {sub.price}\nОписание - {sub.description}', reply_markup=reply_markup_payment(purchase="subscription", user_data=f"{sub.title}"))

# --------------------------------------------------------------------------------------------------------------------------------

# --- card product --------------------------------------------------------------------------------------------

async def card_product(message):
  user = await db_queries.get_user_by_telegram_user_id(message.chat.id)
  gtp_requests = await db_queries.get_user_gpt_requests(user_id=user.id)
    
  if gtp_requests >= 1:
    # цена запроса с огр на длинну 255 символов(которые вводит юзер) + * кол во на 2 + * 100 умножить(свободный)
    await bot.send_message(message.chat.id, f'На данный момент у вас: {gtp_requests} запросов\nВведите ключевые слова для описание товара', reply_markup=edit_token_reply_markup())
    set_user_session_step(message, 'card_product')
  else:
    # await bot.send_message(message.chat.id, f'На данный момент у вас "{tokens}" токенов, этого не хватает для создания карточки товара.\nМинимум 100', reply_markup=universal_reply_markup())
    await bot.send_message(message.chat.id, f'На данный момент у вас "{gtp_requests}" запросов, этого не достаточно для создания карточки товара.', reply_markup=universal_reply_markup())
    set_user_session_step(message, 'База')


async def card_product_next_step_handler(message):
  user = await db_queries.get_user_by_telegram_user_id(message.chat.id)
    
  keyword = message.text
  
  if len(keyword) >= 255:
    return await bot.send_message(message.chat.id, f'К сожалению, нельзя использовать больше 255 символов, попробуйте еще раз', reply_markup=universal_reply_markup())
  
  proccesing = await bot.send_message(message.chat.id, "Обработка запроса...", reply_markup=universal_reply_markup())
  user = await db_queries.get_user_by_telegram_user_id(message.chat.id)
  gpt_text = await gpt_queries.get_card_description(user_id=user.id, prompt=keyword)
  # logger.warn(gpt_text)
  
  await bot.delete_message(proccesing.chat.id, proccesing.message_id)
  await bot.send_message(message.chat.id, gpt_text, reply_markup=universal_reply_markup())

# --------------------------------------------------------------------------------------------------------------------------------

# --- работа с сессией --------------------------------------------------------------------------------------------

def set_user_session_step(message, step_name):
  message.user_session['step'] = step_name
  message.user_session_step_set = True

def update_user_session(message):
  if message.user_session == message.user_session_old:
    return
  
  message.user_session['updated_at'] = str(datetime.now())
  cache_worker.set_user_session(message.from_user.id, message.user_session)

# --- график с аналитикой для юзера -----------------
async def user_analitics_grafic(message):
  user = await db_queries.get_user_by_telegram_user_id(message.from_user.id)
  user_id = user.id
  try:
    campaign_id = message.text.split('_')[-1]
    file = graphics_analitics.start(user_id, campaign_id)
    await bot.send_photo(message.chat.id, types.InputFile(file))
    graphics_analitics.delete_photo(file)
  except Exception:
    await bot.send_message(message.chat.id, 'Произошла ошибка с формированием графика')

# --- Статистика ----------------------------------

async def show_statistics_menu(message):
  await bot.send_message(message.chat.id, 'Меню статистики', reply_markup=statistics_reply_markup())
  set_user_session_step(message, 'Show_statistics_menu')

async def id_getter(message):
  await bot.send_message(message.chat.id, 'Введите ID товара и опционально период')
  set_user_session_step(message, 'Statistics_on_popular_queries')

async def statistics_on_popular_queries(message):
  user_input = message.text.split(' ')
  p_id, start_date, end_date = None, None, None
  if len(user_input) == 1:
    p_id = user_input[0]
  elif len(user_input) == 2:
    p_id, start_date = user_input
  elif len(user_input) == 3:
    p_id, start_date, end_date = user_input
  else:
    await bot.send_message(message.chat.id, "Возможно вы ввели что-то неправильно, формат через пробелы 'id продукта' 'дата начала' 'дата окончания'")
    set_user_session_step(message, 'Show_statistics_menu')
    return
  result = await get_csv_statistics_search_words(p_id, start_date, end_date)
  df = pd.DataFrame(result.json())

  if len(df) < 6:
    creater_table = Create_table(df=df)
    creater_table.create_table()
    table_img = creater_table.get_img_table()
    await bot.send_photo(message.chat.id, table_img)
  else:
    # file = io.BytesIO(result.content)
    file = io.BytesIO()
    df.to_csv(path_or_buf=file, index= False,encoding='utf-8-sig')
    short_df = df.head(5)
    creater_table = Create_table(df=short_df)
    creater_table.create_table()
    table_img = creater_table.get_img_table()
    await bot.send_photo(message.chat.id, table_img)
    file.seek(0)
    await bot.send_document(message.chat.id, file, visible_file_name=f'admp.pro Статистика по поисковым запросам WB {p_id}.csv')
    
  set_user_session_step(message, 'Show_statistics_menu')



# --- маппинг степов --------------------------------------------------------------------------------------------

step_map = {
  'База': {
    'user_analitics_grafic': user_analitics_grafic,
    'Помощь': help,
    'Поиск': search_adverts,
    'Подписка и запросы': show_paid_services,
    'Список рекламных компаний': {"action": list_adverts, "access_level": 1},
    'Выбрать город': choose_city,
    'Выбор:': choose_city_handler,
    'Управление токенами': management_tokens,
    'История действий': show_action_history,
    'Дополнительные опции': menu_additional_options,
    'Выбрать фильтрацию': action_history_filter,
    'Статистика': show_statistics_menu,
    # 'Статистика по популярным запросам': show_statistics,
    'Загрузить историю действий': action_history_download,
    'Назад': menu_back,
    'add_adv_': add_advert,
    'adv_settings_': adv_settings,
    'Изменить максимальную ставку': adv_settings_bid,
    'Изменить предпочитаемое место': adv_settings_place,
    'Показать Плюс слова': adv_settings_get_plus_word,
    'Показать Минус слова': adv_settings_get_minus_word,
    'Включить Фиксированные фразы': adv_settings_switch_on_word,
    'Выключить Фиксированные фразы': adv_settings_switch_off_word,
    'Пополнить бюджет': adv_settings_add_budget,
    'Изменить статус': adv_settings_switch_status,
    'Карточка товара': {"action": card_product, "access_level": 1},
    'Посмотреть статус Фиксированных фраз': adv_settings_switch_fixed_word,
    'default': misSpell
  },
  'Search_adverts': {
    'default': search_next_step_handler
  },
  'Set_token_cmp': {
    'default': set_token_cmp_handler
  },
  'Show_statistics_menu':{
    'Статистика по популярным запросам': id_getter,
    'Назад': menu_back,
  },
  'Statistics_on_popular_queries':{
    'default': statistics_on_popular_queries,
    'Назад': show_statistics_menu,
  },
  'Manage_tokens': {
    'WBToken': token_cmp_handler,
    # 'WildAuthNewV3': wb_v3_main_token_handler,
    'x_supplier_id': x_supplier_id_handler,
    'PublicAPIToken': public_api_token_handler,
    'GetWbToken': get_wb_token,
    'Назад' : menu_back_token,
  },
  'Wb_cmp_token_edit': {
    'default': set_token_cmp_handler,
    'Назад' : menu_back_selected_token,
  },
  # 'Wb_v3_main_token_edit': {
  #   'default': set_wb_v3_main_token_handler,
  #   'Назад' : menu_back_selected_token,
  # },
  'public_api_token_edit': {
    'default': set_public_api_token,
    'Назад': menu_back_selected_token,
  },
  'x_supplier_id_edit': {
    'default': set_x_supplier_id_handler,
    'Назад' : menu_back_selected_token,
  },
  'Add_advert': {
    'default': add_advert_with_define_id
  },
  'choice_advert_strategy': {
    'default': menu_back_word,
  },
  'fixed_word_status': {
    'Назад': menu_back_word,
    'Включить Фиксированные фразы': adv_settings_switch_on_word,
    'Выключить Фиксированные фразы': adv_settings_switch_off_word,
  },
  'Set_advert_place': {
    'Назад': menu_back_word,
    'default': set_advert_place_with_define_id
  },
  'card_product': {
    'default': card_product_next_step_handler,
    'Назад': menu_back,
  },
  'get_word': {
    'Назад': menu_back_word,
    'Добавить Плюс слово': adv_settings_add_plus_word,
    'Добавить Минус слово': adv_settings_add_minus_word,
    'Удалить Плюс слово': adv_settings_delete_plus_word,
    'Удалить Минус слово': adv_settings_delete_minus_word,
  },
  'add_plus_word': {
    'default': add_plus_word_next_step_handler,
    'Назад': menu_back_word,
  },
  'add_minus_word': {
    'default': add_minus_word_next_step_handler,
    'Назад': menu_back_word,
  },
  'delete_plus_word': {
    'default': delete_plus_word_next_step_handler,
    'Назад': menu_back_word,
  },
  'delete_minus_word': {
    'default': delete_minus_word_next_step_handler,
    'Назад': menu_back_word,
  },
  # New - Обозначает то, что РК новая и поэтому добавление новых слов будет с задержкой
  'new_get_word': {
    'Назад': menu_back_word,
    'Добавить Плюс слово Потом': new_adv_settings_add_plus_word,
    'Добавить Минус слово Потом': new_adv_settings_add_minus_word,
    'Удалить Плюс слово Потом': new_adv_settings_delete_word,
    'Удалить Минус слово Потом': new_adv_settings_delete_word,
  },
  'new_add_plus_word': {
    'default': new_add_plus_word_next_step_handler,
    'Назад': menu_back_word,
  },
  'new_add_minus_word': {
    'default': new_add_minus_word_next_step_handler,
    'Назад': menu_back_word,
  },
  'new_delete_word': {
    'default': new_delete_word_next_step_handler,
    'Назад': menu_back_word,
  },
  'add_budget': {
    'default': add_budget_next_step_handler,
    'Назад': menu_back_word,
  },
  'paid_service': {
    'Моя подписка': show_my_sub,
    'Мои запросы': show_my_requests,
    'Назад': menu_back
  }
}

callback_map = {
  'page': adv_list_pagination,
  'strategy_': choice_advert_strategy,
  'action': load_action_page_info,
  'filter:action:': action_page_filter,
  'status:change:': change_adv_status,
  'paid_service:': paid_service,

}