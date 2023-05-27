import json
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

from db.queries import db_queries
from wb_common.wb_queries import wb_queries

class graphics_analitics:
    def start(user_id, campaign_id):
        data_list = db_queries.get_user_analitics_data(user_id, campaign_id)
        #даты
        index_ox = []
        max_bid = []
        spent_money = []
        up_money = []
        for obj in data_list:
            index_ox.append(obj.date_time)
            max_bid.append(obj.max_bid_company)
            spent_money.append(obj.current_bet)
            up_money.append(obj.economy)

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        #формирование графика
        df = pd.DataFrame({
                    'Максимальная ставка': max_bid,
                    'Потрачено на рекламу': spent_money,
                    'Экономия': up_money
                }, index=index_ox)
        axes = df.plot.bar(rot=0, subplots=True, figsize=(11, 11))
        plt.savefig(f"user_analitics_image/{campaign_id}.png")     
        return f"user_analitics_image/{campaign_id}.png"
    
    def delete_photo(path):
        try:
            os.remove(path)
        except Exception:
            pass