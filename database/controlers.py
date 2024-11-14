import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from database.models import *
from sqlalchemy import func
import logging
# Import settings from the config package
import config
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class db:
    def __init__(self):
        self.engine = create_engine(f"sqlite:///{config.DB_NAME}", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        
    def add_user(self, user_id: str, username: str):
        """Add a new user to the database if they don't exist."""
        with self.Session() as session:
            existing_user = session.query(User).filter_by(id=user_id).first()
            if not existing_user:
                new_user = User(id=user_id, username=username)
                session.add(new_user)
                session.commit()
                print(f"User {username} added to the database.")
            else:
                print(f"User {username} already exists in the database.")

    def get_user(self, user_id: str):
        """Retrieve a user from the database by ID."""
        with self.Session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            return user
        
    def update_user(self, user_id: str, data: dict) -> bool:
        """
        Update user data in the database.

        :param user_id: The ID of the user to update.
        :param data: A dictionary containing the columns to be updated with their new values.
        :return: True if the user was updated successfully, False otherwise.
        """
        try:
            with self.Session() as session:
                # Perform the update and capture the number of affected rows
                rows_updated = session.query(User).filter_by(id=user_id).update(data)
                # Commit the changes
                session.commit()
                # Check if the update was successful
                if rows_updated > 0:
                    logger.info(f"User {user_id} successfully updated.")
                    return True
                else:
                    logger.warning(f"User {user_id} not found or no changes made.")
                    return False
        except SQLAlchemyError as e:
            # Handle SQL errors and log the exception
            session.rollback()  # Rollback in case of error
            logger.error(f"Error updating user {user_id}: {str(e)}")
            return False

    def update_user_tips(self, user_id: str, tip_count: int, tip_spend: int, tip_received: int):
        """Update user's tip stats: count, spend, and received."""
        with self.Session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                user.tip_count += tip_count
                user.tip_spend += tip_spend
                user.tip_received += tip_received
                session.commit()
                print(f"User {user.username}'s tip stats updated.")
            else:
                print(f"User with ID {user_id} not found.")

    def update_user_bets(self, user_id: str, bet_count: int, bet_spend: int, bet_win: int):
        """Update user's bet stats: count, spend, and win/lose."""
        with self.Session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                user.bet_count += bet_count
                user.bet_spend += bet_spend
                user.bet_win += bet_win
                user.bet_lose = user.bet_spend - user.bet_win
                session.commit()
                print(f"User {user.username}'s bet stats updated.")
            else:
                print(f"User with ID {user_id} not found.")

    def update_user_yield(self, user_id: str, yield_earned: float, unclaimed_yield: float):
        """Update user's yield stats: earned and unclaimed yield."""
        with self.Session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                user.yield_earned += yield_earned
                user.unclaimed_yield += unclaimed_yield
                session.commit()
                print(f"User {user.username}'s yield stats updated.")
            else:
                print(f"User with ID {user_id} not found.")

    def add_pool(self, pool_type: str, balance: int = 0):
        """Add a new pool entry to the database."""
        with self.Session() as session:
            existing_pool = session.query(Pool).filter_by(type=pool_type).first()
            if not existing_pool:
                new_pool = Pool(type=pool_type, balance=balance)
                session.add(new_pool)
                session.commit()
                print(f"Pool {pool_type} added with balance {balance}.")
            else:
                print(f"Pool {pool_type} already exists.")

    def update_pool_balance(self, pool_type: str, amount: int):
        """Update the balance of a specified pool by type."""
        with self.Session() as session:
            pool = session.query(Pool).filter_by(type=pool_type).first()
            if pool:
                pool.balance += amount
                session.commit()
                print(f"Pool {pool_type} balance updated by {amount}.")
            else:
                print(f"Pool {pool_type} not found.")

    def get_pool_balance(self, pool_type: str):
        """Retrieve the balance of a specified pool by type."""
        with self.Session() as session:
            pool = session.query(Pool).filter_by(type=pool_type).first()
            return pool.balance if pool else None
        
    def get_random_user_id(self):
        with self.Session() as session:
            user = session.query(User).order_by(func.random()).first()
            return user.id
        
    def get_all_user_ids(self):
        with self.Session() as session:
            users = session.query(User).all()
            return [user.id for user in users]