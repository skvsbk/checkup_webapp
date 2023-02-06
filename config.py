from datetime import timedelta


class Config(object):
    DEBUG = False
    TESTING = False

    # os.urandom(20).hex()
    SECRET_KEY = '3e8cd834f5e9657fe6ca26475b2f961ec53eb248'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:Ad147852@127.0.0.1:53000/checkup_ogi?charset=utf8mb4"
    # APPLICATION_ROOT = '/admin'
    # PREFERRED_URL_SCHEME = 'http'
    # SERVER_NAME = '127.0.0.1'
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    # Flask-admin
    FLASK_ADMIN_SWATCH = 'cerulean'


class ProductionConfig(Config):
    pass


class DebugConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
