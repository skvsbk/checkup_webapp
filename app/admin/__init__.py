from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babelex import Babel
from wtforms import validators, PasswordField
from werkzeug.security import check_password_hash, generate_password_hash


from app import app
from app.models import *


admin = Admin(app, name='Журнал обходов', template_mode='bootstrap4')

babel = Babel(app)


@babel.localeselector
def get_locale():
    return 'en'

class UserCustom(ModelView):
    column_list = ('name', 'login', 'roles', 'password', 'active')
    column_labels = dict(name='ФИО', login='Имя входа', roles='Роль', active='Активный')
    form_columns = ('name', 'login', 'roles', 'password', 'active')
    form_extra_fields = {
        'password': PasswordField('Пароль', [validators.DataRequired()])
    }
    column_filters = ('login', 'roles', 'active')

    # Mangle password before create/update
    def on_model_change(self, form, model, is_created):
        hashed_password = generate_password_hash(model.password)
        model.password = hashed_password

# admin.add_view(ModelView(model=UserDB, name='Пользователи', session=db.session))
admin.add_view(UserCustom(model=UserDB, name='Пользователи', session=db.session,
                          menu_icon_type='fa', menu_icon_value='fa-users'))
admin.add_view(ModelView(model=NfcTagDB, session=db.session, name='NFC метки',
                         menu_icon_type='fa', menu_icon_value='fa-tags'))
admin.add_view(ModelView(model=ValParamsDB, session=db.session, name='Параметры',
                         category='Параметры', menu_icon_type='fa', menu_icon_value='fa-sliders'))
admin.add_view(ModelView(model=ValUnitsDB, session=db.session, name='Ед.измерения',
                         category='Параметры', menu_icon_type='fa', menu_icon_value='fa-wrench'))
admin.add_view(ModelView(model=RoutesDB, session=db.session, name='Список маршрутов',
                         category='Маршруты', menu_icon_type='fa', menu_icon_value='fa-list'))
admin.add_view(ModelView(model=RouteLinksDB, session=db.session, name='Точки маршрутов',
                         category='Маршруты', menu_icon_type='fa', menu_icon_value='fa-dot-circle-o'))
admin.add_view(ModelView(model=FacilitiesDB, session=db.session, name='Площадки',
                         category='Расположения', menu_icon_type='fa', menu_icon_value='fa-map-o'))
admin.add_view(ModelView(model=PlantsDB, session=db.session, name='Оборудование',
                         category='Расположения', menu_icon_type='fa', menu_icon_value='fa-tachometer'))
