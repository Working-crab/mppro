
from ui_backend.message_queue import queue_message_async as queue_message_to_user
from ui_backend.mq_campaign_info import queue_message_async as queue_campaign_info



def process_campaign(message_body):
    data = queue_campaign_info()
    template = f'Список ваших рекламных компаний с cmp\.wildberries\.ru, страница: {page_number}\n\n'
    
