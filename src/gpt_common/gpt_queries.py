
import openai
from ui_backend.config import GPT_TOKEN, GPT_MODEL_NAME

from db.queries import db_queries

from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)
logger_token = appLogger.getLogger(__name__+'_token')

class gpt_queries:

    def get_card_description(prompt):
        openai.api_key = GPT_TOKEN
        completion = openai.ChatCompletion.create(
            model=GPT_MODEL_NAME,
            messages=[{"role": "user", "content": f"Создай описание товара и индексируемые теги, на маркетплейс с такими ключевыми параметрами: {prompt}"}])
        
        completion_content = completion.choices[0].message.content
        return completion_content