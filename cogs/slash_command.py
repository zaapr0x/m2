import discord
from discord import app_commands
from discord.ext import commands
import re
from controlers import db
from api import API
from discord.ui import Button, View


class Slash_Command(commands.Cog, db):
    """
    Slash Command class that provides various interaction commands
    for transaction scanning, leaderboards, dashboard, yield claims,
    and yield distribution.
    """

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.db = db()
        self.api = API()

    @app_commands.command(
        name="txs-scan", description="View transaction details using transaction ID"
    )
    async def txs(self, interaction: discord.Interaction, txid: str):
        """
        Command to scan transactions by transaction ID and display details
        to the user if found in the specific transactions channel.
        """
        channel_name = "💸┆transactions"
        channel = None

        # Find the transactions channel across all guilds
        for guild in self.bot.guilds:
            for c in guild.channels:
                if c.name.lower() == channel_name.lower():
                    channel = c
                    break
            if channel:
                break

        # Exit if the channel is not found
        if not channel:
            print(f"Failed to find channel: {channel_name}")
            return

        # Retrieve messages from the specified channel
        messages = [msg async for msg in channel.history(limit=None)]

        # Filter messages containing the transaction ID within embeds
        embed_messages = [
            msg
            for msg in messages
            if any(embed.description.find(txid) != -1 for embed in msg.embeds)
        ]

        # If matching messages found, process each for display
        if embed_messages:
            print(
                f'Found {len(embed_messages)} messages with embeds containing "{txid}"'
            )
            for msg in embed_messages:
                dict_msg = msg.embeds[0].to_dict()

                # Process tip transactions
                if dict_msg["title"] == "Transaction: Tip":
                    parse_msg = re.findall(
                        r"\*\*\w+\*\*:(.*)", dict_msg["description"].replace(" ", "")
                    )
                    sender = re.search(r"<@([0-9]+)>", parse_msg[1]).group(1)
                    receiver = re.search(r"<@([0-9]+)>", parse_msg[3]).group(1)
                    amount = parse_msg[0]
                    tx_id = parse_msg[5]

                    # Create embed for transaction details
                    embed = discord.Embed(
                        description=f"**Receiver** : <@{receiver}>\n**Sender** : <@{sender}>\n**Amount** :  {amount} :sparkles: \n**txid** : {tx_id}\n\n**Reward**:\n\n<@{sender}> : **{0.001 * float(amount) * 0.8}** ✨\n<@{receiver}> : **{0.001 * float(amount) * 0.2}** ✨",
                        colour=0xFDB73F,
                    )
                    embed.set_author(name="Transaction Details")
                    await interaction.response.send_message(embed=embed)

                # Process casino bet transactions
                elif dict_msg["title"] == "Transaction: Casino Bet":
                    parse_msg = re.findall(
                        r"\*\*\w+\*\*:(.*)", dict_msg["description"].replace(" ", "")
                    )
                    spend = parse_msg[0]
                    sender = re.search(r"<@([0-9]+)>", parse_msg[1]).group(1)

                    embed = discord.Embed(
                        description=f"**Receiver** : Casino Bet\n**Sender** : <@{sender}>\n**Amount** :  {spend} :sparkles: \n**txid** : {txid}\n\n**Reward**:\n\n<@{sender}> : **{0.001 * float(spend) * 0.8}** ✨\n",
                        colour=0xFDB73F,
                    )
                    embed.set_author(name="Transaction Details")
                    await interaction.response.send_message(embed=embed)
        else:
            print(f'No messages found with embeds containing "{txid}"')

    @app_commands.command(
        name="tipper-leaderboard", description="Show top tipper leaderboard"
    )
    async def tipper_leaderboard(self, interaction: discord.Interaction):
        """
        Command to display a leaderboard of the top users who have spent points on tips.
        """
        leaderboard = self.db.leaderboard()
        sorted_data = sorted(leaderboard, key=lambda x: x["tip_spend"], reverse=True)

        embed = discord.Embed(colour=0x29C2FF)
        embed.set_author(
            name="Tipper Leaderboard",
            icon_url="https://i.ibb.co/KFgSWdb/ezgif-1-2f25589644.gif",
        )

        # Build leaderboard description
        leaderboard_description = "Top Users Spending Points on Tips\n\n"
        for i, item in enumerate(sorted_data):
            name = await self.bot.fetch_user(item["user_id"])
            leaderboard_description += f"**{i+1}** {name} - {item['tip_spend']} ✨\n"
        embed.description = leaderboard_description

        await interaction.response.send_message(embed=embed, ephemeral=False)

    @app_commands.command(
        name="yield-leaderboard", description="Show the top yield earners"
    )
    async def yield_leaderboard(self, interaction: discord.Interaction):
        """
        Command to display a leaderboard of users who have earned the most yield.
        """
        leaderboard = self.db.leaderboard()
        sorted_data = sorted(leaderboard, key=lambda x: x["yield_earned"], reverse=True)

        embed = discord.Embed(colour=0x29C2FF)
        embed.set_author(
            name="Earned Yield Leaderboard",
            icon_url="https://i.ibb.co/KFgSWdb/ezgif-1-2f25589644.gif",
        )

        leaderboard_description = "Top Users Earned Yield\n\n"
        for i, item in enumerate(sorted_data):
            name = await self.bot.fetch_user(item["user_id"])
            leaderboard_description += f"**{i+1}** {name} - {item['yield_earned']} ✨\n"
        embed.description = leaderboard_description

        await interaction.response.send_message(embed=embed, ephemeral=False)

    @app_commands.command(name="dashboard", description="Show user's dashboard")
    async def dashboard(self, interaction: discord.Interaction):
        """
        Command to display a dashboard with the user's balance, yield, and tip stats.
        """
        if interaction.type == discord.InteractionType.application_command:
            view = View()
            user = interaction.user
            user_data = self.db.check_users(str(user.id))
            check_balance = self.api.get_user_balance(user.id)
            balance = round(
                float(
                    check_balance["data"]["tokens"]
                    if check_balance["status"] == 200
                    else 0
                )
            )

            if user_data["status"]:
                # Display user's stats if registered
                yields = round(float(user_data["yield_earned"]))
                unclaimed_yields = float(user_data["unclaimed_yield"])
                tips_given = float(user_data["tip_spend"])
                tips_received = float(user_data["tip_receive"])
                desc = (
                    f"User Balance\n✨ **{balance}** Points\n\nYields\n"
                    f"✨ **{unclaimed_yields}** Unclaimed Yields\n✨ **{yields}** Yields Earned So Far\n\nUser Stats\n"
                    f"✨ **{tips_received}** Tip Received\n✨ **{tips_given}** Tip Given"
                )

                embed = discord.Embed(
                    title=f"{user.name}'s Dashboard", description=desc, colour=0x29C2FF
                )
                embed.set_thumbnail(url=user.display_avatar)

                claim_yield = Button(
                    label="Claim Unclaimed Yields", style=discord.ButtonStyle.blurple
                )
                claim_yield.callback = self.claim_yield
                view.add_item(claim_yield)

                await interaction.response.send_message(embed=embed, view=view)
            else:
                # Display error if the user is not registered
                embed = discord.Embed(
                    title="Something Went Wrong",
                    colour=0x29C2FF,
                    description="You are not registered on system.\nto register you must do atleast one transaction, like giving tip or casino bets.",
                )
                await interaction.response.send_message(embed=embed)

    async def claim_yield(self, interaction: discord.Interaction):
        """
        Command callback to allow users to claim unclaimed yields.
        """
        claimable_yield = float(
            self.db.check_users(str(interaction.user.id))["unclaimed_yield"]
        )

        if claimable_yield > 0:
            embed = discord.Embed(
                title="Unclaimed Yield Too Low!",
                description="Your unclaimed yield is too low to claim! Minimum 1 ✨ To Claim",
            )
            embed.set_image(
                url="https://media1.tenor.com/m/riKvVZ2Et-cAAAAd/dumb-huh.gif"
            )
            await interaction.response.edit_message(embed=embed, view=None)
        elif claimable_yield == 0:
            embed = discord.Embed(
                title="Nothing to Claim!",
                description="You have no unclaimed yields to claim!",
            )
            embed.set_image(
                url="https://media1.tenor.com/m/riKvVZ2Et-cAAAAd/dumb-huh.gif"
            )
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            check_balance = self.api.get_user_balance(interaction.user.id)
            balance = (
                check_balance["data"]["tokens"] if check_balance["status"] == 200 else 0
            )
            update_user_balance = self.api.update_balance(
                interaction.user.id, round(claimable_yield)
            )

            if update_user_balance["status"] == 200:
                # Update the user's yield in the database and notify
                id = str(interaction.user.id)
                self.db.update_data(id, {"unclaimed_yield": "0"})
                embed = discord.Embed(
                    title="Yield Claimed!",
                    description=f"**+ {claimable_yield} ✨** From Unclaimed Yield",
                )
                await interaction.response.edit_message(embed=embed, view=None)

    @app_commands.command(
        name="distribute-yield", description="Distribute yield rewards to users"
    )
    async def distribute_yield(self, interaction: discord.Interaction):
        """
        Command to distribute yield rewards to all registered users.
        """
        view = View()
        pool_balance = self.db.get_pool("yield")

        if pool_balance != 0:
            user = self.db.get_user()
            desc = f"Users: {len(user)}"
            embed = discord.Embed(
                title="Distribute Yield to Users", description=desc, colour=0x29C2FF
            )

            # Confirmation buttons for yield distribution
            yes_button = Button(label="Confirm", style=discord.ButtonStyle.green)
            yes_button.callback = self.yes_button

            no_button = Button(label="Cancel", style=discord.ButtonStyle.red)
            no_button.callback = self.no_button

            view.add_item(yes_button)
            view.add_item(no_button)

            await interaction.response.send_message(embed=embed, view=view)
        else:
            embed = discord.Embed(
                title="Failed! Insufficient Yield Balance",
                description="Please add yield balance first.\n\nType `!menu` and click the balance button.",
                colour=0x29C2FF,
            )
            embed.set_image(
                url="https://media1.tenor.com/m/o6_Suc3YJq4AAAAC/no-money-please.gif"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    async def yes_button(self, interaction: discord.Interaction):
        """
        Callback to confirm and distribute yield evenly to all users.
        """
        pool_balance = self.db.get_pool("yield")
        total_users = self.db.get_user()
        calculate_yield = pool_balance / len(total_users) if total_users else 0

        if pool_balance != 0:
            # Distribute yield to each user
            for user_id in total_users:
                self.db.update_data(
                    str(user_id), {"unclaimed_yield": f"{calculate_yield}"}
                )
            self.db.update_pool_balance("yield", 0)

            embed = discord.Embed(
                title=f"Yield Distributed to {len(total_users)} Users",
                description=f"**+ {calculate_yield} ✨** per User",
            )
            await interaction.response.edit_message(embed=embed, view=None)

    async def no_button(self, interaction: discord.Interaction):
        """
        Callback to cancel yield distribution.
        """
        embed = discord.Embed(
            title="Cancelled!",
            description="Distribution of yield canceled.",
        )
        await interaction.response.edit_message(embed=embed, view=None)


async def setup(bot: commands.Bot) -> None:
    """Add Slash_Command cog to the bot."""
    await bot.add_cog(Slash_Command(bot))
