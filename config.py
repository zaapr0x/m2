from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

TOKEN=os.getenv('TOKEN')
DB_NAME=os.getenv('DB_NAME')
DRIP_API_KEY=os.getenv('DRIP_API_KEY')
BASE_URL=os.getenv('BASE_URL')
REALM_ID=os.getenv('REALM_ID')
REALM_POINT_ID=os.getenv('REALM_POINT_ID')

LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(message)s | %(name)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOGGER_LEVEL_STYLE={
        'info': {'color': 'cyan'},    # Color for INFO
        'debug': {'color': 'green'},  # Color for DEBUG
        'warning': {'color': 'yellow'}, # Color for WARNING
        'error': {'color': 'red'},    # Color for ERROR
        'critical': {'color': 'magenta', 'bold': True}  # Color for CRITICAL
}
LOGGER_FIELD_STYLE={
        'asctime': {'color': 'white'},  # Color for timestamp
        'levelname': {'color': 'blue', 'bold': True},  # Color for log level name
        'message': {'color': 'white'}   # Color for log message
    }