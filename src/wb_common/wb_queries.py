
import json
from datetime import datetime
from cache_worker.cache_worker import cache_worker
import requests

CONSTS = {
  'Referer_default': 'https://cmp.wildberries.ru/campaigns/list/all',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.5.715 Yowser/2.5 Safari/537.36'
}


class wb_queries:

  def get_base_tokens(user):
    user_wb_tokens = cache_worker.get_user_wb_tokens(user.id)
    if not user_wb_tokens['wb_cmp_token'] or not user_wb_tokens['wb_user_id'] or not user_wb_tokens['wb_supplier_id']:
      user_wb_tokens = wb_queries.reset_base_tokens(user)

    return user_wb_tokens

  
  def wb_query(method, url, cookies, headers):
    response = requests[method](url, cookies=cookies, headers=headers)
    result = response.json()
    print(f'{datetime.now()} \t wb_query \t url: {url} \t cookies: {str(cookies)} \t headers: {str(headers)} \t result: {str(result)}')
    return result


  def reset_base_tokens(user):

    user_wb_tokens = cache_worker.get_user_wb_tokens(user.id)
    print('cache token', user_wb_tokens['wb_cmp_token'])
    if not user_wb_tokens['wb_cmp_token']:
      user_wb_tokens['wb_cmp_token'] = user.wb_cmp_token
      print('bd token', user_wb_tokens['wb_cmp_token'])

    if not user_wb_tokens['wb_cmp_token']:
      raise Exception('Не найден токен! wb_cmp_token')

    print(f'{datetime.now()} \t reset_base_tokens \t User id: {user.id} \t Old tokens: {str(user_wb_tokens)}')

    cookies = {
      'WBToken': user_wb_tokens['wb_cmp_token'],
    }

    headers = {
      'Referer': CONSTS['Referer_default'],
      'User-Agent': CONSTS['User-Agent']
    }

    print('cookies, headers', cookies, headers)

    introspect_result = requests.get('https://cmp.wildberries.ru/passport/api/v2/auth/introspect', cookies=cookies, headers=headers).json()

    if not introspect_result or not 'sessionID' in introspect_result or not 'userID' in introspect_result:
      cache_worker.delete_user_wb_tokens(user.id)
      print(f'{datetime.now()} \t reset_base_tokens \t introspect error! \t {introspect_result}')
      raise Exception('Не верный токен!')

    user_wb_tokens['wb_cmp_token']  = introspect_result['sessionID']
    user_wb_tokens['wb_user_id']    = introspect_result['userID']

    cookies['WBToken']              = introspect_result['sessionID']
    headers['X-User-Id']            = str(introspect_result['userID'])


    supplierslist_result = requests.get('https://cmp.wildberries.ru/backend/supplierslist', cookies=cookies, headers=headers).json()

    user_wb_tokens['wb_supplier_id'] = supplierslist_result[0]['id']

    cache_worker.set_user_wb_tokens(user.id, user_wb_tokens)

    print(f'{datetime.now()} \t reset_base_tokens \t User id: {user.id} \t New tokens: {str(user_wb_tokens)}')

    return user_wb_tokens


  def search_adverts_by_keyword(keyword):
    res = requests.get(f'https://catalog-ads.wildberries.ru/api/v5/search?keyword={keyword}')
    res = res.json()['adverts'][0:10]

    result = []
    for advert in res:
      result.append({
        "price": advert['cpm'],
        "p_id": advert['id'],
        "position": advert['id']
      })
    return result


  def get_campaign_info(user, campaign):
    user_wb_tokens = wb_queries.get_base_tokens(user)
    custom_referer = f'https://cmp.wildberries.ru/campaigns/list/all/edit/search/{campaign.campaign_id}'
    req_params = wb_queries.get_base_request_params(user_wb_tokens, custom_referer)

    print('get_campaign_info', req_params)

    r = requests.get(f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/placement', 
      cookies=req_params['cookies'],
      headers=req_params['headers']
    ).json()

    campaign_key_word = ''

    if 'place' in r and len(r['place']) > 0:
      campaign_key_word = r['place'][0]['keyWord']
    else:
      campaign_key_word = r['place'][0]['keyWord']

    res = {
      'campaign_id': campaign.campaign_id,
      'campaign_bid': r['place'][0]['price'],
      'campaign_key_word': campaign_key_word,
      'search_elements': r['place'][0]['searchElements']
    }

    return res


  def get_stat_words(user, campaign):
    user_wb_tokens = wb_queries.get_base_tokens(user)
    custom_referer = f'https://cmp.wildberries.ru/campaigns/list/all/edit/search/{campaign.campaign_id}'
    req_params = wb_queries.get_base_request_params(user_wb_tokens, custom_referer)

    print('get_campaign_info', req_params)

    r = requests.get(f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/stat-words', 
      cookies=req_params['cookies'],
      headers=req_params['headers']
    ).json()

    pluses = []
    main_pluse_word = ''

    if 'words' in r and 'pluses' in r['words']:
      pluses = r['words']['pluses']

    if len(pluses) > 0:
      main_pluse_word = pluses[0]

    res = {
      'pluses': pluses,
      'main_pluse_word': main_pluse_word
    }

    return res


  def set_campaign_bid(user, campaign, campaign_info, new_bid, approximate_place):
    user_wb_tokens = wb_queries.get_base_tokens(user)
    custom_referer = f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}'
    req_params = wb_queries.get_base_request_params(user_wb_tokens, custom_referer)
    req_params['headers']['Content-type'] = 'application/json'

    request_body = {
      "place": [
        {
          "keyWord": campaign_info['campaign_key_word'],
          "price": new_bid,
          "searchElements": campaign_info['search_elements']
        }
      ]
    }

    r = requests.put(f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/save',
      cookies=req_params['cookies'],
      headers=req_params['headers'],
      data=json.dumps(request_body)
    ).json()

    print(f'{datetime.now()} \t check_campaign \t Campaign {campaign.campaign_id} updated! \t New bid: {new_bid} \t Approximate place: {approximate_place}')


    return r


  def get_base_request_params(user_wb_tokens, referer=CONSTS['Referer_default']):
    return {
      'cookies': {
        'WBToken': user_wb_tokens['wb_cmp_token'],
        'x-supplier-id-external': str(user_wb_tokens['wb_supplier_id']),
      },
      'headers': {
        'Referer': referer,
        'User-Agent': CONSTS['User-Agent'],
        'X-User-Id': str(user_wb_tokens['wb_user_id']),
      }
    }
    
  def get_user_atrevds(req_params):

    user_atrevds = requests.get('https://cmp.wildberries.ru/backend/api/v3/atrevds?order=createDate', cookies=req_params['cookies'], headers=req_params['headers'])
    view = user_atrevds.json()['content']
    return view

  def get_budget(user, campaign):
    user_wb_tokens = wb_queries.get_base_tokens(user)
    custom_referer = f'https://cmp.wildberries.ru/campaigns/list/all/edit/search/{campaign.campaign_id}'
    req_params = wb_queries.get_base_request_params(user_wb_tokens, custom_referer)

    print('get_campaign_info', req_params)

    r = requests.get(f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/budget',
    cookies=req_params['cookies'],
    headers=req_params['headers']
    ).json()

    total_budget = 0

    if 'total' in r:
      total_budget = int(r['total'])

    res = {
      'Бюджет компании ': total_budget,
    }

    return res