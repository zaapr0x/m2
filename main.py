import logging
import os
import platform
import discord
from discord.ext import commands
from dotenv import load_dotenv
import settings


class LoggingFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\x1b[38m",
        logging.INFO: "\x1b[34m",
        logging.WARNING: "\x1b[33m",
        logging.ERROR: "\x1b[31m",
        logging.CRITICAL: "\x1b[31m",
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "[{asctime}] [{levelname:<8}] {name}: {message}"
        return f"{log_color}{format}\x1b[0m".format(record)


class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned, intents=discord.Intents.all()
        )
        self.logger = logging.getLogger("discord_bot")
        self.logger.setLevel(logging.INFO)
        self._connected = False

        self.logger.info("Setting up logging")
        self.logger.addHandler(self._create_stream_handler())
        self.logger.addHandler(self._create_file_handler())

    def _create_stream_handler(self):
        handler = logging.StreamHandler()
        handler.setFormatter(self._create_formatter())
        return handler

    def _create_file_handler(self):
        handler = logging.FileHandler(
            filename="logs/discord.log", encoding="utf-8", mode="w"
        )
        handler.setFormatter(self._create_formatter())
        return handler

    def _create_formatter(self):
        formatter = logging.Formatter(
            "[{asctime}] [{levelname:<8}] {name}: {message}",
            "%Y-%m-%d %H:%M:%S",
            style="{",
        )
        return formatter

    async def setup_hook(self):
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("-------------------")
        self.logger.info("Loading cogs...")
        await self.load_extension("cogs.chatbot")
        await self.load_extension("cogs.listen_transaction")
        await self.load_extension("cogs.slash_command")
        await self.load_extension("cogs.menu")
        self.logger.info("cogs loaded!")
        self.logger.info("-------------------")

    async def on_ready(self):
        await self.wait_until_ready()
        await self.tree.sync()
        if not self._connected:
            self.logger.info("Bot is ready!" + self.user.name)
            self.logger.info("synced!")
        else:
            self.logger.info("Bot reconnected.")

    async def close(self):
        await super().close()


if __name__ == "__main__":
    load_dotenv(override=True)
    bot = DiscordBot()
    bot.run(settings.TOKEN)
