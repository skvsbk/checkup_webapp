from flask import Flask
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from app.routes import main_bp


app = Flask(__name__)
# if app.config['ENV'] == 'production':
#     app.config.from_object('config.ProductionConfig')
# elif app.config['ENV'] == 'testing':
#     app.config.from_object('config.TestingConfig')
# else:
#     app.config.from_object('config.DebugConfig')
app.config.from_object('config.DebugConfig')


db = SQLAlchemy(app)

# Проверка хэша пароля

# from app.models import UserDB
# from werkzeug.security import generate_password_hash, check_password_hash
#
# with app.app_context():
#     a = db.session.query(UserDB.password).filter(UserDB.login == 'admin').first()
#     print(a)
#     print(check_password_hash(a[0], 'admin'))
#     b = generate_password_hash('admin')
#     print(b)
#     print(check_password_hash(b, 'admin'))


app.register_blueprint(main_bp, url_prefix="/")

from app.admin.routes import admin_bp
app.register_blueprint(admin_bp, url_prefix="/admin")


