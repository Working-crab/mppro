import requests

async def get_csv_statistics_search_words(product_id):
  response = requests.get(f'http://127.0.0.1:8005/csv_statistics_search_words?id_product={product_id}')
  if response.status_code == 200:
    file_path = f"../../temporary_files/{product_id}.csv"
    return {'text': response.text, 'content': response._content}
  else:
    return 'Произошла ошибка'
