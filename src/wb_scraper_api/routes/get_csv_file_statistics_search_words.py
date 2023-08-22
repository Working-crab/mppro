from fastapi import APIRouter, Query, Depends
import pandas as pd
import clickhouse_driver
from fastapi.responses import StreamingResponse
from io import BytesIO
from datetime import datetime, timedelta


class CustomQueryParams:
    def __init__(
        self,
        id_product: int | None = Query(description="Атрибут товара"),
        start_periud: int | None  = Query(default=None, description="Старт периуда (unix time)"),
        end_periud: int | None  = Query(default=None, description="Конец периуда (unix time)")
    ):
        self.id_product = id_product

        if start_periud == None:
            self.start_periud = (datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d')
            print(self.start_periud)
        else:
            self.start_periud = datetime.fromtimestamp(start_periud).strftime('%Y-%m-%d')

        if start_periud == None:
            self.end_periud = datetime.now().strftime('%Y-%m-%d')
            print(self.end_periud)
        else:
            self.end_periud = datetime.fromtimestamp(end_periud).strftime('%Y-%m-%d')

route = APIRouter()

@route.get('/csv_file_statistics_search_words')
async def main (params: CustomQueryParams = Depends()):
    client = clickhouse_driver.Client.from_url(f"""clickhouse://default:@localhost:9000/default""")
    result = client.execute(f""" SELECT * FROM product_position WHERE id_product = {params.id_product} and date_collected >= '{params.start_periud}' and date_collected <= '{params.end_periud}'""")
    df = pd.DataFrame(result)
    search_words = df[3].unique()
    df[4] = pd.to_datetime(df[4])
    date_lst = df[4].unique()
    df_result = []

    def get (lst, defaulf):
        try:
            return lst[0]
        except:
            return defaulf

    for i_word,value_word in enumerate(search_words):
        res_obj = {
            'Слово для поиска': value_word
        }
        for i,value in enumerate(date_lst):
            res_obj[datetime.strftime(value,'%Y-%m-%d')] = get(df.loc[(df[4] == value) & (df[3] == value_word)][:1][2].values,0)
        df_result.append(res_obj)

    df_res = pd.DataFrame(df_result)
    csv_file = BytesIO()
    df_res.to_csv(csv_file,index= False,encoding='utf-8')
    csv_file.seek(0)
    return StreamingResponse(csv_file, media_type="text/csv",headers={'Content-Disposition': f'attachment; filename="{params.id_product}.csv"'})
    
@route.get('/statistics_search_words')
async def main (params: CustomQueryParams = Depends()):
    client = clickhouse_driver.Client.from_url(f"""clickhouse://default:@localhost:9000/default""")
    result = client.execute(f""" SELECT * FROM product_position WHERE id_product = {params.id_product} and date_collected >= '{params.start_periud}' and date_collected <= '{params.end_periud}'""")
    df = pd.DataFrame(result)
    print(df)
    search_words = df[3].unique()
    df[4] = pd.to_datetime(df[4])
    date_lst = df[4].unique()
    df_result = []

    def get (lst, defaulf):
        try:
            return lst[0]
        except:
            return defaulf

    for i_word,value_word in enumerate(search_words):
        res_obj = {
            'Слово для поиска': value_word
        }
        for i,value in enumerate(date_lst):
            res_obj[datetime.strftime(value,'%Y-%m-%d')] = get(df.loc[(df[4] == value) & (df[3] == value_word)][:1][2].values,0)
        df_result.append(res_obj)

    df = pd.DataFrame(df_result)
    return {df.to_json()}
