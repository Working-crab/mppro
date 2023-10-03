from src.wb_scraper.class_list.Process_parsing_search_word import Process
from src.wb_scraper.class_list.main_var import Main_var
from datetime import datetime, timedelta
import clickhouse_driver

def scrapping_searching_word_latest(product_id):
    client = clickhouse_driver.Client.from_url(Main_var.DB_URL)
    lst = client.execute(f"""SELECT serarch_word FROM product_position WHERE id_product={product_id}""")
    
    search_words = [item[0] for item in lst]
        
    prc = Process(search_words=search_words)
    prc.start()
    
    return f'Process'
    