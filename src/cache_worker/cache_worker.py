
import redis
import json

redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0, password='eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81', decode_responses=True)

WB_CONSTANTS = {
    'prefix': 'wb',
    'wb_cmp_token': 'WBToken',
    'wb_v3_main_token': 'wb_v3_main_token',
    'wb_supplier_id': 'x-supplier-id-external',
    'wb_user_id': 'X-User-Id',
    'categories': 'categories'
}

def make_wb_key(user_id, wb_token_name):
  return f'{WB_CONSTANTS["prefix"]}_{user_id}_{WB_CONSTANTS[wb_token_name]}'

def make_general_key(user_id, key_name):
  return f'general_{user_id}_{key_name}'

class cache_worker:

  def get_user_wb_tokens(user_id):

    wb_cmp_token    = redis_client.get(make_wb_key(user_id, 'wb_cmp_token'))
    wb_v3_main_token    = redis_client.get(make_wb_key(user_id, 'wb_v3_main_token'))
    wb_supplier_id  = redis_client.get(make_wb_key(user_id, 'wb_supplier_id'))
    wb_user_id      = redis_client.get(make_wb_key(user_id, 'wb_user_id'))
    # x_supplier_id      = redis_client.get(make_wb_key(user_id, 'x_supplier_id'))

    result = {
      'wb_cmp_token': wb_cmp_token,
      'wb_supplier_id': wb_supplier_id,
      'wb_user_id': wb_user_id,
      'wb_v3_main_token' : wb_v3_main_token,
      # 'x_supplier_id': x_supplier_id
    }

    return result


  def set_user_wb_tokens(user_id, user_wb_tokens):
      
      expire = 60 * 60 * 24 * 7 # 7 days
      if 'wb_cmp_token' in user_wb_tokens and user_wb_tokens["wb_cmp_token"] != None:
        redis_client.set(make_wb_key(user_id, 'wb_cmp_token'),    user_wb_tokens['wb_cmp_token'],   ex=expire)
      if 'wb_v3_main_token' in user_wb_tokens and user_wb_tokens["wb_v3_main_token"] != None:
        redis_client.set(make_wb_key(user_id, 'wb_v3_main_token'),    user_wb_tokens['wb_v3_main_token'],   ex=expire)
      if 'public_api_token' in user_wb_tokens and user_wb_tokens["public_api_token"] != None:
        redis_client.set(make_wb_key(user_id, 'public_api_token'),    user_wb_tokens['public_api_token'],   ex=expire)
      # if 'x_supplier_id' in user_wb_tokens:
      #   redis_client.set(make_wb_key(user_id, 'x_supplier_id'),  user_wb_tokens['x_supplier_id'], ex=expire)
      redis_client.set(make_wb_key(user_id, 'wb_supplier_id'),  user_wb_tokens['wb_supplier_id'], ex=expire)
      redis_client.set(make_wb_key(user_id, 'wb_user_id'),      user_wb_tokens['wb_user_id'],     ex=expire)

      return True


  def delete_user_wb_tokens(user_id):
      
      redis_client.delete(make_wb_key(user_id, 'wb_cmp_token'))
      redis_client.delete(make_wb_key(user_id, 'wb_v3_main_token'))
      redis_client.delete(make_wb_key(user_id, 'wb_supplier_id'))
      redis_client.delete(make_wb_key(user_id, 'wb_user_id'))

      return True
  

  def set_wb_categories(categories):
    redis_client.set(make_wb_key('routine', 'categories'), json.dumps(categories))

  def get_wb_categories():
    return json.loads(redis_client.get(make_wb_key('routine', 'categories')))

  def set_user_session(user_id, session_data):
    key = make_general_key(user_id, 'user_session_key')
    redis_client.set(key, json.dumps(session_data))
    
  def set_action_history_filter(user_id, filter):
    key = make_general_key(user_id, 'action_history_filter')
    redis_client.set(key, json.dumps(filter))
    
    
  # def set_adv_status(campaign_id, new):
  #   key = make_general_key(campaign_id, 'adv_status')
  #   redis_client.set(key, json.dumps(new))
  
  
  # def get_adv_status(campaign_id):
  #   key = make_general_key(campaign_id, 'adv_status')
  #   data = redis_client.get(key)
  #   message = {}
  #   if data:
  #     message = json.loads(data)
  #   return message
  
  
  def get_action_history_filter(user_id):
    key = make_general_key(user_id, 'action_history_filter')
    data = redis_client.get(key)
    message = {}
    if data:
      message = json.loads(data)
    return message

  def get_user_session(user_id):
    key = make_general_key(user_id, 'user_session_key')
    data = redis_client.get(key)
    message = {}
    if data:
      message = json.loads(data)
    return message
  
  def delete_user_session(user_id, key):
    key = make_general_key(user_id, key)
    if redis_client.get(key):
      redis_client.delete(key)
      return True
    else:
      return False

  
  def set_user_dev_mode(user_id):
    redis_client.set(f'dev-{user_id}', user_id)
    
  def get_user_dev_mode(user_id):
    if redis_client.get(f'dev-{user_id}'):
      dev_mode = redis_client.get(f"dev-{user_id}")
      return dev_mode
    else:
      return None
      
  def delete_user_dev_mode(user_id):
    successful = False
    if redis_client.get(f'dev-{user_id}'):
      redis_client.delete(f"dev-{user_id}")
      successful = True
      return successful
    else:
      return successful