from func_catalog.lst_chunk import lst_chunk
from func_catalog.read_csv import reader_csv_file
from class_list.Process_parsing_search_word import Process
import clickhouse_driver
from class_list.main_var import Main_var
from datetime import datetime, timedelta

def scrapping_search_word (min, max):
    count_procces = 2
    prc_list = []
    search_words_list = list(lst_chunk(reader_csv_file(min,max), c_num=count_procces))
    for i in range(count_procces):
        prc = Process(name=f'prc-{i}',search_words=search_words_list[i])
        prc.start()
        prc_list.append(prc)

    for i in prc_list:
        i.join()  
    
    client = clickhouse_driver.Client.from_url(Main_var.DB_URL)
    client.execute(f"""ALTER TABLE product_position DELETE WHERE date_collected < '{(datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d')}' """)