from wb_common.wb_queries import wb_queries
from ui_backend.common import status_parser

from unittest import mock
import time

from munch import DefaultMunch

class Capaign_processor_functions:

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
      return_string += f"Отслеживается! "
      return_string += f"Перестать отслеживать РК: /delete_adv_{wb_advert_id}"
    else:
      return_string += f"Не отслеживается! "
      return_string += f"Отслеживать РК: /add_adv_{wb_advert_id}"

    return return_string
  
  def get_advert_budget(context, wb_advert_id, **kwargs):
    campaign = mock.Mock()
    campaign.campaign_id = wb_advert_id
    user = context['metadata']['user']
    user_obj = DefaultMunch.fromDict(user)
    res = wb_queries.get_budget(user_obj, campaign)
    return res

  def advert_budget_decorator(context, wb_advert_id, result, **kwargs):
    return f"Бюджет компании {result['Бюджет компании']}"
  
  def get_campaign_name(context, wb_advert_id, **kwargs):
    adverts = context['data']['adverts_from_wb_account']
    adverts_by_id = {x['id']: x for x in adverts}
    res = adverts_by_id.get(int(wb_advert_id))
    return res['campaignName']

  def campaign_name_decorator(context, wb_advert_id, result, **kwargs):
    return result
  
  def get_id_advert(context, wb_advert_id, **kwargs):
    adverts = context['data']['adverts_from_wb_account']
    adverts_by_id = {x['id']: x for x in adverts}
    advert = adverts_by_id.get(int(wb_advert_id))
    return {'wb_advert_id': advert['id'], 'status': status_parser(advert['statusId'])} 

  def id_advert_decorator(context, wb_advert_id, result, **kwargs):
    advert_id = result["wb_advert_id"]
    res = f'ID: [{advert_id}](https://cmp.wildberries.ru/campaigns/list/all/edit/search/{advert_id}) Статус: {result["status"]}'
    return res
  
  def get_settings(context, wb_advert_id, **kwargs):
    return wb_advert_id

  def settings_decorator(context, wb_advert_id, result, **kwargs):
    return f'Настроить РК: /adv_settings_{wb_advert_id}'
  
  def get_analitics_command_str(context, wb_advert_id, **kwargs):
    return f'Получить график аналитики: /user_analitics_grafic_{wb_advert_id}'
  
  def analitics_decorator(context, wb_advert_id, result, **kwargs):
    return result