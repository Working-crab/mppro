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

    def __init__(self, group: None = None, target: Callable[..., object] | None = None, name: str | None = None, args: Iterable[Any] = (), kwargs: Mapping[str, Any] = [], *, daemon: bool | None = None, search_words = []) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.search_words = search_words
        print(len(self.search_words),self.name)
        self.tasks = []
        self.date_collected = time.strftime("%Y-%m-%d")
        self.client = None
        

    async def parser(self):
        self.client = clickhouse_driver.Client.from_url(Main_var.DB_URL)
        async with aiohttp.ClientSession() as session:
            for i2,search_word in enumerate(self.search_words, start=0):
                for i in range(1,3):
                    task = asyncio.create_task(self.parse_search(session, i, search_word))
                    self.tasks.append(task)
                if i2%1000 == 0:
                    result = await asyncio.gather(*self.tasks)
                    th = Thread(target=self.db_insert_info, args=(result,))
                    th.start()
                    self.tasks.clear()
            if len(self.tasks) > 0:
                result = await asyncio.gather(*self.tasks)
                th = Thread(target=self.db_insert_info, args=(result,))
                th.start()
                self.tasks.clear()
                    
    
    async def parse_search(self, session, page, search_word):
        url = f'https://search.wb.ru/exactmatch/ru/common/v4/search?page={page}&resultset=catalog&TestGroup=no_test&TestID=no_test&appType=1&curr=rub&dest=-1257786&query={search_word}&regions=80,38,4,64,83,33,68,70,69,30,86,75,40,1,66,110,22,31,48,71,114&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false'
        headers = {'user-agent':user_agent.generate_user_agent()}
        await asyncio.sleep(random.random())
        async with session.get(url,headers=headers) as response:
            try:
                result_array = []
                if response.status == 500:
                    return
                data = await response.read()
                hashrate = json.loads(data)
                for i in range(len(hashrate.get('data',{}).get('products',''))):
                    result = {
                        "id" : hashrate["data"]["products"][i]["id"],
                        "place" : (page - 1) * 100 + i + 1,
                        "search_word" : search_word
                    }
                    result_array.append(result)
            except Exception as ex:
                print(ex, 'add parser info')
            finally:
                return result_array
            
    def db_insert_info(self, result_scraping):
        try:
            query = "INSERT INTO product_position (id,id_product,`position`,serarch_word,date_collected) SETTINGS async_insert=1,wait_for_async_insert=1 VALUES "
            values_list = []
            for i2 in result_scraping:
                for i in i2:
                    if i["search_word"] != None:
                        values_list.append(f"""(generateUUIDv4(),{i["id"]},{i["place"]},'{i["search_word"].replace("'","''")}','{self.date_collected}')""")
            add_list = []
            for i, value in enumerate(values_list, start=0):
                add_list.append(value)
                if i%100000 == 0 and i>0:
                    print(len(values_list),i,(i/len(values_list))*100)
                    query += ",".join(add_list)
                    self.client.execute(query)
                    query = "INSERT INTO product_position (id,id_product,`position`,serarch_word,date_collected) SETTINGS async_insert=1,wait_for_async_insert=1 VALUES "
                    add_list.clear()
            if len(add_list) > 0 and len(add_list) < 100000:
                query += ",".join(add_list)
                self.client.execute(query)
        except Exception as ex:
            print(ex, 'query')
