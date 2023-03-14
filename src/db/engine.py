from .models import User, Base
from sqlalchemy import create_engine

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy').setLevel(logging.DEBUG) # logging.WARN DEBUG

engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres", future=True, echo=True) # , echo=True
Base.metadata.create_all(engine)