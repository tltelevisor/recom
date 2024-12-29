import logging, os
logging.basicConfig(
    level=logging.INFO, filename='py.log',
    format="%(asctime)s - [%(levelname)s] %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
)
# logging.getLogger("httpx").setLevel(logging.WARNING) 
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER= os.getenv("PHONE_NUMBER")
NAME = os.getenv("NAME")

API_KEY = os.getenv("API_KEY")
OPENAI_MODEL = 'gpt-4o'

from os.path import abspath, dirname, join
BASE_DIR = dirname(abspath(__file__))
FILES_DIR = join(BASE_DIR, 'files')
DATABASE = join(BASE_DIR, 'recom.db')
CHANNELS = ['anatoly_nesmiyan', 'aviatorshina',]

MSG_LIMIT = 1