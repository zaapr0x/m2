import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import as_declarative
import settings
from sqlalchemy import select, func
from sqlalchemy import select
from sqlalchemy.sql.functions import random

Base = sqlalchemy.orm.declarative_base()


# Define database models
class Pool(Base):
    __tablename__ = "pool"
    id = Column(Integer, primary_key=True)
    type = Column(String(50))
    balance = Column(Integer)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), unique=True, nullable=False)
    tip_count = Column(Integer, default=0)
    tip_spend = Column(Integer, default=0)
    tip_receive = Column(Integer, default=0)
    bet_count = Column(Integer, default=0)
    bet_spend = Column(Integer, default=0)
    bet_win = Column(Integer, default=0)
    bet_lose = Column(Integer, default=0)
    yield_earned = Column(String, default="0")
    unclaimed_yield = Column(String, default="0")


class UserBet(Base):
    __tablename__ = "user_bet"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False)
    bet_count = Column(Integer, default=0)
    bet_spend = Column(Integer, default=0)
    bet_win = Column(Integer, default=0)
    bet_lose = Column(Integer, default=0)


class Lottery(Base):
    __tablename__ = "lottery"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False)
    ticket = Column(Integer, nullable=False)


# Database handler class
class db:
    def __init__(self):
        self.engine = create_engine(settings.DB_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_pool(self, pool_type: str) -> int:
        with self.Session() as session:
            pool = session.query(Pool).filter_by(type=pool_type).first()
            return pool.balance if pool else 0

    def update_pool_balance(self, pool_type: str, amount: int) -> bool:
        with self.Session() as session:
            result = (
                session.query(Pool)
                .filter_by(type=pool_type)
                .update({"balance": amount})
            )
            session.commit()
            return result > 0

    def check_users(self, userid: str) -> dict:
        with self.Session() as session:
            user = session.query(User).filter_by(user_id=userid).first()
            return (
                {
                    "status": bool(user),
                    **{
                        col: getattr(user, col)
                        for col in User.__table__.columns.keys()
                        if user
                    },
                }
                if user
                else {"status": False}
            )

    def add_user(self, data: dict):
        with self.Session() as session:
            new_user = User(**data)
            session.add(new_user)
            session.commit()

    def update_data(self, user_id: str, data: dict) -> bool:
        with self.Session() as session:
            result = session.query(User).filter_by(user_id=user_id).update(data)
            session.commit()
            return result > 0

    def leaderboard(self, limit: int = 20) -> list:
        with self.Session() as session:
            results = (
                session.query(User).order_by(desc(User.tip_spend)).limit(limit).all()
            )
            return [
                {
                    "user_id": user.user_id,
                    "tip_count": user.tip_count,
                    "tip_spend": round(user.tip_spend),
                    "yield_earned": round(float(user.yield_earned)),
                }
                for user in results
            ]

    def get_user(self) -> list:
        with self.Session() as session:
            return [user.user_id for user in session.query(User).all()]

    def pick_random_user(self) -> User:
        with self.Session() as session:
            return session.query(User).order_by(func.random()).first()
