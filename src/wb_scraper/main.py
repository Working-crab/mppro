from collections.abc import Callable, Iterable, Mapping
import json
from typing import Any
import aiohttp
import asyncio
import csv
import math
import re
import time
import asyncpg
import multiprocessing
import user_agent
import random
import pathlib

start = time.time()
prc_list = []
count_procces = 4
MIN_POSITION_SCRAPER = 0
MAX_POSITION_SCRAPER = 80000

class Process(multiprocessing.Process):
    def run(self):
        asyncio.run(self.parser())

    def __init__(self, group: None = None, target: Callable[..., object] | None = None, name: str | None = None, args: Iterable[Any] = (), kwargs: Mapping[str, Any] = [], *, daemon: bool | None = None, search_words = []) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.search_words = search_words
        self.tasks = []
        self.date_collected = time.strftime("%d/%m/%Y")
        self.db_pool = None
        

    async def parser(self):
        self.db_pool = await asyncpg.create_pool("postgresql://postgres:postgres@localhost/postgres")
        async with aiohttp.ClientSession() as session:
            i = 0
            for search_word in self.search_words:
                i+=1
                print(f'Парсинг результатов на слово \"{search_word}\" {i/len(self.search_words)}%')
                for i in range(1,3):
                    task = asyncio.create_task(self.parse_search(session, i, search_word))
                    self.tasks.append(task)
                # await asyncio.gather(*self.tasks)
            await self.db_insert_info(await asyncio.gather(*self.tasks))
    
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
                    result={}
                    id = hashrate["data"]["products"][i]["id"]
                    result['id'] = id
                    result['place'] = (page - 1) * 100 + i + 1
                    result['search_word'] = search_word
                    result_array.append(result)
            except Exception as ex:
                print(ex, 'add parser info')
                await asyncio.sleep(10)
            finally:
                return result_array
    
    async def db_insert_info(self, info):
        values_list = []
        query = "INSERT INTO wbscraper_product_position (id_product, \"position\", serarch_word, date_collected) VALUES "
        chunk = 0
        try:
            for i2 in info:
                for i in i2:
                    s = i["search_word"].replace("'","''")
                    values_list.append(f'({i["id"]},{i["place"]},\'{s}\',TO_DATE(\'{self.date_collected}\', \'DD/MM/YYYY\'))')
                    chunk+=1
                if (chunk >= 2000):
                    query += ','.join(values_list)
                    print(f'В базу добавлется {chunk} строк')
                    await self.db_pool.fetch(query)
                    values_list.clear()
                    query = "INSERT INTO wbscraper_product_position (id_product, \"position\", serarch_word, date_collected) VALUES "
                    chunk = 0
        except Exception as ex:
            print(ex, 'query')
        finally:
            pass
        

def array_chunk (lst, c_num):
    n = math.ceil(len(lst) / c_num)

    for x in range(0, len(lst), n):
        e_c = lst[x : n + x]

        if len(e_c) < n:
            e_c = e_c + [None for y in range(n - len(e_c))]
        yield e_c

def reader_csv_file () :
    with open(f'{pathlib.Path("/data","src","wb_scraper")}/qwe.csv', "r", encoding='utf-8-sig') as c:
        search_words = []
        reader = csv.reader(c)
        i = 0
        for r in reader:
            i+=1
            searchWord = r[0]
            regexp = re.findall(r"[A-Z a-z а-я А-Я]",searchWord)
            if len(regexp) == 0:
                continue
            if i < MIN_POSITION_SCRAPER:
                continue
            if i >= MAX_POSITION_SCRAPER:
                break
            search_words.append(searchWord)
        return search_words

if __name__ == '__main__':
    search_words_list = list(array_chunk(reader_csv_file(), c_num=count_procces))
    for i in range(count_procces):
        prc = Process(name=f'prc-{i}',search_words=search_words_list[i])
        prc.start()
        prc_list.append(prc)

for i in prc_list:
    i.join()

print(time.time()-start)
