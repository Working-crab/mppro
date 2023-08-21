import clickhouse_driver
from func_catalog.lst_chunk import lst_chunk
from class_list.main_var import Main_var
from class_list.Process_scraping_main_info import Process

def scraping_product_main_info ():
    client = clickhouse_driver.Client.from_url(Main_var.DB_URL)
    lst = client.execute(f"""SELECT DISTINCT id_product FROM product_position""")
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
