
class Config(object):
    DEBUG = False
    TESTING = False

    SECRET_KEY = 'sjdkghfluwhefihj9134hgiuh8o173yt'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:Ad147852@127.0.0.1:53000/checkup_ogi?charset=utf8mb4"

    # Flask-admin
    FLASK_ADMIN_SWATCH = 'cerulean'



class ProductionConfig(Config):
    pass


class DebugConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
