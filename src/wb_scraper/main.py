import time
from sys import argv
from scraping.scraping_search_word import scrapping_search_word
from scraping.scraping_product_main_info import  scraping_product_main_info

start = time.time()

script_name = argv[1]

if __name__ == '__main__':
    if script_name == "search_word":
        scrapping_search_word(int(argv[2]),int(argv[3]))
    elif script_name == "scraping_main_info":
        scraping_product_main_info()

print(time.time()-start)
