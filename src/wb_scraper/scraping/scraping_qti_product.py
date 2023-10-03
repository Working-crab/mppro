from func_catalog.lst_chunk import lst_chunk
from func_catalog.read_csv import reader_csv_file
import clickhouse_driver
from class_list.main_var import Main_var
from datetime import datetime, timedelta
from class_list.Process_scraping_qti_product import Process

def scraping_qti_product ():
    
    client = clickhouse_driver.Client.from_url(Main_var.DB_URL)
    lst = client.execute(f"""SELECT DISTINCT id_product from product_position WHERE date_collected < '{(datetime.now()).strftime('%Y-%m-%d')}' """)
    lst_id = []
    for val in lst:
        lst_id.append(val[0])

    lst_procces_product = list(lst_chunk(lst_id, c_num=2))
    prc_list=[]

    for i in range(2):
        prc = Process(name=f'prc-{i}',id_product=lst_procces_product[i])
        prc.start()
        prc_list.append(prc)

    for i in prc_list:
        i.join()  