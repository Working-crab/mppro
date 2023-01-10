from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, BigInteger
from sqlalchemy import String, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(BigInteger, nullable=False, unique=True)
    telegram_chat_id = Column(BigInteger, nullable=False, unique=True)
    telegram_username = Column(String(120))
    wb_main_token = Column(String(255))
    

    def __repr__(self):
        return f"User(id={self.id!r}, username={self.telegram_username!r})"
