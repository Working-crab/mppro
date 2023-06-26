from admin_dashboard.backend.main import Sub, SubList, db_queries, User

user = db_queries.get_user_by_id(1)
subs = db_queries.get_all_sub()

subs_q = list(subs)

dict_user = User.from_orm(user)
list_subs = SubList.from_orm(subs_q).dict()