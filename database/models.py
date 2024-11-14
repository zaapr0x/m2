from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
import datetime
from sqlalchemy import create_engine
import config
from sqlalchemy.orm import sessionmaker
# Base class for declarative models
Base = declarative_base()
engine = create_engine(f"sqlite:///{config.DB_NAME}", echo=True)

class Pool(Base):
    __tablename__ = 'pool'
    id = Column(Integer, primary_key=True)
    type = Column(String(50))
    balance = Column(Integer,default=0)
    def __init__(self,balance,type):
        self.type = type
        self.balance = balance

class User(Base):
    __tablename__ = 'users'

    # Primary key and user identification
    id = Column(String, primary_key=True, nullable=False)  # User's unique ID (e.g., Discord ID)
    username = Column(String, nullable=False, index=True)  # User's username, indexed for performance

    # Tip-related statistics
    tip_count = Column(Integer, default=0, nullable=False)  # Total number of tips sent by the user
    tip_spend = Column(Integer, default=0, nullable=False)  # Total amount spent on tips
    tip_received = Column(Integer, default=0, nullable=False)  # Total amount received as tips

    # Bet-related statistics
    bet_count = Column(Integer, default=0, nullable=False)  # Total number of bets placed by the user
    bet_spend = Column(Integer, default=0, nullable=False)  # Total amount spent on betting
    bet_win = Column(Integer, default=0, nullable=False)  # Total amount won by the user from their bets
    bet_lose = Column(Integer, default=0, nullable=False)  # Total amount lost (calculated as bet_spend - bet_win)

    # Yield statistics
    yield_earned = Column(Float, default=0.0, nullable=False)  # Total yield earned by the user (e.g., rewards, returns)
    unclaimed_yield = Column(Float, default=0.0, nullable=False)  # Yield that has been earned but not yet claimed

    def __init__(self, id, username):
        self.id = id
        self.username = username
# Create the tables in the database
def initialize_tables():
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    insert_lottery = Pool(type='lottery',balance=0)
    insert_yield = Pool(type='yield',balance=0)
    session.add(insert_lottery)
    session.add(insert_yield)
    session.commit()