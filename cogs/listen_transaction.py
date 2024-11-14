import logging
import re
from nextcord.ext import commands
from database.controlers import db

# Set up logging for the cog
logger = logging.getLogger(__name__)
logging.getLogger('nextcord').setLevel(logging.WARNING)

class MessageListener(commands.Cog):
    """Cog for listening to and handling transaction messages."""

    def __init__(self, bot):
        self.bot = bot
        self.db = db()

    @commands.Cog.listener()
    async def on_message(self, message):
        """Event fired when a message is received."""
        if message.author == self.bot.user:
            return  # Avoid bot responding to itself

        if message.channel.name == '💸┆transactions':
            for embed in message.embeds:
                if embed.title == 'Transaction: Tip':
                    await self.handle_tip_transaction(embed.description, message.created_at)
                elif embed.title == 'Transaction: Casino Bet':
                    await self.handle_casino_bet_transaction(embed.description)
                elif 'Win' in embed.title or 'Cashout' in embed.title:
                    await self.handle_casino_win_transaction(embed.description)

    async def handle_tip_transaction(self, description, timestamp):
        """Handle 'Tip' transactions and update the database."""
        # Extract details using regex
        amount = int(re.search(r"\*\*Amount\*\*: (\d+)", description).group(1))
        sender = int(re.search(r"\*\*Sender\*\*: <@(\d+)>", description).group(1))
        receiver = int(re.search(r"\*\*Receiver\*\*: <@(\d+)>", description).group(1))

        # Calculate rewards for sender and receiver
        sender_rewards = 0.001 * amount * 0.8
        receiver_rewards = 0.001 * amount * 0.2

        # Ensure sender and receiver exist in the database
        sender_user = await self.ensure_user_in_db(sender)
        receiver_user = await self.ensure_user_in_db(receiver)

        # Update sender and receiver stats in the database
        self.db.update_user_tips(sender, tip_count=1, tip_spend=amount, tip_received=0)
        self.db.update_user_tips(receiver, tip_count=0, tip_spend=0, tip_received=amount)
        self.db.update_user_yield(sender, yield_earned=sender_rewards, unclaimed_yield=sender_rewards)
        self.db.update_user_yield(receiver, yield_earned=receiver_rewards, unclaimed_yield=receiver_rewards)

        # Log the transaction
        logger.info(f"Processed Tip: {amount} from User {sender} to User {receiver}. Timestamp: {timestamp}")

    async def handle_casino_bet_transaction(self, description):
        """Handle 'Casino Bet' transactions and update the database."""
        # Extract details using regex
        amount = int(re.search(r"\*\*Amount\*\*: (\d+)", description).group(1))
        sender = int(re.search(r"\*\*Sender\*\*: <@(\d+)>", description).group(1))

        # Ensure sender exists in the database
        sender_user = await self.ensure_user_in_db(sender)

        # Update sender's bet stats
        self.db.update_user_bets(sender, bet_count=1, bet_spend=amount, bet_win=0)

        # Update sender's yield and pool balance
        yield_increase = 0.001 * amount * 0.2
        self.db.update_user_yield(sender, yield_earned=yield_increase, unclaimed_yield=0)
        self.db.update_pool_balance("yield", balance=amount)

        # Log the transaction
        logger.info(f"Processed Casino Bet: {amount} bet by User {sender}.")

    async def handle_casino_win_transaction(self, description):
        """Handle 'Casino Win' transactions and update the database."""
        # Extract details using regex
        amount = int(re.search(r"\*\*Amount\*\*: (\d+)", description).group(1))
        receiver = int(re.search(r"\*\*Receiver\*\*: <@(\d+)>", description).group(1))

        # Ensure receiver exists in the database
        receiver_user = await self.ensure_user_in_db(receiver)

        # Update receiver's win stats and adjust pool balance
        self.db.update_user_bets(receiver, bet_count=0, bet_spend=0, bet_win=amount)
        self.db.update_pool_balance("yield", balance=-amount)

        # Log the transaction
        logger.info(f"Processed Casino Win: {amount} won by User {receiver}.")

    async def ensure_user_in_db(self, user_id):
        """Check if a user is in the database, if not, add them."""
        user = self.db.get_user(user_id)
        if not user:
            user_obj = await self.bot.fetch_user(user_id)
            self.db.add_user(user_id=user_id, username=user_obj.name)
            user = self.db.get_user(user_id)
        return user

def setup(bot):
    """Setup the cog."""
    bot.add_cog(MessageListener(bot))
