from datetime import datetime

from db.queries import db_queries
from wb_common.wb_queries import wb_queries

class User_logs():
    def start(user_id, error_message, error_type):
        date_time = datetime.now()
        db_queries.add_user_logs(user_id, date_time, error_message, error_type)
        return True
