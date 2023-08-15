
import asyncio
from db.queries import db_queries
from wb_common.wb_queries import wb_queries
from wb_common.wb_api_queries import wb_api_queries
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

      try:
        await campaign_automation.check_campaign(advert)
        await campaign_automation.check_stat_word(advert)
        await user_analitics.start_logs_analitcs(advert.user_id, advert.campaign_id)
      except Exception as e:
        await db_queries.add_action_history(
          user_id=advert.user_id,
          action="campaign_scan",
          action_description=f'check_campaign id: {advert.campaign_id} Exception: {e}',
          status="error")
        traceback.print_exc()
        logger.error(f'Exception: {e}.')


  async def check_campaign(campaign):

    campaign_user = await db_queries.get_user_by_id(campaign.user_id)

    campaign_info = None

    # campaign_info = await wb_queries.very_try_get_campaign_info(campaign_user, campaign, 5)
    campaign_info = None
    if campaign_user.public_api_token:
      campaign_info = await wb_api_queries.get_campaign_info(campaign_user, campaign)
    else:
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

    campaign_strategy = 'strategy_combined'
    if campaign.strategy:
      campaign_strategy = campaign.strategy

    new_bid = 0
    approximate_place = 0
    new_bid_campaign_id = 0

    off_the_campaign = False

    campaign_places = campaign.place.split('-') # example 2-4
    max_place = 1
    min_place = float('inf')
    if len(campaign_places) > 0:
      if campaign_places[0]:
        max_place = campaign_places[0]
      if len(campaign_places) > 1:
        min_place = campaign_places[1]

    for bid in current_bids_table:
      new_bid = bid['price'] + 1
      new_bid_campaign_id = bid['p_id']
      approximate_place = bid['position']

      # campaign strategy checking
      if 'strategy_hold_the_position' in campaign_strategy:
        if float(bid['position']) >= float(campaign.place):
          break

      elif 'strategy_hold_the_bid' in campaign_strategy:
        if float(bid['price']) < float(campaign.max_bid):
          break

      elif 'strategy_combined' in campaign_strategy:
        if float(bid['position']) < float(max_place):
          continue

        if float(bid['position']) > float(min_place):
          if not 'always_online' in campaign_strategy:
            off_the_campaign = True
            break

        if bid['price'] < campaign.max_bid:
          break

        

    old_bid = campaign_info["campaign_bid"]

    await db_queries.add_action_history(
      user_id=campaign.user_id,
      action="campaign_scan",
      action_description=f'check_campaign id: {campaign.id} \t new_bid: {new_bid} \t old_bid: {old_bid} \t off_the_campaign: {off_the_campaign}',
      status="info")


    if off_the_campaign:
      await wb_queries.off_the_campaign(campaign_user, campaign)


    # check if need to update bid
    if new_bid != old_bid and new_bid_campaign_id != campaign.campaign_id:

      if campaign_user.public_api_token:
        await wb_api_queries.set_campaign_bid(campaign_user, campaign, campaign_info, new_bid, old_bid, approximate_place)
    
      # check if bid is updated
      campaign_info_check = await wb_api_queries.get_campaign_info(campaign_user, campaign)
      if campaign_info_check["campaign_bid"] == old_bid:
        # emulate full setup
        campaign_info_full = await wb_queries.get_campaign_info(campaign_user, campaign, False)
        await wb_queries.set_campaign_bid(campaign_user, campaign, campaign_info_full, new_bid, old_bid, approximate_place, use_public_api = False)
        await wb_queries.post_get_active(campaign_user, campaign)
      


  async def check_stat_word(campaign):
    logger.warn(campaign.campaign_id)
    db_words = await db_queries.get_stat_words(campaing_id=campaign.campaign_id, status="Created")
    logger.warn(db_words)
    if not db_words:
      return
    campaign_user = await db_queries.get_user_by_id(campaign.user_id)
    if campaign_user.public_api_token:
      words = await wb_api_queries.get_stat_words(user=campaign_user, campaign=campaign)
    else:
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
