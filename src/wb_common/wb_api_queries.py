
import json
from datetime import datetime
from cache_worker.cache_worker import cache_worker
import aiohttp
import asyncio


from common.appLogger import appLogger
from db.queries import db_queries
logger = appLogger.getLogger(__name__)

# TODO переименовать чтобы имя класса совпадало с именем файла
class wb_api_queries:
  async def get_base_tokens(user):
    user_wb_tokens = cache_worker.get_user_wb_tokens(user.id)
    if user.public_api_token:
      user_wb_tokens['public_api_token'] = user.public_api_token
    else:
      user_wb_tokens['public_api_token'] = ""

    return user_wb_tokens

  
  async def wb_query(method, url, cookies=None, headers=None, data=None, req=False, user_id=None):

    result = {}
    try:
      logger.warn(f"{method} url={url}, cookies={cookies}, headers={headers}, data={data}")
      async with aiohttp.ClientSession() as session:
        response = None
        output = {}
        for attempt in range(3):
          async with session.request(method=method, url=url, cookies=cookies, headers=headers, data=data) as response:
            if response.status != 200:
              logger.warn(f"In while {attempt}")
              await asyncio.sleep(4)
              logger.warn(response.status)
            elif response.status == 200:
              if data == "{}":
                return response.headers
              try:
                if not req:
                  output = await response.json()
              except Exception as e:
                  logger.error('result.json() error')
                  if (response.status != 200):
                    raise e
        
        
        if response.status == 401:
          # TODO удалить токен из бд чтобы условие if user.public_api_token: не проходило
          raise Exception('Неверный токен Public API!')
        if response.status == 429:
          raise Exception('Read timed out')
        if response.status == 400:
          logger.warn(response)
          logger.warn(await response.text())
          raise Exception('Произошла ошибка') # TODO Андрей Плохое наименование ошибки
        
    except Exception as e:
      logger.debug({
        'method': method,
        'url': url,
        'cookies': cookies,
        'headers': headers,
        'data': data
      })
      raise Exception("wb_query error " + str(e) + " user_id:" + str(user_id))      
    logger.debug(f'user_id: {user_id} url: {url} \t headers: {str(headers)} \t result: {str(result)}')    
    return output


  async def get_base_request_params(user_wb_tokens):
    return {
      'headers': {
        'Authorization': user_wb_tokens['public_api_token'],
        'Accept': 'application/json'
      }
    }


  async def reset_base_tokens(user):

    user_wb_tokens = cache_worker.get_user_wb_tokens(user.id)
    if not user_wb_tokens['wb_cmp_token']:
      user_wb_tokens['wb_cmp_token'] = user.wb_cmp_token

    if not user_wb_tokens['wb_cmp_token']:
      raise Exception('Не найден токен! wb_cmp_token')

    logger.info(f'{datetime.now()} \t reset_base_tokens \t User id: {user.id} \t Tokens: {str(user_wb_tokens)}')
    
    cache_worker.set_user_wb_tokens(user.id, user_wb_tokens)

    return user_wb_tokens


  # def search_adverts_by_keyword(keyword):
  #   res = wb_api_queries.wb_query(method="get", url=f'https://catalog-ads.wildberries.ru/api/v5/search?keyword={keyword}')
  #   res = res['adverts'][0:10] if res.get('adverts') is not None else []
  #   result = []
  #   for advert in res:
  #     result.append({
  #     "price": advert['cpm'],
  #     "p_id": advert['id'],
  #     "position": advert['id']
  #     })
  #   return result


  async def get_campaign_info(user, campaign):
    user_wb_tokens = await wb_api_queries.get_base_tokens(user)
    request_url = f'https://advert-api.wb.ru/adv/v0/advert?id={campaign.campaign_id}'
    req_params = await wb_api_queries.get_base_request_params(user_wb_tokens)

    result = await wb_api_queries.wb_query(method="get", url=request_url, headers=req_params['headers'])

    if 'params' in result and len(result['params']) == 0:
      raise Exception('wb не вернул данные get_campaign_info')

    res = {
      'campaign_id': campaign.campaign_id,
      'campaign_bid': result['params'][0]['price'],
      'campaign_key_word': result['params'][0]['subjectName'],
      'status': result['status'],
      'full_body': result
    }

    return res


  async def set_campaign_bid(user, campaign, campaign_info, new_bid, old_bid, approximate_place):
    user_wb_tokens = await wb_api_queries.get_base_tokens(user)
    request_url = f'https://advert-api.wb.ru/adv/v0/cpm'
    req_params = await wb_api_queries.get_base_request_params(user_wb_tokens)

    request_body = {
      "advertId": campaign.campaign_id,
      "type": 6,
      "cpm": new_bid,
      "param": 0
    }

    result = await wb_api_queries.wb_query(method="post", url=request_url, headers=req_params['headers'],
      data=json.dumps(request_body)
    )

    log_string = f'{datetime.now()} \t check_campaign wb_api_queries \t Campaign {campaign.campaign_id} updated! \t New bid: {new_bid} \t Old bid: {old_bid} \t Approximate place: {approximate_place}'
    print(log_string)
    await db_queries.add_action_history(
      user_id=user.id,
      action="set_campaign_bid_wb_api_queries",
      action_description=log_string,
      status='success')


    return result


    
  async def get_user_atrevds(user):
    user_wb_tokens = await wb_api_queries.get_base_tokens(user)
    req_params = await wb_api_queries.get_base_request_params(user_wb_tokens)
    
    user_atrevds = await wb_api_queries.wb_query(method="get", url='https://advert-api.wb.ru/adv/v0/adverts?order=create', headers=req_params['headers'], user_id=user.id)
    # view = user_atrevds['content']
    view = {'adverts': user_atrevds['content'], 'total_count': user_atrevds['counts']['totalCount']}
    return view


  async def get_budget(user, campaign):
    user_wb_tokens = await wb_api_queries.get_base_tokens(user)
    # campaign.campaign_id
    # custom_referer = f'https://advert-api.wb.ru/adv/v1/budget'
    req_params = await wb_api_queries.get_base_request_params(user_wb_tokens)

    r = await wb_api_queries.wb_query(method="get", url=f'https://advert-api.wb.ru/adv/v1/budget?id={campaign.campaign_id}',
    headers=req_params['headers'],
    data={'id': campaign.campaing_id},
    user_id=user.id
    )

    total_budget = None

    if 'total' in r:
      total_budget = int(r['total'])

    res = {
      'Бюджет компании': total_budget,
    }

    return res
  
  
  async def switch_status(user, campaign, status):
    user_wb_tokens = await wb_api_queries.get_base_tokens(user)
    req_params = await wb_api_queries.get_base_request_params(user_wb_tokens)
    
    if status == "pause":
      r = await wb_api_queries.wb_query(method='GET', url=f'https://advert-api.wb.ru/adv/v0/pause?id={campaign.campaing_id}',
        headers=req_params['headers'], user_id=user.id)
      
    elif status == "active":
      r = await wb_api_queries.wb_query(method='GET', url=f'https://advert-api.wb.ru/adv/v0/pause?id={campaign.campaing_id}', headers=req_params['headers'])
      
    elif status == "stop":
      r = await wb_api_queries.wb_query(method='GET', url=f'https://advert-api.wb.ru/adv/v0/stop?id={campaign.campaing_id}', headers=req_params['headers'])
    
    return r
  
  
  async def get_stat_words(user, campaign):
    user_wb_tokens = await wb_api_queries.get_base_tokens(user)
    req_params = await wb_api_queries.get_base_request_params(user_wb_tokens)

    print('get_campaign_info', req_params)

    r = await wb_api_queries.wb_query(method='GET', url=f'https://advert-api.wb.ru/adv/v1/stat/words?id={campaign.campaign_id}', 
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
  
  
  async def get_fixed(user, campaign):
    user_wb_tokens = await wb_api_queries.get_base_tokens(user)
    req_params = await wb_api_queries.get_base_request_params(user_wb_tokens)
    

    r = await wb_api_queries.wb_query(method='GET', url=f'https://advert-api.wb.ru/adv/v1/stat/words?id={campaign.campaign_id}', 
      headers=req_params['headers']
    )

    fixed = [] # Status

    if 'words' in r and 'fixed' in r['words']:
      fixed = r['words']['fixed']

    res = {
      'fixed': fixed
    }

    return res


  async def add_word(user, campaign, plus_word=None):
    user_wb_tokens = await wb_api_queries.get_base_tokens(user)
    req_params = await wb_api_queries.get_base_request_params(user_wb_tokens)
    req_params['headers']['Content-type'] = 'application/json'
    
    # plus_word = [plus.lower() for plus in plus_word]
    request_body = {"pluse": plus_word}
    r = await wb_api_queries.wb_query(method='POST', url=f'https://advert-api.wb.ru/adv/v1/search/set-plus?id={campaign.campaign_id}',
    headers=req_params['headers'],
    data=json.dumps(request_body))
    await db_queries.add_action_history(user_id=user.id, action="Добавлено Плюс слово", action_description=f"Было добавлено Плюс слово {plus_word[-1]} в компанию с id {campaign.campaign_id}")


    return r


  async def switch_word(user, campaign, switch):
    user_wb_tokens = await wb_api_queries.get_base_tokens(user)
    req_params = await wb_api_queries.get_base_request_params(user_wb_tokens)
    req_params['headers']['Content-type'] = 'application/json'
    
    r = await wb_api_queries.wb_query(method='GET', url=f'https://advert-api.wb.ru/adv/v1/search/set-plus?id={campaign.campaign_id}&fixed={switch}',
      headers=req_params['headers'],
      req=True
    )
    
    status = "Включены" if switch == "true" else "Выключены"
    await db_queries.add_action_history(user_id=user.id, action=f"Были {status} Фиксированные фразы", action_description=f"Были {status} Фиксированные фразы в компании с id {campaign.campaign_id}")

    return r
  
  
  async def add_budget(user, campaign, budget):
    user_wb_tokens = await wb_api_queries.get_base_tokens(user)
    req_params = await wb_api_queries.get_base_request_params(user_wb_tokens)
    req_params['headers']['Content-type'] = 'application/json'
    
    request_body = {"sum": budget, "type": 1}
    r = await wb_api_queries.wb_query(method='POST', url=f'https://advert-api.wb.ru/adv/v1/budget/deposit?id={campaign.campaign_id}',
    headers=req_params['headers'],
    data=json.dumps(request_body), req=True)
        
    
    # if not r.raise_for_status:
    await db_queries.add_action_history(user_id=user.id, action="Изменен бюджет", action_description=f"Было добавлено {budget} к бюджету в компании с id {campaign.campaign_id}")

    # if not tries:
    #   return error
    return r
  
  
  async def get_user_atrevds(user=None):
    url = f'https://advert-api.wb.ru/adv/v0/adverts?order=createDate'
    
    user_wb_tokens = await wb_api_queries.get_base_tokens(user)
    req_params = await wb_api_queries.get_base_request_params(user_wb_tokens)
    
    user_atrevds = await wb_api_queries.wb_query(method='GET', url=url, headers=req_params['headers'], user_id=user.id)
    # logger.warn("USER_LIST")
    # logger.warn(user_atrevds)
                                       
    logger.warn(user_atrevds)
    view = {'adverts': user_atrevds, 'total_count': len(user_atrevds)}
    return view