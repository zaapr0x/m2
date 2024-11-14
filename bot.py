import nextcord
from nextcord.ext import commands
import logging
import os
import config
import coloredlogs
import platform
from database.models import initialize_tables
# Set up logging with the custom format
logging.basicConfig(
    format=config.LOG_FORMAT,
    datefmt=config.DATE_FORMAT,
    level=logging.INFO
)

# Set up colored logging
coloredlogs.install(
    level='INFO',               # Default log level to show
    fmt=config.LOG_FORMAT,      # Log format (from config)
    datefmt=config.DATE_FORMAT, # Date format (from config)
    level_styles=config.LOGGER_LEVEL_STYLE,
    field_styles=config.LOGGER_FIELD_STYLE
)

logger = logging.getLogger(__name__)
logging.getLogger('nextcord').setLevel(logging.WARNING)

class MyBot(commands.Bot):
    def __init__(self):
        intents = nextcord.Intents.all()
        intents.message_content = True
        
        # Initialize the bot with a prefix and intents
        super().__init__(command_prefix="!", intents=intents)
        
        # Load cogs
        self.load_all_cogs()

    async def on_ready(self):
        """Event fired when the bot has successfully logged in and is ready."""
        logger.info(f'Logged in as {self.user.name} ({self.user.id})')
        
        # Set the bot's activity (e.g., playing a game)
        activity = nextcord.Game(name="Playing with cogs!")
        await self.change_presence(activity=activity)
        
        # Log to confirm the bot is ready
        logger.info(f'{self.user} has connected to Discord!')

    async def on_error(self, event, *args, **kwargs):
        """Event fired when an error occurs."""
        logger.error(f'Error in event {event}: {args} {kwargs}')

    def load_all_cogs(self):
        logger.info(f"nextcord API version: {nextcord.__version__}")
        logger.info(f"Python version: {platform.python_version()}")
        logger.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        logger.info("-------------------")
        logger.info("Loading cogs...")
        
        """Load all cogs dynamically from the cogs directory."""
        cog_files = os.listdir('./cogs')
        loaded_cogs = 0
        failed_cogs = 0

        for filename in cog_files:
            if filename.endswith('.py'):
                cog_name = f'cogs.{filename[:-3]}'
                try:
                    self.load_extension(cog_name)
                    logger.info(f'Successfully loaded cog: {cog_name}')
                    loaded_cogs += 1
                except Exception as e:
                    logger.error(f'Failed to load cog {cog_name}: {e}')
                    failed_cogs += 1

        if loaded_cogs > 0:
            logger.info(f'{loaded_cogs} cog(s) loaded successfully.')
        if failed_cogs > 0:
            logger.error(f'{failed_cogs} cog(s) failed to load.')

# Create bot instance

logger.info('Check Database If Already Initialized')
if not os.path.exists(config.DB_NAME):
    logger.info('Initializing Database')
    initialize_tables()
    logger.info('Database Initialized')
    bot = MyBot()
    logger.info('Running Bot..')
    bot.run(config.TOKEN)
else:
    logger.info('Database Already Initialized')
    bot = MyBot()
    logger.info('Running Bot..')
    bot.run(config.TOKEN)