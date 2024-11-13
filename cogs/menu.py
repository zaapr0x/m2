import discord
from discord.ext import commands
from controlers import db
from discord.ui import Button, View
from discord import Embed
from api import API
from discord.ui.select import SelectOption, Select


class Menu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = db()
        self.api = API()

    # Listener for on_message events, triggers the main menu when "!menu" command is sent
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        if message.content.startswith("!menu"):
            # Embed for main menu
            embed = discord.Embed(
                title="m2 Bots Dashboard",
                description="🏦 **Pool Balance** - Show and Add Pool Balance\n🎰 **Lottery** - Roll Lottery Ticket",
                colour=0x29C2FF,
            )
            embed.set_image(
                url="https://codaio.imgix.net/docs/7Ee5YHYoEI/blobs/bl-TMsmmaMj4S/517b02bb9a5edb17dbfd4333c3bdf1c8e0d571857bb81fd429c1a3910b80fcd1379f9c5951f6a3727c8995eecbe75fecb1b402994b9cfdd8780faf39811288867811fd82382f6f67e3ee97abbcefc2e87f1aad43d297caa9440877c87f37f69f675a6814?auto=format%2Ccompress&fit=crop&w=1920&ar=4%3A1&crop=focalpoint&fp-x=0.5&fp-y=0.5&fp-z=1"
            )

            # Buttons for Balance and Lottery actions
            balance = Button(label="🏦 Balance", style=discord.ButtonStyle.blurple)
            balance.callback = self.balance_callback

            lottery = Button(label="🎰 Lottery Roll", style=discord.ButtonStyle.blurple)
            lottery.callback = self.lottery_callback

            view = View(timeout=None)
            view.add_item(balance)
            view.add_item(lottery)
            await message.channel.send(embed=embed, view=view)

    # Callback for Balance button, displays balance details and options to add funds
    async def balance_callback(self, interaction: discord.Interaction):
        view = View()

        # Buttons for adding to pool and yield balances
        add_pool_balance = Button(
            label="🎰 Add Lottery Balance", style=discord.ButtonStyle.blurple
        )
        add_pool_balance.callback = self.add_pool_balance

        add_tip_balance = Button(
            label="💸 Add Yield Balance", style=discord.ButtonStyle.blurple
        )
        add_tip_balance.callback = self.add_tip_balance

        view.add_item(add_pool_balance)
        view.add_item(add_tip_balance)

        # Embed displaying current pool balances
        embed = discord.Embed(
            description=f"Lottery Balance: **{self.db.get_pool('lottery')}** ✨\nYield Pool: **{self.db.get_pool('yield')}** ✨"
        )
        embed.set_author(name="Pool Balance")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    # Callback for adding to lottery pool balance
    async def add_pool_balance(self, interaction: discord.Interaction):
        view = View()

        # Dropdown options for adding balance amounts
        dropdown = Select(
            options=[
                SelectOption(label=str(amount), description=f"add {amount} ✨")
                for amount in [
                    500,
                    1000,
                    2000,
                    5000,
                    10000,
                    20000,
                    50000,
                    100000,
                    200000,
                    500000,
                    1000000,
                ]
            ],
            min_values=1,
            max_values=1,
        )
        dropdown.callback = lambda i: self.dropdown_callback(i, 1)
        view.add_item(dropdown)

        # Embed for adding lottery balance
        embed = discord.Embed(description="Select Amount to Add To Lottery Balance")
        embed.set_author(
            name="Add Lottery Balance",
            icon_url="https://i.ibb.co/KFgSWdb/ezgif-1-2f25589644.gif",
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    # Callback for adding to yield balance
    async def add_tip_balance(self, interaction: discord.Interaction):
        view = View()

        # Dropdown options for adding yield balance
        dropdown = Select(
            options=[
                SelectOption(label=str(amount), description=f"add {amount} ✨")
                for amount in [
                    500,
                    1000,
                    2000,
                    5000,
                    10000,
                    20000,
                    50000,
                    100000,
                    200000,
                    500000,
                    1000000,
                ]
            ],
            min_values=1,
            max_values=1,
        )
        dropdown.callback = lambda i: self.dropdown_callback(i, 2)
        view.add_item(dropdown)

        # Embed for adding yield balance
        embed = discord.Embed(description="Select Amount to Add To Reward Balance")
        embed.set_author(
            name="Add Yield Balance",
            icon_url="https://i.ibb.co/KFgSWdb/ezgif-1-2f25589644.gif",
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    # Callback for Lottery button, allows users to choose percentage of pool balance to distribute as prizes
    async def lottery_callback(self, interaction: discord.Interaction):
        view = View()
        pool_balance = self.db.get_pool("lottery")

        if pool_balance >= 100:
            dropdown = Select(
                options=[
                    SelectOption(
                        label=f"{round(percent * pool_balance)}",
                        description=f"{int(percent * 100)}% Off Pool Balance",
                    )
                    for percent in [
                        0.05,
                        0.1,
                        0.15,
                        0.2,
                        0.25,
                        0.3,
                        0.35,
                        0.4,
                        0.45,
                        0.5,
                        0.65,
                        0.7,
                        0.75,
                        0.8,
                        0.85,
                        0.9,
                        0.95,
                        1,
                    ]
                ],
                min_values=1,
                max_values=1,
            )
            dropdown.callback = lambda i: self.dropdown_callback(i, 3)
            view.add_item(dropdown)

            # Embed for lottery distribution selection
            embed = discord.Embed(
                title="Lottery Roll",
                description="Select the Amount You Want to Distribute as Lottery Prizes",
                colour=0x29C2FF,
            )
            embed.set_image(url="https://i.ibb.co.com/5h0LJ6C/200w.gif")
            await interaction.response.send_message(
                embed=embed, view=view, ephemeral=True
            )
        else:
            # Embed for insufficient pool balance
            embed = discord.Embed(
                title="Failed! Lottery Balance Too Low",
                description="Please Add Pool Balance First. Required >= 100",
                colour=0x29C2FF,
            )
            embed.set_image(
                url="https://media1.tenor.com/m/o6_Suc3YJq4AAAAC/no-money-please.gif"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    # Callback to show leaderboard based on tipping activity
    async def leaderboard_callback(self, interaction: discord.Interaction):
        leaderboard = self.db.leaderboard()
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(
            name="Tipper Leaderboard",
            icon_url="https://i.ibb.co/KFgSWdb/ezgif-1-2f25589644.gif",
        )

        # Generate leaderboard entries
        embed.description = "\n".join(
            f"**{i+1}** <@{item['user_id']}> - {item['total_tip_mats']} ✨"
            for i, item in enumerate(leaderboard)
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # Handles dropdown selections for balance updates and lottery winner selection
    async def dropdown_callback(self, interaction: discord.Interaction, method):
        value = int(interaction.data["values"][0])

        if method == 1:
            # Update lottery balance
            result = self.db.update_pool_balance(
                "lottery", self.db.get_pool("lottery") + value
            )
            if result:
                await interaction.response.send_message(
                    embed=Embed(
                        description=f"Successfully Added {value} ✨ To Lottery Pool Balance"
                    )
                )
            else:
                await interaction.response.send_message(
                    f"Failed to Add {value} To Lottery Pool Balance"
                )

        elif method == 2:
            # Update yield balance
            result = self.db.update_pool_balance(
                "yield", self.db.get_pool("yield") + value
            )
            if result:
                await interaction.response.send_message(
                    embed=Embed(
                        description=f"Successfully Added {value} ✨ To Yield Pool Balance"
                    )
                )
            else:
                await interaction.response.send_message(
                    f"Failed to Add {value} To Yield Pool Balance"
                )

        elif method == 3:
            # Select a random lottery winner
            winner = self.db.pick_random_user()
            if winner:
                balance_update = self.db.get_pool("lottery") - value
                self.db.update_pool_balance("lottery", round(balance_update))
                winner_user = self.bot.get_user(winner.user_id)
                if winner_user:
                    embed = Embed(
                        title=winner_user.name,
                        description=f"Congratulations <@{winner.user_id}> for winning {value} ✨!",
                        colour=0x29C2FF,
                    )
                    embed.set_image(
                        url="https://i.ibb.co/WFT6k6R/kisspng-shiba-inu-cryptocurrency-dogecoin-puppy-bitcoin-shiba-5b3ba7b1c7e2d2-1812628215306508017888.png"
                    )
                    await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Failed to pick a winner.")


async def setup(bot):
    await bot.add_cog(Menu(bot))
