import clickhouse_driver
from class_list.main_var import Main_var
import pathlib 
import json
from datetime import datetime, timedelta

def add_wh_db():
    with open(f'{pathlib.Path("src/wb_scraper")}/wh.json', "r", encoding='utf-8-sig') as c:
        json_data = json.load(c)
        wh_lst = json_data.get('result',{}).get('resp',{}).get('data',[])

    for i in wh_lst:
        client = clickhouse_driver.Client.from_url(Main_var.DB_URL)
        client.execute(f""" INSERT INTO `default`.warehouse (id, id_wh, name, addres, rating) 
                       VALUES (generateUUIDv4(), {i.get('origid',0)}, '{i.get('warehouse','')}', '{i.get('address','')}', {i.get('rating',0)}); """)

