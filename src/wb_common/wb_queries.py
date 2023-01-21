
from src.cache_worker.cache_worker import cache_worker
import requests

CONSTS = {
  'Referer': 'https://cmp.wildberries.ru/campaigns/list/all',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.5.715 Yowser/2.5 Safari/537.36'
}


class wb_queries:
  def reset_base_tokens(user):

    user_wb_tokens = cache_worker.get_user_wb_tokens(user.telegram_user_id)
    if not user_wb_tokens['wb_cmp_token']:
      user_wb_tokens['wb_cmp_token'] = user.wb_cmp_token


    cookies = {
      'WBToken': user_wb_tokens['wb_cmp_token'],
    }

    headers = {
      'Referer': CONSTS['Referer'],
      'User-Agent': CONSTS['User-Agent']
    }

    introspect_result = requests.get('https://cmp.wildberries.ru/passport/api/v2/auth/introspect', cookies=cookies, headers=headers).json()

    user_wb_tokens['wb_cmp_token']  = introspect_result['sessionID']
    user_wb_tokens['wb_user_id']    = introspect_result['userID']

    cookies['WBToken']              = introspect_result['sessionID']
    headers['X-User-Id']            = str(introspect_result['userID'])


    supplierslist_result = requests.get('https://cmp.wildberries.ru/backend/supplierslist', cookies=cookies, headers=headers).json()

    user_wb_tokens['wb_supplier_id'] = supplierslist_result[0]['id']

    cache_worker.set_user_wb_tokens(user.telegram_user_id, user_wb_tokens)

    print('reset_base_tokens', str(user_wb_tokens))

    return user_wb_tokens

  def search_adverts_by_keyword(keyword):
    r2 = requests.get(f'https://catalog-ads.wildberries.ru/api/v5/search?keyword={keyword}')
    return r2.json()['adverts']
