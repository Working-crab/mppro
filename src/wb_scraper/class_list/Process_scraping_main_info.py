from collections.abc import Callable, Iterable, Mapping
import json
from typing import Any
import aiohttp
import asyncio
import time
import multiprocessing
import user_agent
import clickhouse_driver
import random
from threading import Thread
from src.wb_scraper.class_list.main_var import Main_var

class Process(multiprocessing.Process):
    def run(self):
        asyncio.run(self.parser())
        pass

    def __init__(self, group: None = None, target: Callable[..., object] | None = None, name: str | None = None, args: Iterable[Any] = (), kwargs: Mapping[str, Any] = [], *, daemon: bool | None = None, id_product = []) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.id_product_list = id_product
        print(len(self.id_product_list),self.name)
        self.client = clickhouse_driver.Client.from_url(Main_var.DB_URL)
        self.tasks = []

    async def parser (self):
        async with aiohttp.ClientSession() as session:
            for i2,product_id in enumerate(self.id_product_list, start=0):
                task = asyncio.create_task(self.parse_search(session, str(product_id)))
                self.tasks.append(task)
            result = await asyncio.gather(*self.tasks)
                

    async def parse_search(self, session, id : str = ""):
        # Переписать код на этот json, хз как, но надо
        # url = f"""https://basket-01.wb.ru/vol{id[:-5]}/part{id[:-3]}/{id}/info/ru/card.json"""
        # print(url)
        url = f"""https://card.wb.ru/cards/detail?appType=1&curr=rub&regions=80,38,83,4,64,33,68,70,30,40,86,75,69,1,31,66,22,110,48,71,114&spp=0&nm={id}"""
        headers = {'user-agent':user_agent.generate_user_agent()}
        async with session.get(url,headers=headers) as response:
            try:
                if response.status == 500:
                    return
                data = await response.read()
                hashrate = json.loads(data)
                result = {
                    'name' : hashrate.get('data',{}).get('products',[{}])[0].get('name','Error'),
                    'id' : hashrate.get('data',{}).get('products',[{}])[0].get('id',0),
                    'id_brand' : hashrate.get('data',{}).get('products',[{}])[0].get('brandId',0)
                }
                if result['id'] == 0 or result['id_brand'] == 0:
                    return 
                self.client.execute(f"""INSERT INTO product (id,name,`desc`,id_brand) SETTINGS async_insert=1,wait_for_async_insert=1 VALUES ({int(result['id'])},'{result['name']}','',{int(result['id_brand'])})""")

            except Exception as ex:
                print(ex, 'add parser info')
            finally:
                return