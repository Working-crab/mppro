import csv
import math
import re
import time
import pathlib 
from class_list.Process_parsing import Process

start = time.time()
prc_list = []
count_procces = 2
MIN_POSITION_SCRAPER = 0
MAX_POSITION_SCRAPER = 20000

def array_chunk (lst, c_num):
    n = math.ceil(len(lst) / c_num)

    for x in range(0, len(lst), n):
        e_c = lst[x : n + x]

        if len(e_c) < n:
            e_c = e_c + [None for y in range(n - len(e_c))]
        yield e_c

def reader_csv_file () :
    with open(f'{pathlib.Path("/data/src/wb_scraper")}/qwe.csv', "r", encoding='utf-8-sig') as c:
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
            if i > MAX_POSITION_SCRAPER:
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
