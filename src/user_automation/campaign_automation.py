
import asyncio
from db.queries import db_queries
from wb_common.wb_queries import wb_queries
import time
from datetime import datetime
from user_analitics import main as user_analitics
import traceback

import asyncio

from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)

class campaign_automation:

  async def start():
    adverts = await db_queries.get_adverts_chunk()

    print('============= campaign automation start =============')

    if not adverts:
      return False
    
    for advert in adverts:
      await asyncio.sleep(1)
      print('=== campaign automation ===')
      # print(campaign.campaign_id, campaign)

      try:
        await campaign_automation.check_campaign(advert)
        await campaign_automation.check_stat_word(advert)
        await user_analitics.start_logs_analitcs(advert.user_id, advert.campaign_id)
      except Exception as e:
        await db_queries.add_action_history(user_id=advert.user_id, action="campaign_scan", action_description=f'check_campaign id: {advert.campaign_id} \t new_bid: {new_bid} \t old_bid: {old_bid}')
        traceback.print_exc()
        logger.error(f'Exception: {e}.')


  async def check_campaign(campaign):

    campaign_user = await db_queries.get_user_by_id(campaign.user_id)

    campaign_info = None

    # campaign_info = await wb_queries.very_try_get_campaign_info(campaign_user, campaign, 5)
    campaign_info = await wb_queries.get_campaign_info(campaign_user, campaign, False)

    # auto stop checking if not valid
    logger.warn('logger.warn(campaign_info)')
    logger.warn(campaign_info)
    if campaign_info.get('status') == 'OFF_CAMP':  
      await db_queries.add_user_advert(campaign_user, campaign.campaign_id, None, 'OFF', None)      
      await db_queries.add_action_history(user_id=campaign.user_id, action="campaign_off", action_description=campaign.campaign_id)
      logger.warn("OFF")
      return False

    if campaign_info['status'] != 9: # check only active campaigns
      return False

    check_word = campaign_info['campaign_key_word']

    # TODO adjust pluse logics
    # campaign_pluse_words = await wb_queries.get_stat_words(campaign_user, campaign)
    # if campaign_pluse_words['main_pluse_word']:
    #   check_word = campaign_pluse_words['main_pluse_word']

    current_bids_table = await wb_queries.search_adverts_by_keyword(check_word)

    new_bid = 0
    approximate_place = 0
    bid_p_id = 0

    for bid in current_bids_table:
      if int(bid['position']) < int(campaign.place):
        continue
      if bid['price'] < campaign.max_bid:
        new_bid = bid['price'] + 1
        bid_p_id = bid['p_id']
        approximate_place = bid['position']
        break

    old_bid = campaign_info["campaign_bid"]

    await db_queries.add_action_history(user_id=campaign.user_id, action="campaign_scan", action_description=f'check_campaign id: {campaign.id} \t new_bid: {new_bid} \t old_bid: {old_bid}')


    if new_bid != old_bid and bid_p_id != campaign.campaign_id:

      # emulate full setup
      await wb_queries.set_campaign_bid(campaign_user, campaign, campaign_info, new_bid, old_bid, approximate_place)
      await wb_queries.get_campaign_info(campaign_user, campaign, False)
      await wb_queries.post_get_active(campaign_user, campaign)
      

    pass


  async def check_stat_word(campaign):
    logger.warn(campaign.campaign_id)
    db_words = await db_queries.get_stat_words(campaing_id=campaign.campaign_id, status="Created")
    logger.warn(db_words)
    if not db_words:
      return
    campaign_user = await db_queries.get_user_by_id(campaign.user_id)
    words = await wb_queries.get_stat_words(user=campaign_user, campaign=campaign)
    logger.warn("before if")
    logger.warn(words)
    if len(words['fixed']) != 0:
      logger.warn("In if")
      db_words_plus = await db_queries.get_stat_words(campaing_id=campaign.campaign_id, status="Created", types="plus")
      db_words_minus = await db_queries.get_stat_words(campaing_id=campaign.campaign_id, status="Created", types="minus")
      db_switch_fixed = await db_queries.get_stat_words(campaing_id=campaign.campaign_id, status="Created", types="Change")
      
      if db_switch_fixed:
        if db_switch_fixed.word == "On":
          switch = "true"
        else:
          switch = "false"
        
        try:
          await wb_queries.switch_word(user=campaign_user, campaign=campaign, switch=switch)
          await db_queries.change_status_stat_words(campaing_id=campaign.campaign_id, status="Finished", types="Changed")
        except:
          logger.warn("Error, check_stat_word_plus")
      
      if db_words_plus:
        pluse_word = []
        pluse_word = [word for word in words['pluses']]
        for word_plus in db_words_plus:
          pluse_word.append(word_plus.word)
          
        try:
          await wb_queries.add_word(campaign_user, campaign, plus_word=pluse_word)
          await db_queries.change_status_stat_words(campaing_id=campaign.campaign_id, status="Finished", types="plus", words=pluse_word)
        except:
          logger.warn("Error, check_stat_word_plus")
        
      if db_words_minus:
        minus_word = []
        minus_word = [word for word in words['minuses']]

        for word_minus in db_words_minus:
          minus_word.append(word_minus.word)
        
        try:
          await wb_queries.add_word(campaign_user, campaign, excluded_word=minus_word)
          await db_queries.change_status_stat_words(campaing_id=campaign.campaign_id, status="Finished", types="minus", words=minus_word)
        except:
          logger.warn("Error, check_stat_word_minus")
