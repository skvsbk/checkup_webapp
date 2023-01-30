from flask_admin.contrib.sqla import ModelView
from wtforms import validators, PasswordField
from werkzeug.security import generate_password_hash


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


class NFCTagCustom(ModelView):
    column_list = ('nfc_serial', 'plant')
    column_labels = dict(nfc_serial='Серийной номер', plant='Помещение / оборудование')
    column_filters = ('plant', )


class ValParamsCustom(ModelView):
    column_list = ('name', 'min_value', 'max_value', 'units', 'nfctag')
    column_labels = dict(name='Наименование', min_value='Мин.знач.', max_value='Мкас.знач.',
                         units='Ед.изм.', nfctag='NFC tag')


class ValUnitsCustom(ModelView):
    column_labels = dict(name='Наименование')


class RoutesCustom(ModelView):
    column_list = ('name', 'facilities', 'active')
    column_labels = dict(name='Наименование', facilities='Площадка', active='Активен')
    column_filters = ('active', 'facilities')


class RouteLinksCustom(ModelView):
    column_list = ('routes', 'nfctag', 'order', 'active')
    column_labels = dict(routes='Маршрут', nfctag='NFC tag', order='Порядок', active='Активен')
    column_default_sort = 'order'
    column_filters = ('active', 'routes')


class FacilitiesCustom(ModelView):
    column_labels = dict(name='Наименование')


class PlantsCustom(ModelView):
    column_labels = dict(facilities='Площадка', name='Помещение / Оборудование')
    column_filters = ('facilities',)
