import os
import datetime
from dotenv import load_dotenv

load_dotenv()

DEBUG = False
TESTING = False
TEST = 'from root config.py'
MONGO_URL = os.getenv('MONGO_DB_URL')
MONGO_DB_NAME = 'splash'
REMEMBER_COOKIE_PATH = '/api'
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1,)
