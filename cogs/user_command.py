import logging
import nextcord
import re
from datetime import datetime
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
from nextcord.ui import View, Button
from database.controlers import db
from DRIP_API import DripRealmAPI
# Set up logging for the cog to track errors and information
logger = logging.getLogger(__name__)

class SlashCommand(commands.Cog):
    """Slash commands for user interaction and transaction management."""
    
    def __init__(self, bot):
        """Initialize the bot and database connection."""
        self.bot = bot
        self.db = db()
        self.api = DripRealmAPI()

    @nextcord.slash_command(name="dashboard", description="User Dashboard")
    async def dashboard(self, interaction: Interaction):
        user_balance = self.api.view_user_balance(interaction.user.id)["tokens"]
        """Display the user's dashboard, showing balance and yield stats."""
        # Fetch user data from the database
        user_data = self.db.get_user(interaction.user.id)

        # If user data doesn't exist, create a new user
        if not user_data:
            self.db.add_user(user_id=interaction.user.id, username=interaction.user.name)

            # Create a default dashboard with 0 balance and yields
            embed = nextcord.Embed(
                title=f"{interaction.user.name}'s Dashboard",
                description="User Balance\n✨ **0**\n\nYields\n✨ **0 Unclaimed Yields**\n✨ **0 Yields Earned So Far**"
            )
            embed.set_thumbnail(url=interaction.user.avatar)

            # Send the message to the user
            await interaction.response.send_message(embed=embed)
        else:
            # Create a personalized dashboard for the user with their actual data
            embed = nextcord.Embed(
                title=f"{interaction.user.name}'s Dashboard",
                description=f"User Balance\n✨ **{user_balance}**\n\nYields\n✨ **{user_data.unclaimed_yield} Unclaimed Yields**\n✨ **{user_data.yield_earned} Yields Earned So Far**"
            )
            embed.set_thumbnail(url=interaction.user.avatar)

            # Add a button for claiming yield
            claim_yield = Button(label="Claim Yield", style=nextcord.ButtonStyle.green)
            claim_yield.callback = self.claim_yield

            # Add the button to the view
            view = View()
            view.add_item(claim_yield)

            # Send the personalized dashboard to the user with the claim button
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def claim_yield(self, interaction: Interaction):
        """Claim the user's unclaimed yield."""
        # Get user details from the database
        user_data = self.db.get_user(interaction.user.id)

        # Check if the user has unclaimed yield
        if not user_data or round(user_data.unclaimed_yield) <= 0:
            # Inform the user that there is nothing to claim
            await interaction.response.edit_message(content="❌ Minimum yield to claim is 1.", embed=None, view=None)
            return
        
        # Claim the user's yield
        claim = self.api.update_user_balance(interaction.user.id,user_data.unclaimed_yield)
        if claim:
            self.db.update_user(interaction.user.id, {"unclaimed_yield": 0})
            await interaction.response.edit_message(content="✅ Your unclaimed yield has been claimed!", embed=None, view=None)
            return
        
        

        # Create an updated embed after the yield claim
       

    @nextcord.slash_command(name="stats", description="User Stats")
    async def stats(self, interaction: Interaction):
        """Display the user's statistics including tips and bets."""
        user_data = self.db.get_user(interaction.user.id)

        # Create an embed showing user's stats for tips and bets
        embed = nextcord.Embed(
            title=f"{interaction.user.name}'s Stats",
            description=(
                f"✨ **{user_data.tip_count}** Tip Count\n"
                f"✨ **{user_data.tip_spend}** Tip Spend\n"
                f"✨ **{user_data.tip_received}** Tip Receive\n\n"
                f"✨ **{user_data.bet_count}** Bet Count\n"
                f"✨ **{user_data.bet_spend}** Bet Spend\n\n"
                f"✨ **{user_data.bet_win}** Bet Win\n"
                f"✨ **{max(user_data.bet_spend - user_data.bet_win, 0)}** Bet Lose"
            )
        )
        embed.set_thumbnail(url=interaction.user.avatar)

        # Send the stats embed to the user
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(name="txs-scan", description="Transaction Scan")
    async def txs_scan(self, interaction: Interaction, tx_hash: str = SlashOption(description="Txid")):
        """Search and display transaction details for a given transaction hash."""
        # Get the transactions channel
        channel = nextcord.utils.get(interaction.guild.channels, name='💸┆transactions')

        # If the channel doesn't exist, send a message and stop
        if not channel:
            await interaction.response.send_message("Channel not found.", ephemeral=True)
            return
        
        embed = nextcord.Embed(title="Search Results", colour=0x1a73e8)
        
        # Search through the entire message history in the channel for the tx_hash
        async for message in channel.history(limit=None):  # No limit to search all messages
            for embed_content in message.embeds:
                if embed_content.description and tx_hash in embed_content.description:
                    if embed_content.title == 'Transaction: Tip':
                        # Extract and format transaction details
                        timestamp_obj = datetime.fromisoformat(str(message.created_at))
                        timestamp = timestamp_obj.strftime("%Y-%m-%d %I:%M:%S %p")
                        amount_pattern = r"\*\*Amount\*\*: (\d+)"
                        sender_pattern = r"\*\*Sender\*\*: <@(\d+)>"
                        receiver_pattern = r"\*\*Receiver\*\*: <@(\d+)>"
                        
                        amount = int(re.search(amount_pattern, embed_content.description).group(1))
                        sender = int(re.search(sender_pattern, embed_content.description).group(1))
                        receiver = int(re.search(receiver_pattern, embed_content.description).group(1))
                        sender_rewards = 0.001 * amount * 0.8
                        receiver_rewards = 0.001 * amount * 0.2
                        
                        # Fetch user details by ID
                        s_uname = await self.bot.fetch_user(sender)
                        r_uname = await self.bot.fetch_user(receiver)

                        # Create the embed for the tip transaction details
                        embed = nextcord.Embed(
                            title="Transaction : Tip",
                            description=(
                                f"**Sender** : {s_uname}\n**Receiver** : {r_uname}\n\n"
                                f"**Amount** : {amount} ✨\n**Total Yield** : {0.001 * amount} ✨\n\n"
                                f"**Sender Reward** : {sender_rewards} ✨\n**Receiver Reward** : {receiver_rewards} ✨"
                            )
                        )
                        embed.set_footer(text=timestamp, icon_url=self.bot.user.avatar)

                        # Send the embed with the button
                        await interaction.response.send_message(embed=embed,ephemeral=True)
                        return  # Stop after the first match
                    elif embed_content.title == 'Transaction: Casino Bet':
                        # Similar process for handling casino bet transactions
                        timestamp_obj = datetime.fromisoformat(str(message.created_at))
                        timestamp = timestamp_obj.strftime("%Y-%m-%d %I:%M:%S %p")
                        amount_pattern = r"\*\*Amount\*\*: (\d+)"
                        sender_pattern = r"\*\*Sender\*\*: <@(\d+)>"
                        amount = int(re.search(amount_pattern, embed_content.description).group(1))
                        sender = int(re.search(sender_pattern, embed_content.description).group(1))
                        sender_rewards = 0.001 * amount * 0.2
                        s_uname = await self.bot.fetch_user(sender)

                        # Create the embed for the casino bet transaction details
                        embed = nextcord.Embed(
                            title="Transaction : Casino Bet",
                            description=(
                                f"**Sender** : {s_uname}\n**Amount** : {amount} ✨\n\n"
                                f"**Total Yield** : {0.001 * amount} ✨\n**Sender Reward** : {sender_rewards} ✨"
                            )
                        )
                        embed.set_footer(text=timestamp, icon_url=self.bot.user.avatar)

                        # Send the embed for the casino bet transaction
                        await interaction.response.send_message(embed=embed,ephemeral=True)

def setup(bot):
    """Setup the cog."""
    bot.add_cog(SlashCommand(bot))
