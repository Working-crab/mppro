
import openai
from ui_backend.config import GPT_TOKEN, GPT_MODEL_NAME

from db.queries import db_queries

from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)
logger_token = appLogger.getLogger(__name__+'_token')

class gpt_queries:

    def get_card_description(prompt, user_id):
        openai.api_key = GPT_TOKEN
        completion = openai.ChatCompletion.create(
            model=GPT_MODEL_NAME,
            messages=[{"role": "user", "content": f"Создай описание товара и индексируемые теги на маркетплейсе с такими ключевыми параметрами [{prompt}]. Все должно быть СТРОГО по следующему шаблону. Индексируемых тегов должно быть СТРОГО НЕ МЕНЬШЕ 10. Индексируемые теги должны идти СТРОГО через заяпятую БЕЗ ЛИШНИХ СИМВОЛОВ. Шаблон: Название товара; Описание товара; Индексируемые теги"}])
        
        logger.warn("completion")
        logger.warn(completion)
        tokens_spent = completion.usage.total_tokens
        
        db_queries.edit_user_tokens_transaction(user_id=user_id, amount=-tokens_spent, type="Карточка товара")
        
        completion_content = completion.choices[0].message.content

        db_queries.add_action_history(telegram_user_id=0, action="gpt_get_card_description", action_description=f"Генерация карточки по запросу: '{prompt}': '{completion_content}'")
  
        return completion_content
