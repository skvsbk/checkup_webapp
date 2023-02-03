from flask import Markup, flash
from flask_admin import expose
from flask_admin.babel import gettext
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import FilterLike, FilterNotLike
from wtforms import validators, PasswordField
from werkzeug.security import generate_password_hash
from app.models import *
from app import db


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
        """
        SELECT facilities.name, routes.name, users.name, checkups.t_start, checkups.t_end, checkups.completed
        FROM checkups
        JOIN routes ON routes.id = checkups.route_id
        JOIN facilities ON facilities.id = routes.facility_id
        JOIN users ON users.id = checkups.user_id
        WHERE checkups.id = 2
        """
        get_title = db.session.query(FacilitiesDB.name, RoutesDB.name, UserDB.name,
                                     CheckupsDB.t_start, CheckupsDB.t_end, CheckupsDB.completed).\
            join(RoutesDB, RoutesDB.id == CheckupsDB.route_id).\
            join(FacilitiesDB, FacilitiesDB.id == RoutesDB.facility_id).\
            join(UserDB, UserDB.id == CheckupsDB.user_id).filter(CheckupsDB.id == checkup_id).first()

        title = [f'Площадка: {get_title[0]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Маршрут: {get_title[1]}']
        title.append(f'Исполнитель: {get_title[2]} ')
        title.append(f'Начало обхода: {get_title[3]} &nbsp;&nbsp;&nbsp; Конец обхода: {get_title[4]}')
        if get_title[5]:
            title.append('<p style="color:#008000">Обход завершен: Да</p>')
        else:
            title.append('<p style="color:#ff0000">Обход завершен: Нет</p>')

        tab_header = ['Время',
                      'Помещение/Оборудование',
                      'Мин.значение',
                      'Текущее значение',
                      'Макс.значение',
                      'Ед.изм',
                      'Комментарий']

        """
        SELECT checks.t_check, plants.name, val_params.min_value, 
        val_checks.value, val_params.max_value, val_units.name, checks.note from checks 
        JOIN nfc_tag ON nfc_tag.id = checks.nfc_id
        JOIN plants ON plants.id = nfc_tag.plant_id
        LEFT JOIN val_params ON val_params.nfc_id = nfc_tag.id
        LEFT JOIN val_units ON val_units.id = val_params.unit_id
        LEFT JOIN val_checks ON val_checks.check_id = checks.id
        WHERE checks.checkup_id = 2
        """
        get_body = db.session.query(ChecksDB.t_check, PlantsDB.name, ValParamsDB.min_value, ValChecksDB.value,
                                        ValParamsDB.max_value, ValUnitsDB.name, ChecksDB.note). \
            join(NfcTagDB, NfcTagDB.id == ChecksDB.nfc_id).join(PlantsDB, PlantsDB.id == NfcTagDB.plant_id). \
            outerjoin(ValParamsDB, ValParamsDB.nfc_id == NfcTagDB.id). \
            outerjoin(ValUnitsDB, ValUnitsDB.id == ValParamsDB.unit_id). \
            outerjoin(ValChecksDB, ValChecksDB.check_id == ChecksDB.id). \
            filter(ChecksDB.checkup_id == checkup_id)

        tab_body = []
        for item in get_body:
            if item[3] is not None and item[2]<=item[3]<=item[4]:
                tab_body.append([item[0], item[1], item[2], f'<a style="color:#008000">{item[3]}</a>', item[4], item[5], item[6]])
            elif item[3] is not None and not item[2]<=item[3]<=item[4]:
                tab_body.append(
                    [item[0], item[1], item[2], f'<a style="color:#ff0000">{item[3]}</a>', item[4], item[5], item[6]])
            else:
                tab_body.append(item)
        print(tab_body)
        return self.render('admin/list_custom.html', title=title, tab_header=tab_header, tab_body=tab_body)


# *********************


class NFCTagCustom(ModelView):
    # Uncomment below in prod
    # can_delete = False
    column_list = ('nfc_serial', 'plant', 'active')
    column_labels = dict(nfc_serial='Серийной номер', plant='Помещение / оборудование', active='Активный')
    column_filters = [FilterLike(PlantsDB.name, 'Площадка/Оборудование'),
                      FilterNotLike(PlantsDB.name, 'Площадка/Оборудование'),
                      'nfc_serial',
                      'active']

    # Check active status if NFC tag already exists
    def on_model_change(self, form, model, is_created):
        get_status = db.session.query(NfcTagDB.active).filter(NfcTagDB.nfc_serial == model.nfc_serial,
                                                              NfcTagDB.id != model.id)

        for tag in get_status:
            for item in tag:
                if item:
                    model.active = False
                    flash(gettext("Уже есть активная NFC метка. Эта буде неактивной"), 'error')


class RoutesCustom(ModelView):
    column_list = ('name', 'facilities', 'active')
    column_labels = dict(name='Наименование маршрута', facilities='Площадка', active='Активен')
    column_filters = [FilterLike(FacilitiesDB.name, 'Площадка'),
                      FilterNotLike(FacilitiesDB.name, 'Площадка'),
                      'active']

# ***** Make url links and get new pages *****
    @staticmethod
    def _formatter(view, context, model, name):
        if model:
            markup_string = "<a href='%s'>%s</a>" % (model.id, model.name)
            return Markup(markup_string)
        else:
            return ""

    column_formatters = {"name": _formatter}

    @expose('/<route_id>')
    def user_det(self, route_id):
        get_title = db.session.query(FacilitiesDB.name, RoutesDB.name).filter(RoutesDB.id == int(route_id)).first()
        title = [f'Площадка: {get_title[0]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Маршрут: {get_title[1]}']

        tab_header = ['Порядок обхода',
                      'Помещение/Оборудование',
                      'NFC',
                      'Мин.значение',
                      'Макс.значение',
                      'Ед.изм']
        """
        SELECT route_links.order, plants.name, nfc_tag.nfc_serial, 
        val_params.min_value, val_params.max_value, val_units.name FROM route_links 
        JOIN nfc_tag ON nfc_tag.id = route_links.nfc_id
        JOIN plants ON plants.id = nfc_tag.plant_id
        LEFT JOIN val_params ON val_params.nfc_id = nfc_tag.id
        LEFT JOIN val_units ON val_units.id = val_params.unit_id
        WHERE route_links.route_id = '2' AND route_links.active = 1
        """
        # outerjoin(ValUnitsDB, ValUnitsDB.id == ValParamsDB.unit_id). \
        tab_body = db.session.query(RouteLinksDB.order, PlantsDB.name, NfcTagDB.nfc_serial,
                                    ValParamsDB.min_value, ValParamsDB.max_value, ValUnitsDB.name). \
            join(NfcTagDB, NfcTagDB.id == RouteLinksDB.nfc_id). \
            join(PlantsDB, PlantsDB.id == NfcTagDB.plant_id). \
            outerjoin(ValParamsDB, ValParamsDB.nfc_id == NfcTagDB.id).\
            outerjoin(ValUnitsDB, ValUnitsDB.id == ValParamsDB.unit_id).filter(RouteLinksDB.route_id == route_id,
                                                                               RouteLinksDB.active == True)
        print(tab_body)

        return self.render('admin/list_custom.html', title=title, tab_header=tab_header, tab_body=tab_body)

# *********************


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
