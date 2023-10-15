import pathlib 
import csv
import re
from sys import argv

def reader_csv_file (min, max) :
    with open(f'{pathlib.Path("src/wb_scraper")}/qwe.csv', "r", encoding='utf-8-sig') as c:
    # with open(f'src/wb_scraper/qwe.csv', "r", encoding='utf-8-sig') as c:
        search_words = []
        reader = csv.reader(c)
        for i,r in enumerate(reader):
            if len(re.findall(r"[A-Z a-z а-я А-Я]",r[0])) == 0:
                continue
            if i < min:
                continue
            if i > max:
                break
            search_words.append({
                "id" : r[0],
                "position" : i
            })
        return search_words
    
reader_csv_file(1,10)