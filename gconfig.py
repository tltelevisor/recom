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

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
PHONE_NUMBER= os.environ.get("PHONE_NUMBER")
NAME = os.environ.get("NAME")

CHLST_URL='http://localhost:8384/chlst'
SVMESS_URL='http://localhost:8384/svmess'
MSG_LIMIT = 1

