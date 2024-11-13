from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import settings
import sqlalchemy
Base = sqlalchemy.orm.declarative_base()
import logging

logger = logging.getLogger("creatting_tables")
logger.setLevel(logging.INFO)


"""
Creating Jackpoot Pool Balance table
"""
class pools(Base):
    __tablename__ = 'pool'
    id = Column(Integer, primary_key=True)
    type = Column(String(50))
    balance = Column(Integer)
    def __init__(self,balance,type):
        self.type = type
        self.balance = balance
"""
Creating Users Stats table
"""

class users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50))
    tip_count = Column(Integer)
    tip_spend = Column(Integer)
    tip_receive = Column(Integer)
    bet_count = Column(Integer)
    bet_spend = Column(Integer)
    bet_win = Column(Integer)
    bet_lose = Column(Integer)
    yield_earned = Column(String)
    unclaimed_yield = Column(String)

    def __init__(self,user_id,tip_count,tip_spend,tip_receive,bet_count,bet_spend,bet_win,bet_lose,yield_earned,unclaimed_yield):
        self.user_id = user_id
        self.tip_count = tip_count
        self.tip_spend = tip_spend
        self.tip_receive = tip_receive
        self.bet_count = bet_count
        self.bet_spend = bet_spend
        self.bet_win = bet_win
        self.bet_lose = bet_lose
        self.yield_earned = yield_earned
        self.unclaimed_yield = unclaimed_yield



class lottery(Base):
    __tablename__ = 'lottery'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50))
    ticket = Column(Integer)

    def __init__(self,user_id,ticket):
        self.user_id = user_id
        self.ticket = ticket

engine = create_engine(settings.DB_URL)
logger.info("Creating Database tables (pool,tip_reward_pool,Users)")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

insert_lottery = pools(type='lottery',balance=0)
insert_yield = pools(type='yield',balance=0)
logger.info("inserting data to table (pool,tip_reward_pool)")
session.add(insert_lottery)
session.add(insert_yield)
session.commit()
session.close()
