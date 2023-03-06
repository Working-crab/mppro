
import json
from datetime import datetime
from cache_worker.cache_worker import cache_worker
import requests

from db.queries import db_queries

from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)
logger_token = appLogger.getLogger(__name__+'_token')

CONSTS = {
  'Referer_default': 'https://cmp.wildberries.ru/campaigns/list/all',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.5.715 Yowser/2.5 Safari/537.36',
  'slice_count': 10
}

class wb_queries:
  def get_base_tokens(user):
    user_wb_tokens = cache_worker.get_user_wb_tokens(user.id)
    user_wb_tokens['wb_cmp_token'] = user.wb_cmp_token
    # if not user_wb_tokens['wb_user_id'] or not user_wb_tokens['wb_supplier_id']:
      # user_wb_tokens = wb_queries.reset_base_tokens(user)

    user_wb_tokens = wb_queries.reset_base_tokens(user)

    return user_wb_tokens

  
  def wb_query(method, url, cookies=None, headers=None, data=None, user_id=None):
    result = {}
    try:
      response = requests.request(method=method, url=url, cookies=cookies, headers=headers, data=data)
      result = response.json()
    except Exception as e:
      logger.error(e)

    logger.debug(f'user_id: {user_id} url: {url} \t headers: {str(headers)} \t result: {str(result)}')

    return result


  def reset_base_tokens(user, token=None):

    user_wb_tokens = {}

    user_wb_tokens['wb_cmp_token'] = user.wb_cmp_token

    if token:
      user_wb_tokens['wb_cmp_token'] = token

    if not user_wb_tokens['wb_cmp_token']:
      raise Exception('Не найден токен! wb_cmp_token')

    logger_token.info(f' \t reset_base_tokens \t User id: {user.id} \t Old tokens: {str(user_wb_tokens)}')

    cookies = {
      'WBToken': user_wb_tokens['wb_cmp_token'],
    }

    headers = {
      'Referer': CONSTS['Referer_default'],
      'User-Agent': CONSTS['User-Agent']
    }

    logger_token.info('cookies, headers', cookies, headers)
    
    introspect_result = wb_queries.wb_query(method='get', url='https://cmp.wildberries.ru/passport/api/v2/auth/introspect', cookies=cookies, headers=headers)

    logger_token.info('introspect_result', introspect_result)

    if not introspect_result or not 'sessionID' in introspect_result or not 'userID' in introspect_result:
      print(f'{datetime.now()} \t reset_base_tokens \t introspect error! \t {introspect_result}')
      raise Exception('Неверный токен!')

    user_wb_tokens['wb_cmp_token']  = introspect_result['sessionID']
    user_wb_tokens['wb_user_id']    = introspect_result['userID']

    cookies['WBToken']              = introspect_result['sessionID']
    headers['X-User-Id']            = str(introspect_result['userID'])


    supplierslist_result = wb_queries.wb_query(method="get", url='https://cmp.wildberries.ru/backend/supplierslist', cookies=cookies, headers=headers)

    user_wb_tokens['wb_supplier_id'] = supplierslist_result[0]['id']

    cache_worker.set_user_wb_tokens(user.id, user_wb_tokens)

    # TODO move to mq db microservice
    db_queries.set_user_wb_cmp_token(telegram_user_id=user.telegram_user_id, wb_cmp_token=user_wb_tokens['wb_cmp_token'])

    logger_token.info(f'\t reset_base_tokens \t User id: {user.id} \t New tokens: {str(user_wb_tokens)}')

    return user_wb_tokens


  def search_adverts_by_keyword(keyword, user_id=None):
    res = wb_queries.wb_query(method="get", url=f'https://catalog-ads.wildberries.ru/api/v5/search?keyword={keyword}', user_id=user_id)
    res = res['adverts'][0:CONSTS['slice_count']] if res.get('adverts') is not None else []
    result = []
    position = 0
    for advert in res:
      position += 1
      result.append({
      "price": advert['cpm'],
      "p_id": advert['id'],
      "position": position
      })
    return result


  def get_campaign_info(user, campaign):
    user_wb_tokens = wb_queries.get_base_tokens(user)
    custom_referer = f'https://cmp.wildberries.ru/campaigns/list/all/edit/search/{campaign.campaign_id}'
    req_params = wb_queries.get_base_request_params(user_wb_tokens, custom_referer)

    print('get_campaign_info', req_params)

    r = wb_queries.wb_query(method="get", url=f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/placement', 
      cookies=req_params['cookies'],
      headers=req_params['headers']
    )

    campaign_key_word = ''

    if 'place' in r and len(r['place']) > 0:
      campaign_key_word = r['place'][0]['keyWord']
    else:
      raise Exception('Вайлдберриес не отправил get_campaign_info')

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

    r = wb_queries.wb_query(method="get", url=f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/stat-words', 
      cookies=req_params['cookies'],
      headers=req_params['headers']
    )

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


  def set_campaign_bid(user, campaign, campaign_info, new_bid, old_bid, approximate_place):
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

    r = wb_queries.wb_query(method="put", url=f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/save',
      cookies=req_params['cookies'],
      headers=req_params['headers'],
      data=json.dumps(request_body)
    )

    log_string = f'{datetime.now()} \t check_campaign \t Campaign {campaign.campaign_id} updated! \t New bid: {new_bid} \t Old bid: {old_bid} \t Approximate place: {approximate_place}'
    print(log_string)
    db_queries.add_action_history(user_id=user.id, action=log_string)


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
    
  def get_user_atrevds(req_params, page_number=1, pagesize=6):
    url = f'https://cmp.wildberries.ru/backend/api/v3/atrevds?order=createDate&pageNumber={page_number}&pageSize={pagesize}'
    
    user_atrevds = wb_queries.wb_query(method="get",
                                       url=url,
                                       cookies=req_params['cookies'], headers=req_params['headers'])
    view = {'adverts': user_atrevds['content'], 'total_count': user_atrevds['counts']['totalCount']}
    return view

  def get_budget(user, campaign):
    user_wb_tokens = wb_queries.get_base_tokens(user)
    custom_referer = f'https://cmp.wildberries.ru/campaigns/list/all/edit/search/{campaign.campaign_id}'
    req_params = wb_queries.get_base_request_params(user_wb_tokens, custom_referer)

    print('get_campaign_info', req_params)

    r = wb_queries.wb_query(method="get", url=f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/budget',
    cookies=req_params['cookies'],
    headers=req_params['headers']
    )

    total_budget = 0

    if 'total' in r:
      total_budget = int(r['total'])

    res = {
      'Бюджет компании ': total_budget,
    }

    return res


  def get_all_categories():
    return wb_queries.wb_query(method='get', url='https://static-basket-01.wb.ru/vol0/data/subject-base.json')
  
  def get_category_by_id(subjectId):
    categories = cache_worker.get_wb_categories()
    category = categories.get(str(subjectId))

    if not category:
      return {}

    return category
  

  def get_products_info_by_wb_ids(wb_ids, city, user_id):

    # default_query = f'https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1257786&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&query={keyword}&reg=0&regions=80,64,38,4,83,33,68,70,69,30,86,75,40,1,22,66,31,48,110,71&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false'
    nm_parameter = ';'.join(wb_ids)
    # Запрос для Москвы
    if city == "Москва":
      query = f'https://card.wb.ru/cards/list?spp=0&regions=80,64,38,4,83,33,68,70,69,30,86,75,40,1,22,66,31,48,110,71&pricemarginCoeff=1.0&reg=0&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=12,3,18,15,21&dest=-1257786&nm={nm_parameter}'
    # Запрос Казань
    if city == "Казань":
      query= f'https://card.wb.ru/cards/list?spp=0&regions=80,64,38,4,83,33,68,70,69,30,86,40,1,22,66,31,48,110&pricemarginCoeff=1.0&reg=0&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=2,12,7,3,6,18,22,21&dest=-2133461&nm={nm_parameter}'
    # Запрос Краснодар
    if city == "Краснодар":
      query = f'https://card.wb.ru/cards/list?spp=0&regions=80,64,38,4,83,33,68,70,69,30,86,40,1,22,66,31,48,110&pricemarginCoeff=1.0&reg=0&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=2,7,3,6,19,21,8&dest=12358075&nm={nm_parameter}'
    # Запрос Питер
    if "Санкт" in city:
      query = f'https://card.wb.ru/cards/list?spp=0&regions=80,64,38,4,83,33,68,70,69,30,86,40,1,22,66,31,48&pricemarginCoeff=1.0&reg=0&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=12,7,3,6,5,18,21&dest=-1181032&nm={nm_parameter}'
      
    res = wb_queries.wb_query(method="get", url=query, user_id=user_id)

    if not res.get('data') or not res['data'].get('products') or not len(res['data']['products']):
      return {}
    
    products = res['data']['products'][0:CONSTS['slice_count']]
    result = {}
    for product in products:
      if not product.get('id'):
        continue
      result[product['id']] = {
        'id': product['id'],
        'name': product.get('name'),
        'time1': product.get('time1'),
        'time2': product.get('time2'),
        'subjectId': product.get('subjectId'),
        'subjectParentId': product.get('subjectParentId'),
        'category_name': wb_queries.get_category_by_id(product.get('subjectId')).get('name'),
      }

    return result
  