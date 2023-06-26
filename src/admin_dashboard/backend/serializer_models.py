from pydantic import BaseModel, ValidationError
from typing import Union, List, Optional
from datetime import datetime

class Sub(BaseModel):
  id: int
  title: str
  description: str
  price: int
  requests_get: Optional[int]
  tracking_advertising: Optional[int]

  class Config:
    orm_mode = True

class SubList(BaseModel):
  __root__: List[Sub]

  class Config:
    orm_mode = True


class User(BaseModel):

  id: int
  telegram_user_id: int
  telegram_chat_id: int
  telegram_username: str
  wb_v3_main_token: str
  wb_cmp_token: str
  x_supplier_id: str

  class Config:
    orm_mode = True

class UserList(BaseModel):
  __root__: List[User]

  class Config:
    orm_mode = True


class Action(BaseModel):

  id: int
  user_id: int
  action: str
  description: str
  date_time: datetime

  class Config:
    orm_mode = True

class ActionList(BaseModel):
  __root__: List[Action]

  class Config:
    orm_mode = True