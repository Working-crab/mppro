from src.wb_scraper.class_list.Process_parsing_search_word import Process
from src.wb_scraper.class_list.main_var import Main_var
from datetime import datetime, timedelta
import clickhouse_driver

from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)

async def scrapping_searching_word_latest(product_id):
    client = clickhouse_driver.Client.from_url(Main_var.DB_URL)
    lst = client.execute(f"""SELECT serarch_word FROM product_position WHERE id_product={product_id}""")
    lst1 = client.execute(f"""SELECT COUNT(serarch_word) FROM product_position WHERE id_product={product_id}""")

    count = lst1[0][0]
    search_words = [item[0] for item in lst]
    
    logger.warn("count", count)
        
    prc = Process(search_words=search_words)
    prc.start()
    
    return f'Process'
    