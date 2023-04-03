from flask import Markup, flash, url_for, redirect
from flask_admin import AdminIndexView, expose
from flask_admin.babel import gettext
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import FilterLike, FilterNotLike
from flask_admin.menu import MenuLink
from flask_login import current_user
from sqlalchemy.orm import load_only
from wtforms import validators, PasswordField
import hashlib
from app.models import *
from app import db


class MyAdminIndexView(AdminIndexView):
    def __init__(self):
        super().__init__(template='admin/dashboard.html', url='/admin')

    @expose('/')
    def dashboard(self):
        user_name = ''
        if not current_user.is_anonymous:
            user_name = current_user.name
        else:
            return redirect(url_for('admin_bp.login'))

        facilities = db.session.query(FacilitiesDB).order_by(FacilitiesDB.id).all()

        """ 
        SELECT checkup_headers.time_start, users.name, routes.name, facilities.name, checkup_headers.is_complete FROM checkup_headers
        JOIN users ON users.id=checkup_headers.user_id
        JOIN routes ON routes.id=checkup_headers.route_id
        JOIN facilities ON facilities.id=routes.facility_id
        WHERE facilities.id=1
        """
        tab_body = {}
        for facility in facilities:
            checkups_list = []
            checkups = db.session.query(CheckupHeadersDB.time_start, RoutesDB.name, UserDB.name,
                                        CheckupHeadersDB.is_complete, CheckupHeadersDB.id).\
                join(UserDB, UserDB.id == CheckupHeadersDB.user_id).\
                join(RoutesDB, RoutesDB.id == CheckupHeadersDB.route_id).\
                join(FacilitiesDB, FacilitiesDB.id == RoutesDB.facility_id).\
                filter(FacilitiesDB.id == facility.id).order_by(CheckupHeadersDB.time_start.desc()).limit(6).all()[::-1]
            for item in checkups:
                markup_string = "<a href='/admin/checkupheadersdb/%s'>%s</a>" % (item[4], item[0])
                item_to_tab = list(i for i in item)
                item_to_tab[0] = markup_string
                checkups_list.append(item_to_tab)
            tab_body.update({facility.name: checkups_list})

        tab_header = ['Дата',
                      'Маршрут',
                      'Сотрудник',
                      ]
        return self.render('admin/dashboard.html', user_name=user_name, tab_header=tab_header, tab_body=tab_body)


class MenuLinkLogout(MenuLink):
    def get_url(self):
        return url_for("admin_bp.logout")


class BaseCustomView(ModelView):
    list_template = 'admin/list_template.html'
    edit_template = 'admin/edit_template.html'
    create_template = 'admin/create_template.html'

    def is_accessible(self):
        try:
            current_role = RoleDB().query.get(current_user.role_id)
            if current_role.name == 'admin':
                return current_user.is_authenticated
            return False
        except AttributeError:
            return redirect(url_for("admin_bp.login"))

    @expose('/')
    def index_view(self):
        return super().index_view()

    def render(self, template, **kwargs):
        if current_user.is_authenticated:
            kwargs['user_name'] = current_user.name
            return super().render(template, **kwargs)
        return redirect(url_for("admin_bp.login"))


class UserCustom(BaseCustomView):
    column_list = ('name', 'login', 'roles', 'active')
    column_labels = dict(name='ФИО', login='Имя входа', roles='Роль', active='Активный')
    form_columns = ('name', 'login', 'roles', 'password', 'active')
    form_extra_fields = {
        'password': PasswordField('Пароль', [validators.DataRequired()])
    }
    column_filters = (FilterLike(RoleDB.name, 'Роль'),
                      FilterNotLike(RoleDB.name, 'Роль'),
                      'active')
    # column_descriptions = dict(name='Фамилия, имя и отчество')

    # Encrypt password before create/update
    def on_model_change(self, form, model, is_created):
        password = model.password
        hashed_password = hashlib.md5(password.encode('utf-8'))
        model.password = hashed_password.hexdigest()


class FacilitiesCustom(BaseCustomView):
    column_labels = dict(name='Наименование')


class PlantsCustom(BaseCustomView):
    column_labels = dict(facilities='Площадка', name='№ помещения', description_plant="Наименование помещения", description_params="Контролируемые параметры")
    column_filters = [FilterLike(FacilitiesDB.name, 'Площадка'),
                      FilterNotLike(FacilitiesDB.name, 'Площадка'),
                      'name']


class CheckupsCustom(BaseCustomView):
    can_delete = False
    can_edit = False
    can_create = False
    column_list = ('time_start', 'routes', 'users', 'is_complete')
    column_labels = dict(time_start='Начало обхода', routes='Маршрут', users='Сотрудник', is_complete='Обход завешен')
    column_filters = [FilterLike(UserDB.name, 'Сотрудник'),
                      FilterNotLike(UserDB.name, 'Сотрудник'),
                      FilterLike(RoutesDB.name, 'Маршрут'),
                      FilterNotLike(RoutesDB.name, 'Маршрут'),
                      'is_complete']

    def is_accessible(self):
        try:
            current_role = RoleDB().query.get(current_user.role_id)
            if current_role.name in ('admin', 'user_webapp'):
                return current_user.is_authenticated
            return False
        except AttributeError:
            return redirect(url_for("admin_bp.login"))

    # ***** Make url links and get new pages *****
    @staticmethod
    def _formatter(view, context, model, name):
        if model:
            markup_string = "<a href='%s'>%s</a>" % (model.id, model.time_start)
            return Markup(markup_string)
        else:
            return ""

    column_formatters = {"time_start": _formatter}

    @expose('/<checkup_id>')
    def checkup(self, checkup_id):
        """
        SELECT facilities.name, routes.name, users.name, checkup_headers.time_start, checkup_headers.time_finish, checkup_headers.is_complete
        FROM checkup_headers
        JOIN routes ON routes.id = checkup_headers.route_id
        JOIN facilities ON facilities.id = routes.facility_id
        JOIN users ON users.id = checkup_headers.user_id
        WHERE checkup_headers.id = 277
        """
        get_title = db.session.query(FacilitiesDB.name, RoutesDB.name, UserDB.name,
                                     CheckupHeadersDB.time_start, CheckupHeadersDB.time_finish, CheckupHeadersDB.is_complete).\
            join(RoutesDB, RoutesDB.id == CheckupHeadersDB.route_id).\
            join(FacilitiesDB, FacilitiesDB.id == RoutesDB.facility_id).\
            join(UserDB, UserDB.id == CheckupHeadersDB.user_id).filter(CheckupHeadersDB.id == checkup_id).first()

        list_title = list([f'Площадка: {get_title[0]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Маршрут: {get_title[1]}'])
        list_title.append(f'Исполнитель: {get_title[2]} ')
        list_title.append(f'Начало обхода: {get_title[3]} &nbsp;&nbsp;&nbsp; Конец обхода: {get_title[4]}')
        if get_title[5]:
            list_title.append('<p style="color:#008000">Обход завершен: Да</p>')
        else:
            list_title.append('<p style="color:#ff0000">Обход завершен: Нет</p>')

        tab_header = ['Время',
                      'Помещение/Оборудование',
                      'Параметр',
                      'Мин.значение',
                      'Текущее значение',
                      'Макс.значение',
                      'Ед.изм',
                      'Комментарий']

        """
        SELECT checkup_details.time_check, checkup_details.plant_name, checkup_details.val_name, checkup_details.val_min, 
        checkup_details.val_fact, checkup_details.val_max, checkup_details.unit_name, checkup_details.note from checkup_details
        WHERE checkup_details.header_id = 280
        """
        get_body = db.session.query(CheckupDetailsDB.time_check, CheckupDetailsDB.plant_name, CheckupDetailsDB.val_name,
                                    CheckupDetailsDB.val_min, CheckupDetailsDB.val_fact, CheckupDetailsDB.val_max,
                                    CheckupDetailsDB.unit_name, CheckupDetailsDB.note). \
            filter(CheckupDetailsDB.header_id == checkup_id)

        tab_body = []
        for item in get_body:
            if item[4] is not None and item[3] <= item[4] <= item[5]:
                tab_body.append([item[0], item[1], item[2], item[3], f'<a style="color:#008000">{item[4]}</a>',
                                 item[5], item[6], item[7]])
            elif item[4] is not None and not item[3] <= item[4] <= item[5]:
                tab_body.append([item[0], item[1], item[2], item[3], f'<a style="color:#ff0000">{item[4]}</a>',
                                 item[5], item[6], item[7]])
            else:
                tab_body.append(item)
        return self.render('admin/list_custom.html', title=list_title, tab_header=tab_header, tab_body=tab_body)


class NFCTagCustom(BaseCustomView):

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
                    flash(gettext("Уже есть активная NFC метка. Эта будет неактивной"), 'error')


class RoutesCustom(BaseCustomView):
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
    def get_routes_by_id(self, route_id):
        get_title = db.session.query(FacilitiesDB.name, RoutesDB.name).filter(RoutesDB.id == int(route_id)).first()
        title = [f'Площадка: {get_title[0]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Маршрут: {get_title[1]}']

        tab_header = ['Порядок обхода',
                      '№ помещения',
                      'Наименование помещения',
                      'Контролируемые параметры',
                      'NFC',
                      'Мин.значение',
                      'Макс.значение',
                      'Ед.изм']
        """
        SELECT route_links.order, plants.name, plants.description_plant, plants.description_params, 
        nfc_tag.nfc_serial, val_params.min_value, val_params.max_value, val_units.name FROM route_links 
        JOIN plants ON plants.id = route_links.plant_id
        LEFT JOIN nfc_tag ON nfc_tag.plant_id = route_links.plant_id
        LEFT JOIN val_params ON val_params.plant_id = plants.id
        LEFT JOIN val_units ON val_units.id = val_params.unit_id
        WHERE route_links.route_id = '6' AND route_links.active = 1
        ORDER BY route_links.order
        """
        # outerjoin(ValUnitsDB, ValUnitsDB.id == ValParamsDB.unit_id). \
        tab_body = db.session.query(RouteLinksDB.order, PlantsDB.name, PlantsDB.description_plant,
                                    PlantsDB.description_params, NfcTagDB.nfc_serial,
                                    ValParamsDB.min_value, ValParamsDB.max_value, ValUnitsDB.name). \
            join(PlantsDB, PlantsDB.id == RouteLinksDB.plant_id). \
            outerjoin(NfcTagDB, NfcTagDB.plant_id == RouteLinksDB.plant_id).\
            outerjoin(ValParamsDB, ValParamsDB.plant_id == PlantsDB.id).\
            outerjoin(ValUnitsDB, ValUnitsDB.id == ValParamsDB.unit_id).\
            filter(RouteLinksDB.route_id == route_id, RouteLinksDB.active == True).order_by(RouteLinksDB.order).all()

        return self.render('admin/list_custom.html', title=title, tab_header=tab_header, tab_body=tab_body)


class RouteLinksCustom(BaseCustomView):

    column_list = ('order', 'route', 'facilities', 'plant', 'active')
    column_labels = dict(order='Порядок', route='Маршрут', facilities='Площадка', plant='Помещение / Оборудование',
                          active='Активен')

    column_default_sort = 'order'
    column_filters = [FilterLike(RoutesDB.name, 'Маршрут'),
                      FilterNotLike(RoutesDB.name, 'Маршрут'),
                      FilterLike(FacilitiesDB.name, 'Площадка'),
                      FilterNotLike(FacilitiesDB.name, 'Площадка'),
                      'active']

    form_columns = ('facilities', 'route', 'plant', 'order', 'active')


class ValParamsCustom(BaseCustomView):
    column_list = ('name', 'facility', 'plant', 'min_value', 'max_value', 'units')
    column_labels = dict(name='Наименование', min_value='Мин.знач.', max_value='Мкас.знач.',
                         units='Ед.изм.', plant='Помещение / Oборудование', facility="Площадка")
    column_filters = [FilterLike(FacilitiesDB.name, 'Площадка'),
                      FilterNotLike(FacilitiesDB.name, 'Площадка'),
                      FilterLike(PlantsDB.name, 'Помещение/оборудование'),
                      FilterNotLike(PlantsDB.name, 'Помещение/оборудование')
                      ]

    form_columns = ('facility', 'plant', 'name', 'units', 'min_value', 'max_value')

class ValUnitsCustom(BaseCustomView):
    column_labels = dict(name='Наименование')
