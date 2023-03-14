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
    time_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    subscriptions_id = Column(Integer, ForeignKey('subscriptions.id'), nullable=True)

    subscriptions = relationship("Subscription", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    user_budget_analitics_logs = relationship("User_budget_analitics_logs", back_populates="user")
    action_history = relationship("Action_history", back_populates="user")
       
    sub_start_date = Column(DateTime(timezone=True))
    sub_end_date = Column(DateTime(timezone=True))

    adverts = relationship("Advert")

    def __repr__(self):
        return f"User(id={self.id!r}, username={self.telegram_username!r})"

class Advert(Base):
    __tablename__ = "adverts"

    id = Column(Integer, primary_key=True)
    max_budget = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    place = Column(String, nullable=False)
    campaign_id = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False)
    
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="adverts")
    user_budget_analitics_logs = relationship('User_budget_analitics_logs', back_populates='adverts')

    def __repr__(self):
        return f"Advert(id={self.id!r}, max_budget={self.max_budget!r}, user_id={self.user_id!r}, place={self.place!r})"


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, default=0)

    user = relationship('User', back_populates='subscriptions')
    transactions = relationship('Transaction', back_populates='subscriptions')

    def __repr__(self):
        return f"Subscription(id={self.id!r}, title={self.title!r}, price={self.price!r}, user_id={self.user_id!r})"
    
    
class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    total = Column(Integer, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'), nullable=False)

    user = relationship('User', back_populates='transactions')
    subscriptions = relationship('Subscription', back_populates='transactions')

    def __repr__(self):
        return f"Transaction(id={self.id!r}, title={self.title!r}, total={self.total!r}, user_id={self.user_id!r}, subscription_id={self.subscription_id!r})"


class User_budget_analitics_logs(Base):
    __tablename__ = "user_budget_analitics_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("adverts.id"), nullable=False)
    date_time = Column(DateTime(timezone=True), server_default=func.now())
    budget = Column(Integer, default=0)
    spent_money = Column(Integer, default=0)
    up_money = Column(Integer, default=0)

    user = relationship('User', back_populates='user_budget_analitics_logs')
    adverts = relationship('Advert', back_populates='user_budget_analitics_logs')

    def __repr__(self):
        return f"User_budget_analitics_logs(id={self.id!r}, user_id={self.user_id!r}, campaign_id={self.campaign_id!r})"
    
    
class Action_history(Base):
    __tablename__ = "action_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String, nullable=False)
    description = Column(String, nullable=False)
    date_time = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='action_history')

    def __repr__(self):
        return f"Action_history(id={self.id!r}, user_id={self.user_id!r}, action={self.action!r}, description={self.description!r})"