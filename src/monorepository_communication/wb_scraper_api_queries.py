import requests
from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)

async def get_csv_statistics_search_words(product_id, start_date, end_date):
  try:
    response = requests.get(f'http://127.0.0.1:8002/csv_statistics_search_words?id_product={product_id}')
    if response.status_code == 200:
      file_path = f"../../temporary_files/{product_id}.csv"
      return {'text': response.text, 'content': response._content}
    else:
      return 'Произошла ошибка'
  except Exception as e:
    return 'Произошла ошибка 1'
