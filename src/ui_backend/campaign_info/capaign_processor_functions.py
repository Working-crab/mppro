from wb_common.wb_queries import wb_queries

from unittest import mock

class Capaign_processor_functions:

  def get_processor_function(function_name):
    if function_name in locals():
      return locals()[function_name]

  def default(context, wb_advert_id, **kwargs):
    return 'default value'
  
  def default_decorator(a, **kwargs):
    return str(a)
  
  def get_advert_status(context, wb_advert_id, **kwargs):
    id_to_db_adverts = context['data']['id_to_db_adverts']

    if db_advert := id_to_db_adverts.get(wb_advert_id):
      if db_advert.status == 'ON':
        return True

    return False

  def advert_status_decorator(context, wb_advert_id, result, **kwargs):

    return_string = ''

    if result:
      return_string += f"Отслеживается!"
      return_string += f"Перестать отслеживать РК: /delete_adv_{wb_advert_id}"
    else:
      return_string += f"Не отслеживается!"
      return_string += f"Отслеживать РК: /add_adv_{wb_advert_id}"

    return return_string
  
  def get_advert_budget(context, wb_advert_id, **kwargs):
    campaign = mock.Mock()
    campaign.campaign_id = wb_advert_id
    user = context['metadata']['user']
    res = wb_queries.get_budget(user, campaign)
    return res

  def advert_budget_decorator(context, wb_advert_id, result, **kwargs):
    return f"Бюджет компании {result['Бюджет компании']}"