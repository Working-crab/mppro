
from src.ui_backend.db.queries import db_queries
from src.wb_common.wb_queries import wb_queries

class campaign_automation:

  def start():
    campaigns = db_queries.get_adverts_chunk()
    for campaign in campaigns:
      if campaign.status == 'ON':
        campaign_automation.check_campaign(campaign)


  def check_campaign(campaign):

    # TODO add place

    campaign_user = db_queries.get_user_by_id(campaign.user_id)
    current_budget = wb_queries.get_campaign_budget(campaign_user, campaign)
    campaign_world = wb_queries.get_campaign_world(campaign_user, campaign)
    current_bids_table = wb_queries.get_campaign_bids_table(campaign_world)

    new_bid = 0

    for bid in current_bids_table:
      if bid['bid'] < campaign.max_budget:
        new_bid = bid['bid'] + 1
        break


    if new_bid != current_budget:
      wb_queries.set_campaign_budget(campaign_user, campaign, new_bid)
      print(f'check_campaign Кампания {campaign.id} была изменена. Новый бюджет: {new_bid}')



    pass

