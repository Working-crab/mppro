
import json
from ui_backend.db.queries import db_queries
from wb_common.wb_queries import wb_queries

class campaign_automation:

  def start():
    campaigns = db_queries.get_adverts_chunk()

    if not campaigns:
      return False
    
    for campaign in campaigns:
      print('campaign')
      print(campaign)
      campaign_automation.check_campaign(campaign)


  def check_campaign(campaign):

    campaign_user = db_queries.get_user_by_id(campaign.user_id)
    campaign_info = wb_queries.get_campaign_info(campaign_user, campaign)
    campaign_pluse_words = wb_queries.get_stat_words(campaign_user, campaign)

    check_word = campaign_info['campaign_key_word']
    if campaign_pluse_words['main_pluse_word']:
      check_word = campaign_pluse_words['main_pluse_word']

    current_bids_table = wb_queries.search_adverts_by_keyword(check_word)

    new_bid = 0
    approximate_place = 0

    for bid in current_bids_table:
      if bid['price'] < campaign.max_budget:
        new_bid = bid['price'] + 1
        bid_p_id = bid['p_id']
        approximate_place = bid['position']
        break

    print(f'check_campaign id: {campaign.id} \t new_bid: {new_bid} \t old_bid: {campaign_info["campaign_bid"]}')

    if new_bid != campaign_info['campaign_bid'] and bid_p_id != campaign.campaign_id:
      wb_queries.set_campaign_bid(campaign_user, campaign, campaign_info, new_bid, approximate_place)


    pass

