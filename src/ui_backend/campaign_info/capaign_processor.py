import datetime
import re
import copy

from kafka_dir.general_publisher import queue_message_async
from kafka_dir.topics import Topics
from wb_common.wb_queries import wb_queries
from ui_backend.campaign_info.capaign_processor_field_structure import campaign_field_structure
from ui_backend.campaign_info.capaign_processor_functions import Capaign_processor_functions
from db.queries import db_queries

header_template = 'Список ваших рекламных кампаний с cmp.wildberries.ru, страница: #page_number# \n'
campaign_template = '''
Кампания: #campaign_name#
  #id_advert#
  #budget#
  #watching_status#
  #settings#
  #analitics#
'''
page_size = 6

class Capaign_processor:

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
    campaign_processing['data']['adverts_from_wb_account'] = adverts


    campaign_processing['metadata'] = {}
    campaign_processing['metadata']['created_at'] = datetime.datetime.now().isoformat()
    campaign_processing['metadata']['user'] = user.as_dict()
    campaign_processing['metadata']['total_count'] = len(user_adverts)
    campaign_processing['metadata']['page_number'] = page_number


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


  async def go_campaign_processing(campaign_processing):

    timer = datetime.timedelta(seconds=3)
    start_time = datetime.datetime.now()
    
    for advert_id in campaign_processing['fields']:
      current_time = datetime.datetime.now()
      if current_time - start_time > timer:
        await queue_message_async(topic=Topics.PROCESSING_CAMPAIGN_TOPIC,
                            campaign_processing=campaign_processing)
        break
      for field_key in campaign_processing['fields'][advert_id]:
        field = campaign_processing['fields'][advert_id][field_key]
        if field['result'] != '':
          continue
        function_args = {}
        function_args.update(field['result_function_args'])
        function_args['context'] = campaign_processing
        function_args['wb_advert_id'] = advert_id

        field['result'] = getattr(Capaign_processor_functions, field['result_function'])(**function_args)
        function_args['result'] = field['result']
        field['result'] = getattr(Capaign_processor_functions, field['decorator_function'])(**function_args)

    message = Capaign_processor.decorate_campaign_processing(campaign_processing)
    chat_id = campaign_processing['metadata']['chat_id']
    message_id = campaign_processing['metadata']['message_id']

    await queue_message_async(topic=Topics.DEFAULT_TOPIC,
                            destination_id=chat_id,
                            message_id=message_id,
                            message=message,
                            edit=True)
    
    return campaign_processing


  def decorate_campaign_processing(campaign_processing):
    page_number = campaign_processing['metadata']['page_number']
    template = header_template.replace('#page_number#', str(page_number))

    for advert_id in campaign_processing['fields']:
      row_template = campaign_template
      for field_key in campaign_processing['fields'][advert_id]:
        field = campaign_processing['fields'][advert_id][field_key]
        row_template = row_template.replace('#' + field_key + '#', field['result'])
      template += row_template
      
    return template

