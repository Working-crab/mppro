
import json
from datetime import datetime
from cache_worker.cache_worker import cache_worker
import aiohttp
import asyncio


from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)

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
          raise Exception('Неверный токен!')
        if response.status == 429:
          raise Exception('Read timed out')
        if response.status == 400:
          raise Exception('Произошла ошибка')
        
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


  def search_adverts_by_keyword(keyword):
    res = wb_api_queries.wb_query(method="get", url=f'https://catalog-ads.wildberries.ru/api/v5/search?keyword={keyword}')
    res = res['adverts'][0:10] if res.get('adverts') is not None else []
    result = []
    for advert in res:
      result.append({
      "price": advert['cpm'],
      "p_id": advert['id'],
      "position": advert['id']
      })
    return result


  def get_campaign_info(user, campaign):
    user_wb_tokens = wb_api_queries.get_base_tokens(user)
    request_url = f'https://advert-api.wb.ru/adv/v0/advert?id={campaign.campaign_id}'
    req_params = wb_api_queries.get_base_request_params(user_wb_tokens)

    result = wb_api_queries.wb_query(method="get", url=request_url, headers=req_params['headers'])

    if 'params' in result and len(result['params']) == 0:
      raise Exception('wb не вернул данные get_campaign_info')

    res = {
      'campaign_id': campaign.campaign_id,
      'campaign_bid': result['params'][0]['price'],
      'campaign_key_word': result['params'][0]['subjectName']
    }

    return res


  def set_campaign_bid(user, campaign, campaign_info, new_bid, approximate_place):
    user_wb_tokens = wb_api_queries.get_base_tokens(user)
    request_url = f'https://advert-api.wb.ru/adv/v0/cpm'
    req_params = wb_api_queries.get_base_request_params(user_wb_tokens)

    request_body = {
      "advertId": campaign.campaign_id,
      "type": 6,
      "cpm": new_bid,
      "param": 0
    }

    result = wb_api_queries.wb_query(method="post", url=request_url, headers=req_params['headers'],
      data=json.dumps(request_body)
    )

    logger.info(f' \t Campaign {campaign.campaign_id} updated! \t New bid: {new_bid} \t Approximate place: {approximate_place}')

    return result


    
  def get_user_atrevds(req_params):

    user_atrevds = wb_api_queries.wb_query(method="get", url='https://cmp.wildberries.ru/backend/api/v3/atrevds?order=createDate', cookies=req_params['cookies'], headers=req_params['headers'])
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
    data={'id': campaign.campaing_id}
    )

    total_budget = None

    if 'total' in r:
      total_budget = int(r['total'])

    res = {
      'Бюджет компании': total_budget,
    }

    return res