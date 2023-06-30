from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware

from db.queries import db_queries
from admin_dashboard.backend.serializers import Action, ActionList

app = FastAPI(openapi_url=None) # openapi_url=None fix on the end TODO

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
@app.get("/last_actons")
def get_last_actions():
  last_actions = db_queries.get_last_actions()
  last_actions_q = list(last_actions)
  list_last_actions = ActionList.from_orm(last_actions_q).dict()
  list_last_actions["__root__"].reverse()
  return {'last_actions': list_last_actions['__root__']}

# @app.get("/last_errors")
# def get_last_actions():
#   last_actions = db_queries.get_last_actions()
#   last_actions_q = list(last_actions)
#   list_subs = ActionList.from_orm(last_actions_q).dict()
#   list_subs["__root__"].reverse()
#   return {'last_actions': list_subs['__root__']}