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
from class_list.main_var import Main_var

class Process(multiprocessing.Process):
    def run(self):
        # asyncio.run(self.parser())
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
                task = asyncio.create_task(self.parse_search(session, product_id))
                self.tasks.append(task)
                

    async def parse_search(self, session, id):
        url = f"""https://basket-01.wb.ru/vo{id[:-5]}/part{id[:-3]}/{id}/info/ru/card.json"""
        headers = {'user-agent':user_agent.generate_user_agent()}
        async with session.get(url,headers=headers) as response:
            try:
                result_array = []
                if response.status == 500:
                    return
                data = await response.read()
                hashrate = json.loads(data)
                print(hashrate.get('selling',{}).get('supplier_id',0))
            except Exception as ex:
                print(ex, 'add parser info')
            finally:
                return result_array