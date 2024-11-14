import nextcord
from nextcord.ext import commands
from nextcord import Interaction, Embed
from nextcord.ui import Button, View, Modal, TextInput, Select
import json
from database.controlers import db


class AdminCommand(commands.Cog):
    """Admin-only commands for configuring and managing bot settings."""

    def __init__(self, bot):
        self.bot = bot
        self.db = db()

    def is_admin(self, interaction: Interaction) -> bool:
        """Returns True if the user has administrator permissions."""
        return interaction.user.guild_permissions.administrator

    @nextcord.slash_command(name="set-role-perms", description="Set role permissions to use admin commands.")
    async def set_role_perms(self, interaction: Interaction, role: nextcord.Role):
        if not self.is_admin(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        await self._add_role_permission(role)
        await interaction.response.send_message("✅ Role permissions set successfully.")

    async def _add_role_permission(self, role: nextcord.Role):
        """Helper function to add a role to the super_roles list in config."""
        with open("config.json", "r") as file:
            config = json.load(file)
        config["super_roles"].append(role.id)
        with open("config.json", "w") as file:
            json.dump(config, file, indent=4)

    @nextcord.slash_command(name="menu", description="Displays the admin menu.")
    async def menu(self, interaction: Interaction):
        roles = interaction.user.roles
        role_ids = [role.id for role in roles]
        super_roles = await self._get_super_roles(interaction)

        # Check if the user is an admin or has one of the super roles
        if not self.is_admin(interaction) and not any(role_id in super_roles for role_id in role_ids):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return
        
        # If the user has the right permissions, proceed with sending the menu
        await interaction.response.send_message(embed=self._create_menu_embed(), view=self._create_menu_view())

    async def _get_super_roles(self, interaction: Interaction):
        with open("config.json", "r") as file:
            config = json.load(file)
        return config["super_roles"]
    def _create_menu_embed(self) -> Embed:
        """Helper function to create the main menu embed."""
        return Embed(
            title="Admin Dashboard",
            description="🏦 Pool Balance - Show and Add Pool Balance\n🎰 Lottery - Roll Lottery Ticket\n💸 Distribute - Distribute Yield To All Users",
        ).set_image(url="https://codaio.imgix.net/docs/7Ee5YHYoEI/blobs/bl-TMsmmaMj4S/517b02bb9a5edb17dbfd4333c3bdf1c8e0d571857bb81fd429c1a3910b80fcd1379f9c5951f6a3727c8995eecbe75fecb1b402994b9cfdd8780faf39811288867811fd82382f6f67e3ee97abbcefc2e87f1aad43d297caa9440877c87f37f69f675a6814?auto=format%2Ccompress&fit=crop&w=1920&ar=4%3A1&crop=focalpoint&fp-x=0.5&fp-y=0.5&fp-z=1")

    def _create_menu_view(self) -> View:
        """Helper function to create the main menu view with buttons."""
        view = View()

        # Create buttons and set callbacks
        balance_button = Button(label="🏦 Pool Balance", style=nextcord.ButtonStyle.blurple)
        balance_button.callback = self.show_balance
        view.add_item(balance_button)

        lottery_button = Button(label="🎰 Lottery", style=nextcord.ButtonStyle.blurple)
        lottery_button.callback = self.start_lottery
        view.add_item(lottery_button)

        distribute_button = Button(label="💸 Distribute", style=nextcord.ButtonStyle.green)
        distribute_button.callback = self.distribute_yield
        view.add_item(distribute_button)
        return view

    async def show_balance(self, interaction: Interaction):
        yield_balance = self.db.get_pool_balance('yield')
        lottery_balance = self.db.get_pool_balance('lottery')
        
        embed = Embed(
            title="Pool Balance",
            description=f"✨ **Yield Balance**: {yield_balance}\n✨ **Lottery Balance**: {lottery_balance}"
        )
        view = self._create_balance_view()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    def _create_balance_view(self) -> View:
        """Creates the view for the Pool Balance section with buttons to add balances."""
        view = View()

        # Create buttons and set callbacks
        add_yield_button = Button(label="🏦 Add Yield Balance", style=nextcord.ButtonStyle.green)
        add_yield_button.callback = lambda i: self.add_balance(i, "yield")
        view.add_item(add_yield_button)

        add_lottery_button = Button(label="🎰 Add Lottery Balance", style=nextcord.ButtonStyle.green)
        add_lottery_button.callback = lambda i: self.add_balance(i, "lottery")
        view.add_item(add_lottery_button)

        return view

    async def add_balance(self, interaction: Interaction, balance_type: str):
        modal = Modal(title=f"Add {balance_type.capitalize()} Balance")
        modal.add_item(TextInput(label="Amount to add", required=True, custom_id=balance_type))
        modal.callback = lambda i: self.update_balance(i, balance_type)
        await interaction.response.send_modal(modal)

    async def update_balance(self, interaction: Interaction, balance_type: str):
        amount = int(interaction.data["components"][0]["components"][0]["value"])
        self.db.update_pool_balance(balance_type, amount)
        
        embed = Embed(
            title="Balance Updated",
            description=f"+ {amount} ✨ added to {balance_type.capitalize()} balance"
        )
        await interaction.response.edit_message(embed=embed, view=None)

    async def start_lottery(self, interaction: Interaction):
        lottery_balance = self.db.get_pool_balance('lottery')
        if lottery_balance < 100:
            await interaction.response.send_message(embed=self._create_low_balance_embed())
            return

        modal = Modal(title="Lottery Rewards")
        modal.add_item(TextInput(label=f"Current Lottery Balance: {lottery_balance}", required=True, custom_id="lottery_rewards"))
        modal.callback = lambda i: self.pick_winner(i, 'lottery_rewards')
        await interaction.response.send_modal(modal)

    def _create_low_balance_embed(self) -> Embed:
        """Creates an embed to notify the user of insufficient lottery balance."""
        return Embed(
            title="Balance Too Low",
            description="Balance too low. Please add more (minimum required: 100)."
        )

    async def pick_winner(self, interaction: Interaction, reward_type: str):
        reward_amount = int(interaction.data["components"][0]["components"][0]["value"])
        winner_id = self.db.get_random_user_id()

        self.db.update_pool_balance('lottery', -reward_amount)
        await self._send_winner_announcement(interaction, winner_id, reward_amount)

    async def _send_winner_announcement(self, interaction: Interaction, winner_id: int, reward_amount: int):
        """Creates and sends the lottery winner announcement embed with a channel selection dropdown."""
        view = View()
        view.add_item(ChannelSelect(interaction.guild.text_channels, winner_id, reward_amount))
        
        embed = Embed(
            title="Winner Selected",
            description=f"🎉 Congratulations to <@{winner_id}>! Please select a channel to make an announcement."
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def distribute_yield(self, interaction: Interaction):
        yield_balance = self.db.get_pool_balance('yield')
        user_id = self.db.get_all_user_ids()
        if yield_balance < 100:
            await interaction.response.send_message(embed=self._create_low_balance_embed(), ephemeral=True)
            return
        view = View()

        # Create buttons and set callbacks
        confirm_button = Button(label="🗸", style=nextcord.ButtonStyle.green)
        confirm_button.callback = self.confirm_button
        view.add_item(confirm_button)

        cancel_button = Button(label="🗙", style=nextcord.ButtonStyle.red)
        cancel_button.callback = self.cancel_button
        view.add_item(cancel_button)

        embed = nextcord.Embed(title="Distribute Yield",
                      description=f"To : {len(user_id)} Users\nFor : {yield_balance} ✨\n\nYield Calculated : {yield_balance / len(user_id)} ✨ Per Users")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def confirm_button(self, interaction: Interaction):
        yield_balance = self.db.get_pool_balance('yield')
        user_id = self.db.get_all_user_ids()
        total_yield = yield_balance / len(user_id)
        for i in user_id:
            self.db.update_user_yield(i, total_yield, total_yield)

        # Deduct the yield balance    
        self.db.update_pool_balance('yield', -yield_balance)

        await interaction.response.send_message("Yield Distributed!", ephemeral=True)

    async def cancel_button(self, interaction: Interaction):
        await interaction.response.send_message("Distribution Cancelled!", ephemeral=True)
class ChannelSelect(Select):
    """Dropdown for selecting a channel to post the lottery winner announcement."""

    def __init__(self, channels, winner_id: int, reward_amount: int):
        options = [nextcord.SelectOption(label=channel.name, value=str(channel.id)) for channel in channels]
        super().__init__(placeholder="Select a channel...", options=options)
        self.winner_id = winner_id
        self.reward_amount = reward_amount

    async def callback(self, interaction: Interaction):
        selected_channel = interaction.guild.get_channel(int(self.values[0]))
        embed = Embed(
            title="Lottery Winner 🎉",
            description=f"Congratulations <@{self.winner_id}>! You've won {self.reward_amount} ✨.\nClaim your reward in the dashboard."
        ).set_image(url="https://media1.tenor.com/m/1vka8p6Kf4gAAAAd/sleep-money.gif")

        await selected_channel.send(embed=embed)
        await interaction.response.send_message("Announcement posted!", ephemeral=True)


def setup(bot):
    bot.add_cog(AdminCommand(bot))
