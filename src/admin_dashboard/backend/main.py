from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware

from db.queries import db_queries
from admin_dashboard.backend.serializers import Action, ActionList, User

from datetime import datetime, timedelta

app = FastAPI(openapi_url=None) # openapi_url=None fix on the end TODO

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
@app.on_event('startup')
async def on_startup():
    print('Startup complete!')

@app.get("/last_actons/")
async def get_last_actions():
  last_actions = await db_queries.get_action_history_last_actions()
  last_actions_q = list(last_actions)
  list_last_actions = ActionList.from_orm(last_actions_q).dict()
  list_last_actions["__root__"]
  return {'last_actions': list_last_actions['__root__']}

@app.get("/last_errors/")
async def get_last_actions():
  last_errors = await db_queries.get_action_history_last_errors()
  last_errors_q = list(last_errors)
  list_last_errors = ActionList.from_orm(last_errors_q).dict()
  list_last_errors["__root__"]
  return {'last_errors': list_last_errors['__root__']}

@app.get("/info_own_services/")
async def get_services_successullnes():
  services_names = ['default', 'ui_backend', 'bot_message_sender', 'wb_routines', 'user_automation']
  services_successullnes = []
  for service_name in services_names:
    service = {}
    query = await db_queries.get_action_history_initiator_succsess_count(service_name)
    
    if query['err'] == 0:
      service[service_name] = 100
    else:
      service[service_name] = round((1 - (query['err'] / query['all_t'])), 2) * 100
    services_successullnes.append(service)

  return {'own_services': services_successullnes}


@app.get("/user/{user_id}")
async def get_user_by_id(user_id):
  user_orm = await db_queries.get_user_by_id(int(user_id))
  user = User.from_orm(user_orm).dict()
  return {'user': user}


@app.get("/last_week_errors/")
async def get_graph_errors():
  errors_orm = await db_queries.get_week_errors_action_history(30)
  errors = ActionList.from_orm(errors_orm).dict()['__root__']
  err_actions_for_time = await db_queries.get_time_interval_errors_action_history(30)
  new_map = {}
  for err_actions in err_actions_for_time:
    date_key = f"{err_actions[0].day}.{err_actions[0].month}.{err_actions[0].year}"
    new_map[date_key] = {"success_count" : int(err_actions[1]), "error_count" : int(err_actions[2])}

  week_days = {}
  date = datetime.now() - timedelta(days=30)
  for day in range(1, 31):
    date_key = f"{date.day}.{date.month}.{date.year}"
    week_days[date_key] = {"success_count" : 0, "error_count" : 0}
    date = date + timedelta(days=1)
  
  week_days.update(new_map)

  return {'errors': week_days}