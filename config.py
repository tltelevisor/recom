import logging, os

from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


logging.basicConfig(
    level=logging.INFO, filename='py.log',
    format="%(asctime)s - [%(levelname)s] %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
)
# logging.getLogger("httpx").setLevel(logging.WARNING) 
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
PHONE_NUMBER= os.environ.get("PHONE_NUMBER")
NAME = os.environ.get("NAME")

API_KEY = os.environ.get("API_KEY")
OPENAI_MODEL = 'gpt-4o'

from os.path import abspath, dirname, join
BASE_DIR = dirname(abspath(__file__))
FILES_DIR = join(BASE_DIR, 'files')
# DATABASE = join(BASE_DIR, 'recom.db')
DATABASE = os.environ.get("DATABASE")
CHANNELS = ['anatoly_nesmiyan', 'aviatorshina',]

# Адрес сервера настройки фильтров
URL = os.environ.get("URL")
PORT = os.environ.get("PORT")

# Максимально количество сообщений, которое выбирается за один запрос из канала
# (этот параментр для сервиса getremserver.py)
MSG_LIMIT = 5

# С задержкой на такое количество часов будут удалены сообщения 
HOURS_TO_LIVE = 24
