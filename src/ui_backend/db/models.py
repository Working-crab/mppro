from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(BigInteger, nullable=False, unique=True)
    telegram_chat_id = Column(BigInteger, nullable=False, unique=True)
    telegram_username = Column(String(255))
    wb_main_token = Column(String(2048))
    wb_cmp_token = Column(String(2048))

    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    adverts = relationship("Advert")

    
    def __repr__(self):
        return f"User(id={self.id!r}, username={self.telegram_username!r})"

class Advert(Base):
    __tablename__ = "adverts"

    id = Column(Integer, primary_key=True)
    max_budget = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    place = Column(String, nullable=False)
    compagin_id = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False)
    
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="adverts")

    def __repr__(self):
        return f"Advert(id={self.id!r}, max_budget={self.max_budget!r}, user_id={self.user_id!r}, place={self.place!r})"
