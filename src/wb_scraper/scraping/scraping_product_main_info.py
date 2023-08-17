import clickhouse_driver
from class_list.main_var import Main_var

def scraping_product_main_info ():
    client = clickhouse_driver.Client.from_url(Main_var.DB_URL)
    client.execute(f"""	SELECT DISTINCT id_product FROM product_position;""")
