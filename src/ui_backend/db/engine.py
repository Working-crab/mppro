from .models import User, Base
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres", echo=True, future=True)
Base.metadata.create_all(engine)