import discord
import re
from discord.ext import commands
from controlers import db


class TransactionCog(commands.Cog):
    """Cog to handle transaction events and update database accordingly."""

    def __init__(self, bot):
        self.bot = bot
        self.db = db()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        if message.channel.name != "💸┆transactions" or not message.embeds:
            return

        msg = message.embeds[0].to_dict()
        if msg["title"] == "Transaction: Tip":
            await self.handle_tip_transaction(msg)
        elif msg["title"] == "Transaction: Casino Bet":
            await self.handle_casino_bet(msg)
        elif "Win" in msg["title"]:
            await self.handle_casino_win(msg)

    async def handle_tip_transaction(self, msg):
        """Handle tip transactions and update the sender's and receiver's database entries."""
        parse_msg = self.parse_transaction_message(msg["description"])
        tip_amount = float(parse_msg[0])
        sender_id = self.extract_user_id(parse_msg[1])
        receiver_id = self.extract_user_id(parse_msg[3])

        sender_reward, receiver_reward = self.calculate_rewards(
            tip_amount, sender_percentage=0.8
        )

        # Process sender data
        await self.update_user_data(
            sender_id, tip_amount, sender_reward, is_sender=True
        )

        # Process receiver data
        await self.update_user_data(
            receiver_id, tip_amount, receiver_reward, is_sender=False
        )

    async def handle_casino_bet(self, msg):
        """Handle casino bet transactions and update the bettor's database entry."""
        parse_msg = self.parse_transaction_message(msg["description"])
        bet_amount = float(parse_msg[0])
        sender_id = self.extract_user_id(parse_msg[1])

        await self.update_bet_data(sender_id, bet_amount, is_win=False)

    async def handle_casino_win(self, msg):
        """Handle casino win transactions and update the bettor's database entry."""
        parse_msg = self.parse_transaction_message(msg["description"])
        win_amount = float(parse_msg[0])
        sender_id = self.extract_user_id(parse_msg[2])

        await self.update_bet_data(sender_id, win_amount, is_win=True)

    def parse_transaction_message(self, description):
        """Extracts transaction details from a formatted description string."""
        return re.findall(r"\*\*\w+\*\*:(.*)", description.replace(" ", ""))

    def extract_user_id(self, user_str):
        """Extract user ID from a string containing a Discord mention."""
        return re.search(r"<@([0-9]+)>", user_str).group(1)

    def calculate_rewards(self, amount, sender_percentage=0.8):
        """Calculate rewards for sender and receiver based on the transaction amount."""
        reward_base = 0.001 * amount  # Conversion factor
        sender_reward = format(reward_base * sender_percentage, ".4f")
        receiver_reward = format(reward_base * (1 - sender_percentage), ".4f")
        return sender_reward, receiver_reward

    async def update_user_data(self, user_id, tip_amount, reward, is_sender=True):
        """Add or update user data in the database for tips and rewards."""
        user_data = self.db.check_users(userid=user_id)

        if user_data["status"]:
            update_data = {
                "tip_count": user_data["tip_count"] + (1 if is_sender else 0),
                "tip_spend": user_data["tip_spend"]
                + (int(tip_amount) if is_sender else 0),
                "tip_receive": user_data["tip_receive"]
                + (int(tip_amount) if not is_sender else 0),
                "yield_earned": float(user_data["yield_earned"]) + float(reward),
                "unclaimed_yield": float(user_data["unclaimed_yield"]) + float(reward),
            }
            self.db.update_data(user_id, update_data)
        else:
            new_user_data = {
                "user_id": str(user_id),
                "tip_count": 1 if is_sender else 0,
                "tip_spend": int(tip_amount) if is_sender else 0,
                "tip_receive": 0 if is_sender else int(tip_amount),
                "bet_count": 0,
                "bet_spend": 0,
                "bet_win": 0,
                "bet_lose": 0,
                "yield_earned": reward,
                "unclaimed_yield": reward,
            }
            self.db.add_user(data=new_user_data)

    async def update_bet_data(self, user_id, amount, is_win=False):
        """Add or update user data in the database for casino bets and wins."""
        user_data = self.db.check_users(userid=user_id)
        pool = self.db.get_pool("yield")

        if user_data["status"]:
            update_data = {
                "bet_count": user_data["bet_count"] + 1,
                "bet_spend": user_data["bet_spend"] + int(amount),
                "bet_win": user_data["bet_win"] + (1 if is_win else 0),
                "bet_lose": user_data["bet_lose"] + (1 if not is_win else 0),
            }
            self.db.update_data(user_id, update_data)
            pool_adjustment = int(pool) + (int(amount) if not is_win else -int(amount))
        else:
            new_user_data = {
                "user_id": user_id,
                "tip_count": 0,
                "tip_spend": 0,
                "tip_receive": 0,
                "unclaimed_yield": 0.001 * float(amount) * 0.8 if not is_win else 0,
                "bet_count": 1,
                "bet_spend": int(amount),
                "bet_win": 1 if is_win else 0,
                "bet_lose": 1 if not is_win else 0,
                "yield_earned": 0.001 * float(amount) * 0.2,
            }
            self.db.add_user(data=new_user_data)
            pool_adjustment = int(pool) + (int(amount) if not is_win else -int(amount))

        self.db.update_pool_balance("yield", pool_adjustment)


async def setup(bot):
    await bot.add_cog(TransactionCog(bot))
