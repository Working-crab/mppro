
import json
from datetime import datetime
from cache_worker.cache_worker import cache_worker
import requests
import time
import openai
from ui_backend.config_local import GPT_TOKEN

from db.queries import db_queries

from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)
logger_token = appLogger.getLogger(__name__+'_token')

class gpt_queries:

    def get_card_description(prompt):
        openai.api_key = GPT_TOKEN
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Создай описание товара и индексируемые теги, на маркетплейс с такими ключевыми параметрами: {prompt}"}])
        
        completion_content = completion.choices[0].message.content
        return completion_content