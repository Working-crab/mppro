
import redis

redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0, password='eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81', decode_responses=True)

WB_CONSTANTS = {
    'prefix': 'wb',
    'wb_cmp_token': 'WBToken',
    'wb_supplier_id': 'x-supplier-id-external',
    'wb_user_id': 'X-User-Id',
}

def make_wb_key(user_id, wb_token_name):
    return f'{WB_CONSTANTS["prefix"]}_{user_id}_{WB_CONSTANTS[wb_token_name]}'

class cache_worker:

  def get_user_wb_tokens(user_id):

    wb_cmp_token    = redis_client.get(make_wb_key(user_id, 'wb_cmp_token'))
    wb_supplier_id  = redis_client.get(make_wb_key(user_id, 'wb_supplier_id'))
    wb_user_id      = redis_client.get(make_wb_key(user_id, 'wb_user_id'))

    result = {
      'wb_cmp_token': wb_cmp_token,
      'wb_supplier_id': wb_supplier_id,
      'wb_user_id': wb_user_id
    }

    return result


  def set_user_wb_tokens(user_id, user_wb_tokens):
      
      expire = 60 * 60 * 24 * 7 # 7 days
      redis_client.set(make_wb_key(user_id, 'wb_cmp_token'),    user_wb_tokens['wb_cmp_token'],   ex=expire)
      redis_client.set(make_wb_key(user_id, 'wb_supplier_id'),  user_wb_tokens['wb_supplier_id'], ex=expire)
      redis_client.set(make_wb_key(user_id, 'wb_user_id'),      user_wb_tokens['wb_user_id'],     ex=expire)

      return True


  def delete_user_wb_tokens(user_id):
      
      redis_client.delete(make_wb_key(user_id, 'wb_cmp_token'))
      redis_client.delete(make_wb_key(user_id, 'wb_supplier_id'))
      redis_client.delete(make_wb_key(user_id, 'wb_user_id'))

      return True
