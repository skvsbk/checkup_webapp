import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('./.env_db'))
DATABASE_URL = os.getenv('DATABASE_URL')



class Config(object):
    DEBUG = False
    TESTING = False

    # os.urandom(20).hex()
    SECRET_KEY = '3e8cd834f5e9657fe6ca26475b2f961ec53eb248'
    # "mysql+pymysql://root:Ad147852@127.0.0.1:53000/checkup_ogi?charset=utf8mb4"
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

    # Flask-admin
    FLASK_ADMIN_SWATCH = 'cerulean'


class ProductionConfig(Config):
    pass


class DebugConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
