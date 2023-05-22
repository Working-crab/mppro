from kafka_dir.topics import Topics
from ui_backend.common import get_first_place, status_parser
from wb_common.wb_queries import wb_queries

from unittest import mock

def process_campaign(adverts, id_to_db_adverts, user, page_number):
    pass
#     template_keys_map = {}
#     for advert in adverts:
#         template_keys_map[advert['id']] = {
#             'budget': None,
#             'first_place': None,
#             'in_db': False
#         }

#     items = template_keys_map.items()
    

#     for advert_id, advert in items:
#         campaign = mock.Mock()
#         campaign.campaign_id = advert_id
#         budget = wb_queries.get_budget(user, campaign)
#         budget = budget.get("Бюджет компании")
#         template_keys_map[advert_id]['budget'] = budget
#         template_keys_map[advert_id]['in_db'] = True

#     # Обновить бюджеты путем изменеия сообщения

#     for i in range(3):
#        pass
#         # update_first_places()
#         # Обновить первые места путем изменеия сообщения

# def update_first_places(items, template_keys_map, campaign, user):
#     for advert_id, advert in items:
#         first_place = get_first_place(user.id, campaign)
#         template_keys_map[advert_id]['first_place'] = first_place


# def template_getter(page_number, advert, keys_values, id_to_db_adverts):
#     stat = status_parser(advert['statusId'])

#     header = f'Список ваших рекламных компаний с cmp\.wildberries\.ru, страница: {page_number}\n\n'
#     add_delete_str = ''
#     bot_status = ''

#     if db_advert := id_to_db_adverts.get(advert['id']):
#       if db_advert.status == 'ON':
#         bot_status     += f"\t Отслеживается\!"
#         add_delete_str += f"\t Перестать отслеживать РК: /delete\_adv\_{advert['id']}\n"
#         add_delete_str += f"\t Макс\. ставка: {db_advert.max_bid} макс\. место: {db_advert.place}\n"
#       else:
#         bot_status     += f"\t Не отслеживается\!"
#         add_delete_str += f"\t Отслеживать РК: /add\_adv\_{advert['id']}\n"
#     else:
#       bot_status     += f"\t Не отслеживается\!"
#       add_delete_str += f"\t Отслеживать РК: /add\_adv\_{advert['id']}\n"

#       a = """
#         Список ваших рекламных компаний с cmp\.wildberries\.ru, страница: {page_number}\n\n
#         \t Отслеживается\!
#       """

      
