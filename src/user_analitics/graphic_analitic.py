import json
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import numpy as np

from db.queries import db_queries
from wb_common.wb_queries import wb_queries

class graphics_analitics:
    def start(user_id, campaign_id):
        data_list = db_queries.get_user_analitics_data(user_id, campaign_id)

        index_ox = []
        max_bid = []
        current_bet = []
        budget = []

        for obj in data_list:
            budget.append(obj.max_budget_company)
            index_ox.append(obj.date_time)
            max_bid.append(obj.max_bid_company)
            current_bet.append(obj.current_bet)

        data = {'bid':current_bet, 'budget':budget, 'max_bid':max_bid, 'data_index': index_ox}
        df = pd.DataFrame(data)
    
        df['spending'] = (-df['budget'].diff()).fillna(0).astype(int)
        df['views_10k'] = df['spending'] / df['bid']
        df['economy_im'] = df['max_bid'] - df['bid']
        df['economy_real'] = df['economy_im'] * df['views_10k']
        df2 = df[df['spending'] >= 0].reset_index(drop=True)

        #формирование графика
        df3 = pd.DataFrame({
                    'Максимальная ставка': list(df2['max_bid']),
                    'Потрачено на рекламу': list(df2['spending']),
                    'Экономия': list(df2['economy_real'])
                }, index=df2['data_index'])

        df3_grouped = df3.groupby(df3.index.date)       
        plot_df = df3_grouped[['Потрачено на рекламу', 'Экономия']].sum()
        plot_df['Максимальная ставка'] = df3_grouped['Максимальная ставка'].max()
        plot_df = plot_df[['Максимальная ставка', 'Потрачено на рекламу', 'Экономия']]

        economy_label = sum(list(df3['Экономия']))
        axes = plot_df.plot.bar(rot=0, subplots=True, figsize=(11, 11))

        plt.xlabel(xlabel=f"Общая экономия за выбранный период: {round(economy_label,2)} рублей", loc='right', labelpad=-65)

        plt.gca().set_xticks(
            np.arange(len(plot_df.index)),
            list(map(lambda x: x.strftime('%d.%m.%Y'), plot_df.index)),
            rotation=45
        )
        plt.savefig(f"user_analitics_image/{campaign_id}.png")     
        return f"user_analitics_image/{campaign_id}.png"
    
    def delete_photo(path):
        try:
            os.remove(path)
        except Exception:
            pass