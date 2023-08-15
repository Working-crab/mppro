import requests

async def get_csv_statistics_search_words(product_id):
  result = requests.get(f'http://127.0.0.1:8005/csv_statistics_search_words?id_product={product_id}')
  if result.status_code == 200:
    return result.text
  else:
    return 'Произошла ошибка'
