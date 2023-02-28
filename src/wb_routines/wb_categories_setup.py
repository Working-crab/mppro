
from datetime import datetime
from wb_common.wb_queries import wb_queries
from cache_worker.cache_worker import cache_worker

class wb_categories_setup:

  def start():
    categories = wb_queries.get_all_categories()

    categories_mapped = {}

    for category_parent in categories:
      categories_mapped[category_parent['id']] = category_parent
      for category in category_parent['childs']:
        categories_mapped[category['id']] = category

    cache_worker.set_wb_categories(categories_mapped)

    print(f'{datetime.now()} Categories set up successful!')

