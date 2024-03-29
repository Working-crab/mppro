
import json
import datetime

from db.queries import db_queries
from wb_common.wb_queries import wb_queries

import asyncio

class analitics_automation:
  @staticmethod
  async def get_current_budget(user_id, campaign_id):
    user = db_queries.get_user_by_id(user_id)
    campaign_identify = db_queries.get_campaign_by_user_id_and_campaign_id(user.id, campaign_id)
    return (await wb_queries.get_budget(user, campaign_identify)).get('Бюджет компании', '')# Возвращает текущий бюджет компании


  @staticmethod
  async def get_campaign_bid(user_id, campaign_id):
    user = db_queries.get_user_by_id(user_id)
    campaign_identify = db_queries.get_campaign_by_user_id_and_campaign_id(user.id, campaign_id)
    return (await wb_queries.get_campaign_info(user, campaign_identify)).get('campaign_bid', '')# Возвращает текущую ставку компании


  @staticmethod
  async def start(user_id, campaign_id):
    pass
    # Экономия пользователя TODO: Не работает

    # max_bid_company = db_queries.get_campaign_by_user_id_and_campaign_id(user_id, campaign_id).max_bid # .max_bid нет Получаем Максимальную ставку кампании из Адвертов
    # max_budget_company = await analitics_automation.get_current_budget(user_id, campaign_id)# Получаем текущий бюджет компании(макс)
    # current_bid = await analitics_automation.get_campaign_bid(user_id, campaign_id)# Получает текущую ставку кампании
    # user_economy = int(max_bid_company) - int(current_bid)
    # time = datetime.datetime.now()# Текущая дата и время
    # db_queries.add_user_analitcs(user_id, campaign_id, max_bid_company, max_budget_company, current_bid, user_economy, time) 
