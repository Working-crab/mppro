
import json
from db.queries import db_queries
from wb_common.wb_queries import wb_queries

class analitics_automation:

  def start(user_id,campaign_id):
    user = db_queries.get_user_by_id(user_id)
    campaign_popa = db_queries.get_campaign_by_user_id_and_campaign_id(user.id, campaign_id)
    total_budget = wb_queries.get_budget(user, campaign_popa)
    print(total_budget)
