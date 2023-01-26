from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app import app
from app.models import *


admin = Admin(app, name='Журнал обходов', template_mode='bootstrap3')


class UserCustom(ModelView):
    # column_list = (
    #     UserDB.name,
    #     UserDB.login,
    #     # UserDB.role_id,
    #     ('UserDB.roles', 'Roles'),
    #     UserDB.active
    # )
    column_labels = dict(name='ФИО', login='Имя входа', roles='Роль', active='Активный')
    column_exclude_list = ('password',)
    column_default_sort = 'name'
    # form_columns = (
    #     UserDB.name,
    #     UserDB.login
    # )

    # pass


admin.add_view(UserCustom(model=UserDB, name='Пользователи', session=db.session))
# admin.add_view(ModelView(model=UserDB, name='Пользователи', session=db.session))

admin.add_view(ModelView(model=NfcTagDB, name='NFC метки', session=db.session))
admin.add_view(ModelView(model=ValParamsDB, session=db.session, name='Параметры', category='Параметры'))
admin.add_view(ModelView(model=ValUnitsDB, session=db.session, name='Ед.измерения', category='Параметры'))
admin.add_view(ModelView(model=RoutesDB, session=db.session, name='Список маршрутов', category='Маршруты'))
admin.add_view(ModelView(model=RouteLinksDB, session=db.session, name='Точки маршрутов', category='Маршруты'))
admin.add_view(ModelView(model=FacilitiesDB, session=db.session, name='Площадки', category='Расположения'))
admin.add_view(ModelView(model=PlantsDB, session=db.session, name='Оборудование', category='Расположения'))
