import datetime
import re
import copy

from wb_common.wb_queries import wb_queries
from ui_backend.campaign_info.capaign_processor_field_structure import campaign_field_structure
from ui_backend.campaign_info.capaign_processor_functions import Capaign_processor_functions
from db.queries import db_queries

header_template = 'Список ваших рекламных кампаний с cmp.wildberries.ru, страница: #page_number# \n\n'
campaign_template = '''
Кампания
  #watching_status#
  #budget#
'''
page_size = 6

class Capaign_processor:

  #watching_functionality#
  #watching_data#
  #watching_settings#
  #campaign_data#
  
  # campaign_processing = {
  #   'data': {},
  #   'metadata': {},
  #   'fields': {
  #     'advert_id': {
  #       'watching_status': {
  #         'result_function': 'lambda x: x',
  #         'result_function_args': {},
  #         'decorator_function': 'lambda x: x',
  #         'last_time_update': 'datetime.now().isoformat()',
  #         'retry_count': 0,
  #         'result': ''
  #       },
  #       'watching_functionality': {},
  #       'watching_data': {}
  #     }
  #   },
    
  # }

  def create_campaign_processing(user, page_number):

    campaign_processing = {}
    
    user_wb_tokens = wb_queries.get_base_tokens(user)
    req_params = wb_queries.get_base_request_params(user_wb_tokens)
    user_adverts = wb_queries.get_user_atrevds(req_params, user_id=user.id).get('adverts')
    if not user_adverts:
      return
    
    adverts = []
    if page_number != 1:
      adverts = user_adverts[(page_size*(page_number-1)):page_size*page_number]
    else:
      adverts = user_adverts[page_number-1:page_size]


    campaign_processing['data'] = {}
    lst_adverts_ids = [i['id'] for i in adverts]
    db_adverts = db_queries.get_user_adverts_by_wb_ids(user.id, lst_adverts_ids)
    id_to_db_adverts = {x.campaign_id: x for x in db_adverts}
    campaign_processing['data']['id_to_db_adverts'] = id_to_db_adverts


    campaign_processing['metadata'] = {}
    campaign_processing['metadata']['created_at'] = datetime.datetime.now().isoformat()
    campaign_processing['metadata']['user'] = user


    compaign_fields = re.findall(r'\#(.*?)\#', campaign_template)
    compaign_fields = [i for i in compaign_fields if i != '\n']
    
    campaign_processing['fields'] = {}
    for advert in adverts:
      campaign_processing['fields'][advert['id']] = {}
      for field in compaign_fields:

        campaign_processing['fields'][advert['id']][field] = copy.deepcopy(campaign_field_structure['default'])
        campaign_processing['fields'][advert['id']][field].update(campaign_field_structure[field])

        campaign_processing['fields'][advert['id']][field]['updated_at'] = datetime.datetime.now().isoformat()

    return campaign_processing


  def go_campaign_processing(campaign_processing):

    for advert_id in campaign_processing['fields']:
      for field_key in campaign_processing['fields'][advert_id]:
        field = campaign_processing['fields'][advert_id][field_key]
        function_args = field['result_function_args']
        function_args['context'] = campaign_processing
        function_args['wb_advert_id'] = advert_id

        field['result'] = getattr(Capaign_processor_functions, field['result_function'])(**function_args)
        function_args['result'] = field['result']
        field['result'] = getattr(Capaign_processor_functions, field['decorator_function'])(**function_args)

    return campaign_processing


  def decorate_campaign_processing(campaign_processing):

    template = header_template

    for advert_id in campaign_processing['fields']:
      row_template = campaign_template
      for field_key in campaign_processing['fields'][advert_id]:
        field = campaign_processing['fields'][advert_id][field_key]
        row_template = row_template.replace('#' + field_key + '#', field['result'])
      template += row_template
      
    return template

