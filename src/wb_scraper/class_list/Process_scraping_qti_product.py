from collections.abc import Callable, Iterable, Mapping
from datetime import datetime, timedelta
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
from class_list.main_var import Main_var


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
            # print(len(result))
            self.insert_db_info(result)
                

    async def parse_search(self, session, id : str = ""):
        url = f"""https://card.wb.ru/cards/detail?appType=1&curr=rub&dest=-1172839&regions=80,38,83,4,64,33,68,70,30,40,86,69,22,1,31,66,48,114&spp=0&nm={id}"""
        headers = {'user-agent':user_agent.generate_user_agent()}
        async with session.get(url,headers=headers) as response:
            try:
                result = {
                    "id" : id,
                    "date" : (datetime.now()).strftime('%Y-%m-%d'),
                    "size" : []
                }
                if response.status == 500:
                    return
                data = await response.read()
                hashrate = json.loads(data)
                hashrate = hashrate.get('data',{})
                # print(hashrate.get("products",[])[0])
                lst_sizes = []
                product = hashrate.get("products",[]) if (len(hashrate.get("products",[]))!=0) else []
                if len(hashrate.get("products",[]))==0:
                    return
                for val in hashrate.get("products",[])[0].get("sizes",[]):
                    lst_sizes.append(val)
                
                result['size'] = lst_sizes

            except Exception as ex:
                print(ex, 'add parser info')
            finally:
                return result
            
    def insert_db_info (self, res):
        if (res.size == []):
            pass
        