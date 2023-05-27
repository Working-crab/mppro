
from db.queries import db_queries
from wb_common.wb_queries import wb_queries
import time
from datetime import datetime
from user_analitics import main as user_analitics
import traceback
from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)

class campaign_automation:

  def start():
    adverts = db_queries.get_adverts_chunk()

    print('============= campaign automation start =============')

    if not adverts:
      return False

    for advert in adverts:
      time.sleep(1)
      print('=== campaign automation ===')
      print(campaign.campaign_id, campaign)

      try:
        campaign_automation.check_campaign(advert)
        campaign_automation.check_stat_word(advert)
        user_analitics.start_logs_analitcs(advert.user_id, advert.campaign_id)
      except Exception as e:
        traceback.print_exc()
        logger.error(f'Exception: {e}.')


  def check_campaign(campaign):

    campaign_user = db_queries.get_user_by_id(campaign.user_id)

    campaign_info = None

    campaign_info = wb_queries.very_try_get_campaign_info(campaign_user, campaign, 5)

    # auto stop checking if not valid
    if campaign_info.get('status') == 'OFF_CAMP':
      db_queries.add_user_advert(campaign.user_id, campaign.campaign_id, None, 'OFF', None)
      return False

    if campaign_info['status'] != 9: # check only active campaigns
      return False

    campaign_pluse_words = wb_queries.get_stat_words(campaign_user, campaign)

    check_word = campaign_info['campaign_key_word']

    # TODO adjust pluse logics
    # if campaign_pluse_words['main_pluse_word']:
    #   check_word = campaign_pluse_words['main_pluse_word']

    current_bids_table = wb_queries.search_adverts_by_keyword(check_word)

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

    logger.info(f'check_campaign id: {campaign.id} \t new_bid: {new_bid} \t old_bid: {old_bid}')

    if new_bid != old_bid and bid_p_id != campaign.campaign_id:

      # emulate full setup
      wb_queries.set_campaign_bid(campaign_user, campaign, campaign_info, new_bid, old_bid, approximate_place)
      wb_queries.get_campaign_info(campaign_user, campaign, False)
      wb_queries.post_get_active(campaign_user, campaign)

    pass


  def check_stat_word(campaign):
    logger.warn(campaign.campaign_id)
    db_words = db_queries.get_stat_words(campaing_id=campaign.campaign_id, status="Created")
    logger.warn(db_words)
    if not db_words:
      return
    campaign_user = db_queries.get_user_by_id(campaign.user_id)
    words = wb_queries.get_stat_words(user=campaign_user, campaign=campaign)
    logger.warn("before if")
    logger.warn(words)
    if len(words['fixed']) != 0:
      logger.warn("In if")
      db_words_plus = db_queries.get_stat_words(campaing_id=campaign.campaign_id, status="Created", types="plus")
      db_words_minus = db_queries.get_stat_words(campaing_id=campaign.campaign_id, status="Created", types="minus")
      db_switch_fixed = db_queries.get_stat_words(campaing_id=campaign.campaign_id, status="Created", types="Change")
      
      if db_switch_fixed:
        if db_switch_fixed.word == "On":
          switch = "true"
        else:
          switch = "false"
        
        try:
          wb_queries.switch_word(user=campaign_user, campaign=campaign, switch=switch)
          db_queries.change_status_stat_words(campaing_id=campaign.campaign_id, status="Finished", types="Changed")
        except:
          logger.warn("Error, check_stat_word_plus")
      
      if db_words_plus:
        pluse_word = []
        pluse_word = [word for word in words['pluses']]
        for word_plus in db_words_plus:
          pluse_word.append(word_plus.word)
          
        try:
          wb_queries.add_word(campaign_user, campaign, plus_word=pluse_word)
          db_queries.change_status_stat_words(campaing_id=campaign.campaign_id, status="Finished", types="plus", words=pluse_word)
        except:
          logger.warn("Error, check_stat_word_plus")
        
      if db_words_minus:
        minus_word = []
        minus_word = [word for word in words['minuses']]

        for word_minus in db_words_minus:
          minus_word.append(word_minus.word)
        
        try:
          wb_queries.add_word(campaign_user, campaign, excluded_word=minus_word)
          db_queries.change_status_stat_words(campaing_id=campaign.campaign_id, status="Finished", types="minus", words=minus_word)
        except:
          logger.warn("Error, check_stat_word_minus")
