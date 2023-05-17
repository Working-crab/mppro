
import json
from datetime import datetime
from cache_worker.cache_worker import cache_worker
import requests
import time

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
  def get_base_tokens(user, check=False):
    user_wb_tokens = cache_worker.get_user_wb_tokens(user.id)

    user_wb_tokens['wb_cmp_token'] = user.wb_cmp_token
    
    if user.wb_v3_main_token:
      user_wb_tokens['wb_v3_main_token'] = user.wb_v3_main_token
              
    if user.x_supplier_id:
      user_wb_tokens['x_supplier_id'] = user.x_supplier_id
    # if not user_wb_tokens['wb_user_id'] or not user_wb_tokens['wb_supplier_id']:
    #   user_wb_tokens = wb_queries.reset_base_tokens(user)
      
    if check:
      user_wb_tokens = wb_queries.reset_base_tokens(user)

    return user_wb_tokens
  

  def wb_query(method, url, cookies=None, headers=None, data=None, user_id=None, timeout=3, request=False):
    result = None
    result = {}
    try:
      logger.warn(f"{method} url={url}, cookies={cookies}, headers={headers}, data={data}, timeout={timeout}")
      result = requests.request(method=method, url=url, cookies=cookies, headers=headers, data=data, timeout=timeout)
      if result.raise_for_status:
        if result.status_code == 401:
          user = db_queries.get_user_by_telegram_user_id(user_id)
          if user.update_v3_main_token:
            token_update = cache_worker.get_user_session(user_id)['update_v3_main_token']
            difference = datetime.now() - datetime.strptime(token_update, "%Y-%m-%d %H:%M:%S.%f")
            if difference.seconds < 600:
              raise Exception('Неверный токен!')
            else:
              user = db_queries.get_user_by_telegram_user_id(user_id)
              wb_queries.reset_base_tokens(user)
              result = requests.request(method=method, url=url, cookies=cookies, headers=headers, data=data, timeout=timeout)
              if result.raise_for_status:
                raise Exception('Неверный токен!')
          else:
            raise Exception('Неверный токен!')
        attemps = 1    
        while ((result.raise_for_status and result.status_code != 200) and attemps != 3):
          logger.warn(f"In while {attemps}")
          attemps += 1
          result = requests.request(method=method, url=url, cookies=cookies, headers=headers, data=data, timeout=timeout)
          # time.sleep(3)
          logger.warn(result.status_code)
          
      if data == "{}":
        return result.headers
      logger.warn(f"result {result.headers}")
      logger.warn(f"result {result}")
      logger.warn(f"result status code")
      logger.warn(result.status_code)
      if not request:
        result = result.json()
    except Exception as e:
      logger.debug({
        'method': method,
        'url': url,
        'cookies': cookies,
        'headers': headers,
        'data': data
      })
      # logger.error(result, result)
      raise Exception("wb_query error " + str(e))

    logger.debug(f'user_id: {user_id} url: {url} \t headers: {str(headers)} \t result: {str(result)}')    
    

    return result


  def reset_base_tokens(user, token_cmp=None, token_main_v3=None):

    user_wb_tokens = {}
    user_wb_tokens['wb_cmp_token'] = ""
    user_wb_tokens['wb_v3_main_token'] = ""
    
    user_wb_tokens['wb_cmp_token'] = user.wb_cmp_token
    
    logger.warn(user.x_supplier_id)
    
    if user.x_supplier_id != None:
      user_wb_tokens['x_supplier_id'] = user.x_supplier_id
    else:
      raise Exception('x_supplier_id Отсутствует!')

    if user.wb_v3_main_token != None or user.wb_v3_main_token != "":
      user_wb_tokens['wb_v3_main_token'] = user.wb_v3_main_token

      # if token_cmp: TODO
      #   raise Exception("Ошибка установки нового токена")
    
    
    if token_cmp:
      user_wb_tokens['wb_cmp_token'] = token_cmp
      
    if token_main_v3:
      user_wb_tokens['wb_v3_main_token'] = token_main_v3
      
    logger.warn(user_wb_tokens['wb_v3_main_token'])  

    # if not user_wb_tokens['wb_cmp_token']:
    #   raise Exception('Не найден токен! wb_cmp_token')
    

    logger_token.info(f' \t reset_base_tokens \t User id: {user.id} \t Old tokens: {str(user_wb_tokens)}')

    cookies = {
      'WBToken': user_wb_tokens['wb_cmp_token'],
      'WILDAUTHNEW_V3': user_wb_tokens['wb_v3_main_token'],
      'x-supplier-id-external': user_wb_tokens['x_supplier_id'],
    }

    headers = {
      'Referer': CONSTS['Referer_default'],
      'User-Agent': CONSTS['User-Agent'],
    }

    logger_token.warn('cookies, headers', cookies, headers)
    # logger.warn(auth_result)
    # if not user_wb_tokens['wb_cmp_token']:
    
    if user_wb_tokens['wb_v3_main_token']:
      auth_result = wb_queries.wb_query(method='post', url='https://cmp.wildberries.ru/passport/api/v2/auth/wild_v3_upgrade', cookies={'WILDAUTHNEW_V3': user_wb_tokens['wb_v3_main_token']}, data="{}")
      
      if not auth_result or not "Set-Cookie" in auth_result:
        raise Exception('Неверный токен!')
      
      cmp_token = db_queries.get_user_wb_cmp_token(user.telegram_user_id)    
      cookies['WBToken'] = auth_result['Set-Cookie'].replace('WBToken=', '').split(";")[0]
            
      if cmp_token != cookies['WBToken']:
        db_queries.set_user_wb_cmp_token(telegram_user_id=user.telegram_user_id, wb_cmp_token=cookies['WBToken'])
        # if token_cmp:
        #   raise Exception("Ошибка установки нового токена")
    
    logger.warn("COOKIES")
    logger.warn(cookies)
      
    introspect_result = wb_queries.wb_query(method='get', url='https://cmp.wildberries.ru/passport/api/v2/auth/introspect', cookies=cookies, headers=headers)
    
    # introspect_result = introspect.json()
    #   logger_token.info('introspect_result', introspect_result)
    
    if not introspect_result or not 'sessionID' in introspect_result or not 'userID' in introspect_result:
      print(f'{datetime.now()} \t reset_base_tokens \t introspect error! \t {introspect_result}')
      raise Exception('Неверный токен!')

    user_wb_tokens['wb_cmp_token']  = introspect_result['sessionID']
    user_wb_tokens['wb_user_id']    = introspect_result['userID']

    cookies['WBToken']              = introspect_result['sessionID']
    headers['X-User-Id']            = str(introspect_result['userID'])
    logger.warn(introspect_result)

    logger.warn("REQ")
    logger.warn(headers)
    logger.warn(cookies)
    
    supplier_result = wb_queries.wb_query(method="get", url='https://cmp.wildberries.ru/backend/api/v3/supplier', cookies=cookies, headers=headers)
    logger.warn(supplier_result['supplier']['id'])
    user_wb_tokens['wb_supplier_id'] = supplier_result['supplier']['id']
    logger.warn(user_wb_tokens)
    cache_worker.set_user_wb_tokens(user.id, user_wb_tokens)

    # TODO move to mq db microservice
    # db_queries.set_user_wb_cmp_token(telegram_user_id=user.telegram_user_id, wb_cmp_token=user_wb_tokens['wb_cmp_token'])

    logger_token.info(f'\t reset_base_tokens \t User id: {user.id} \t New tokens: {str(user_wb_tokens)}')

    return user_wb_tokens


  def search_adverts_by_keyword(keyword, user_id=None):
    res = wb_queries.wb_query(method="get", url=f'https://catalog-ads.wildberries.ru/api/v5/search?keyword={keyword}', user_id=user_id)
    wb_search_positions = None
    
    # kill me please
    if res and res.get('pages') and res.get('pages')[0] and res.get('pages')[0].get('positions') and len(res.get('pages')[0].get('positions')) > 0:
      wb_search_positions = res.get('pages')[0].get('positions')[0:CONSTS['slice_count']]
    
    res = res['adverts'][0:CONSTS['slice_count']] if res.get('adverts') is not None else []
    result = []
    position = 0
    for advert in res:
      result.append({
        "price": advert['cpm'],
        "p_id": advert['id'],
        "position": position,
        "wb_search_position": wb_search_positions[position]
      })
      position +=1
    return result


  def get_campaign_info(user, campaign, send_exeption=True):
    user_wb_tokens = wb_queries.get_base_tokens(user)
    logger.warn('after_user_wb_tokens')
    custom_referer = f'https://cmp.wildberries.ru/campaigns/list/all/edit/search/{campaign.campaign_id}'
    req_params = wb_queries.get_base_request_params(user_wb_tokens, custom_referer)
    # print('get_campaign_info', req_params)
    r = wb_queries.wb_query(method="get", url=f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/placement', 
      cookies=req_params['cookies'],
      headers=req_params['headers'],
      timeout=10,
    )
    campaign_key_word = ''

    if 'place' in r and len(r['place']) > 0:
      campaign_key_word = r['place'][0]['keyWord']
    elif send_exeption:
      raise Exception('Вайлдберриес не отправил get_campaign_info')
    else:
      return r

    res = {
      'campaign_id': campaign.campaign_id,
      'campaign_bid': r['place'][0]['price'],
      'campaign_key_word': campaign_key_word,
      'search_elements': r['place'][0]['searchElements'],
      'status': r['status'],
      'full_body': r
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
    
    error = "На WB произошла ошибка"
    
    pluses = []
    minuses = []
    fixed = [] # Words
    fixed_status = ''
    main_pluse_word = ''

    if 'words' in r and 'pluse' in r['words']:
      pluses = r['words']['pluse']
    
    if 'words' in r and 'keywords' in r['words']:
      fixed = r['words']['keywords']
      
    if 'words' in r and 'fixed' in r['words']:
      fixed_status = r['words']['fixed']
    
    if 'words' in r and 'excluded' in r['words']:
      minuses = r['words']['excluded']

    if len(pluses) > 0:
      main_pluse_word = pluses[0]

    res = {
      'pluses': pluses,
      'minuses': minuses,
      'main_pluse_word': main_pluse_word,
      'fixed': fixed,
      'fixed_status': fixed_status
    }
    try:
      if r.raise_for_status:
        res['error'] = error
    except:
      pass

    return res
  
  
  def get_fixed(user, campaign):
    user_wb_tokens = wb_queries.get_base_tokens(user)
    custom_referer = f'https://cmp.wildberries.ru/campaigns/list/all/edit/search/{campaign.campaign_id}'
    req_params = wb_queries.get_base_request_params(user_wb_tokens, custom_referer)
    

    r = wb_queries.wb_query(method="get", url=f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/stat-words', 
      cookies=req_params['cookies'],
      headers=req_params['headers']
    )

    fixed = [] # Status

    if 'words' in r and 'fixed' in r['words']:
      fixed = r['words']['fixed']

    res = {
      'fixed': fixed
    }

    return res
  
  
  def add_word(user, campaign, plus_word=None, excluded_word=None):
    user_wb_tokens = wb_queries.get_base_tokens(user)
    custom_referer = f'https://cmp.wildberries.ru/campaigns/list/all/edit/search/{campaign.campaign_id}'
    req_params = wb_queries.get_base_request_params(user_wb_tokens, custom_referer)
    req_params['headers']['Content-type'] = 'application/json'
    
    if excluded_word == None:
      # plus_word = [plus.lower() for plus in plus_word]
      request_body = {"pluse": plus_word}
      r = wb_queries.wb_query(method="post", url=f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/set-plus',
      cookies=req_params['cookies'],
      headers=req_params['headers'],
      data=json.dumps(request_body))
      db_queries.add_action_history(user_id=user.id, action="Добавлено Плюс слово", action_description=f"Было добавлено Плюс слово {plus_word[-1]} в компанию с id {campaign.campaign_id}")
    else:
      # excluded_word = [excluded.lower() for excluded in excluded_word]
      request_body = {
        "excluded": excluded_word
      }
      r = wb_queries.wb_query(method="post", url=f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/set-excluded',
      cookies=req_params['cookies'],
      headers=req_params['headers'],
      data=json.dumps(request_body))
      db_queries.add_action_history(user_id=user.id, action="Добавлено Минус слово", action_description=f"Было добавлено Минус слово {excluded_word[-1]} в компанию с id {campaign.campaign_id}")


    return r
  
  def add_budget(user, campaign, budget):
    user_wb_tokens = wb_queries.get_base_tokens(user)
    custom_referer = f'https://cmp.wildberries.ru/campaigns/list/all/edit/search/{campaign.campaign_id}'
    req_params = wb_queries.get_base_request_params(user_wb_tokens, custom_referer)
    req_params['headers']['Content-type'] = 'application/json'
    
    request_body = {"sum": budget, "type": 1}
    r = wb_queries.wb_query(method="post", url=f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/budget/deposit',
    cookies=req_params['cookies'],
    headers=req_params['headers'],
    data=json.dumps(request_body))
        
    
    # if not r.raise_for_status:
    db_queries.add_action_history(user_id=user.id, action="Изменен бюджет", action_description=f"Было добавлено {budget} к бюджету в компании с id {campaign.campaign_id}")

    # if not tries:
    #   return error
    return r
  
  def switch_status(user, campaign, status):
    user_wb_tokens = wb_queries.get_base_tokens(user)
    custom_referer = f'https://cmp.wildberries.ru/campaigns/list/all/edit/search/{campaign.campaign_id}'
    req_params = wb_queries.get_base_request_params(user_wb_tokens, custom_referer)
    
    
    # req_params['headers']['Content-type'] = 'application/json'
    
    logger.info("PLACE")
    if status == "pause":
      r = wb_queries.wb_query(method="get", url=f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/pause',
        cookies=req_params['cookies'],
        headers=req_params['headers'])
  
    elif status == "active":
      req_params['headers']['Content-type'] = 'application/json'
      full_body = wb_queries.get_campaign_info(user, campaign)
      budget = wb_queries.get_budget(user, campaign)
      
      full_body = full_body['full_body']
      
      full_body["budget"]['total'] = budget['Бюджет компании']
      # full_body["status"] = 9
            
      for places in full_body['place']:
        places["is_active"] = True

      user_wb_tokens = wb_queries.get_base_tokens(user)
      custom_referer = f'https://cmp.wildberries.ru/campaigns/list/all/edit/search/{campaign.campaign_id}'
      req_params = wb_queries.get_base_request_params(user_wb_tokens, custom_referer)
      
      
      r = wb_queries.wb_query(method="put", url=f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/placement',
        cookies=req_params['cookies'],
        headers=req_params['headers'],
        data=json.dumps(full_body))
      

    return r
  

  def switch_word(user, campaign, switch):
    user_wb_tokens = wb_queries.get_base_tokens(user)
    custom_referer = f'https://cmp.wildberries.ru/campaigns/list/all/edit/search/{campaign.campaign_id}'
    req_params = wb_queries.get_base_request_params(user_wb_tokens, custom_referer)
    req_params['headers']['Content-type'] = 'application/json'
    
    r = wb_queries.wb_query(method="get", url=f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/set-plus?fixed={switch}',
      cookies=req_params['cookies'],
      headers=req_params['headers'],
      request=True
    )
    
    status = "Включены" if switch == "true" else "Выключены"
    db_queries.add_action_history(user_id=user.id, action=f"Были {status} Фиксированные фразы", action_description=f"Были {status} Фиксированные фразы в компании с id {campaign.campaign_id}")


    return r


  def set_campaign_bid(user, campaign, campaign_info, new_bid, old_bid, approximate_place):
    user_wb_tokens = wb_queries.get_base_tokens(user)
    custom_referer = f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}'
    req_params = wb_queries.get_base_request_params(user_wb_tokens, custom_referer)
    req_params['headers']['Content-type'] = 'application/json'

    budget = wb_queries.get_budget(user, campaign)

    request_body = campaign_info['full_body']
    request_body['budget']['total'] = budget['Бюджет компании']

    for place in request_body.get('place'):
      place['price'] = new_bid
      place['is_active'] = True

    if not request_body.get('excludedBrands'):
      request_body['excludedBrands'] = []

    # request_body = {
    #   "place": [
    #     {
    #       "keyWord": campaign_info['campaign_key_word'],
    #       "price": new_bid,
    #       "searchElements": campaign_info['search_elements']
    #     }
    #   ]
    # }

    print('request_body')
    print(request_body)

    r = wb_queries.wb_query(method="put", url=f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/save',
      cookies=req_params['cookies'],
      headers=req_params['headers'],
      data=json.dumps(request_body)
    )

    log_string = f'{datetime.now()} \t check_campaign \t Campaign {campaign.campaign_id} updated! \t New bid: {new_bid} \t Old bid: {old_bid} \t Approximate place: {approximate_place}'
    print(log_string)
    db_queries.add_action_history(user_id=user.id, action="set_campaign_bid", action_description=log_string)


    return r


  def get_base_request_params(user_wb_tokens, referer=CONSTS['Referer_default']):
    return {
      'cookies': {
        'WBToken': user_wb_tokens['wb_cmp_token'],
        'x-supplier-id-external': user_wb_tokens['x_supplier_id'],
      },
      'headers': {
        'Referer': referer,
        'User-Agent': CONSTS['User-Agent'],
        'X-User-Id': str(user_wb_tokens['wb_user_id']),
      }
    }
    
# def get_user_atrevds(req_params, page_number=1, pagesize=100):
#     url = f'https://cmp.wildberries.ru/backend/api/v3/atrevds?order=createDate&pageNumber={page_number}&pageSize={pagesize}'
  def get_user_atrevds(req_params, pagesize=50, user_id=None):
    url = f'https://cmp.wildberries.ru/backend/api/v3/atrevds?order=createDate&pageNumber=1&pageSize={pagesize}'
    
    user_atrevds = wb_queries.wb_query(method="get",
                                       url=url,
                                       cookies=req_params['cookies'], headers=req_params['headers'], user_id=user_id)
    logger.warn(user_atrevds)
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

    total_budget = None

    if 'total' in r:
      total_budget = int(r['total'])

    return {'Бюджет компании': total_budget,}


  def get_all_categories():
    return wb_queries.wb_query(method='get', url='https://static-basket-01.wb.ru/vol0/data/subject-base.json')
  
  def get_category_by_id(subjectId):
    categories = cache_worker.get_wb_categories()
    category = categories.get(str(subjectId))

    if not category:
      return {}

    return category
  

  def get_products_info_by_wb_ids(wb_ids, city, user_id=None):

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
  

  def post_get_active(user, campaign):
    user_wb_tokens = wb_queries.get_base_tokens(user)
    custom_referer = f'https://cmp.wildberries.ru/campaigns/list/all/edit/search/{campaign.campaign_id}'
    req_params = wb_queries.get_base_request_params(user_wb_tokens, custom_referer)

    print('post_get_active', req_params)

    res = wb_queries.wb_query(method="post", url=f'https://cmp.wildberries.ru/backend/api/v2/search/{campaign.campaign_id}/get-active', 
      cookies=req_params['cookies'],
      headers=req_params['headers'],
      data=json.dumps({})
    )

    return res

  def very_try_get_campaign_info(user, campaign, tries=5, time_sleep=2):

    result = None
    triesDone = 0

    while (not result or triesDone>=tries):
      triesDone = triesDone + 1
      time.sleep(time_sleep)
      logger.info(f'very_try_get_campaign_info campaign {campaign.campaign_id} user {user.id}')
      result = wb_queries.get_campaign_info(user, campaign, False)

      if type(result) != type({}) and 'Некорректный поставщик' in str(result.text):
        print('*OFF_CAMP Некорректный поставщик*')
        return {'status': 'OFF_CAMP'}

    if not result.get('status'):
      raise Exception(f'Вайлдберриес не отправил very_try_get_campaign_info {tries} tries') 
    
    return result
