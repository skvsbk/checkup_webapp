from flask import Markup
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import FilterLike, FilterNotLike
from wtforms import validators, PasswordField
from werkzeug.security import generate_password_hash
from app.models import UserDB, RoleDB, RoutesDB, FacilitiesDB, PlantsDB


class UserCustom(ModelView):
    column_list = ('name', 'login', 'roles', 'active')
    column_labels = dict(name='ФИО', login='Имя входа', roles='Роль', active='Активный')
    form_columns = ('name', 'login', 'roles', 'password', 'active')
    form_extra_fields = {
        'password': PasswordField('Пароль', [validators.DataRequired()])
    }
    column_filters = (FilterLike(RoleDB.name, 'Роль'),
                      FilterNotLike(RoleDB.name, 'Роль'),
                      'active')
    column_descriptions = dict(name='Фамилия, имя и отчество')
    # can_view_details = True
    # column_searchable_list = ("name",)
    # column_editable_list = ("name",)
    # column_details_list = ("name",)
    # form_create_rules = ("name",)

    # Mangle password before create/update
    def on_model_change(self, form, model, is_created):
        hashed_password = generate_password_hash(model.password)
        model.password = hashed_password


class FacilitiesCustom(ModelView):
    column_labels = dict(name='Наименование')


class PlantsCustom(ModelView):
    column_labels = dict(facilities='Площадка', name='Помещение / Оборудование')
    column_filters = [FilterLike(FacilitiesDB.name, 'Площадка'),
                      FilterNotLike(FacilitiesDB.name, 'Площадка'),
                      'name']


class CheckupsCustom(ModelView):
    # Uncomment below in prod
    # can_delete = False
    # can_edit = False
    column_list = ('t_start', 'routes', 'users', 'completed')
    column_labels = dict(t_start='Начало обхода', routes='Маршрут', users='Сотрудник', completed='Обход завешен')
    column_filters = [FilterLike(UserDB.name, 'Сотрудник'),
                      FilterNotLike(UserDB.name, 'Сотрудник'),
                      FilterLike(RoutesDB.name, 'Маршрут'),
                      FilterNotLike(RoutesDB.name, 'Маршрут'),
                      'completed']

# ***** Make url links and get new pages *****
    @staticmethod
    def _formatter(view, context, model, name):
        if model:
            markup_string = "<a href='%s'>%s</a>" % (model.id, model.t_start)
            return Markup(markup_string)
        else:
            return ""

    column_formatters = {"t_start": _formatter}

    @expose('/<checkup_id>')
    def user_det(self, checkup_id):
        return self.render('admin/help.html', id=checkup_id)

# *********************


class NFCTagCustom(ModelView):
    column_list = ('nfc_serial', 'plant')
    column_labels = dict(nfc_serial='Серийной номер', plant='Помещение / оборудование')
    column_filters = [FilterLike(PlantsDB.name, 'Площадка'),
                      FilterNotLike(PlantsDB.name, 'Площадка')]


class RoutesCustom(ModelView):
    column_list = ('name', 'facilities', 'active')
    column_labels = dict(name='Наименование маршрута', facilities='Площадка', active='Активен')
    column_filters = [FilterLike(FacilitiesDB.name, 'Площадка'),
                      FilterNotLike(FacilitiesDB.name, 'Площадка'),
                      'active']


class RouteLinksCustom(ModelView):
    column_list = ('routes', 'nfctag', 'order', 'active')
    column_labels = dict(routes='Маршрут', nfctag='NFC tag', order='Порядок', active='Активен')
    column_default_sort = 'order'
    column_filters = [FilterLike(RoutesDB.name, 'Маршрут'),
                      FilterNotLike(RoutesDB.name, 'Маршрут'),
                      'active']


class ValParamsCustom(ModelView):
    column_list = ('name', 'min_value', 'max_value', 'units', 'nfctag')
    column_labels = dict(name='Наименование', min_value='Мин.знач.', max_value='Мкас.знач.',
                         units='Ед.изм.', nfctag='NFC tag')


class ValUnitsCustom(ModelView):
    column_labels = dict(name='Наименование')
