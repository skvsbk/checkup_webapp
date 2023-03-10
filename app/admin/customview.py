from flask import Markup, flash, url_for, redirect
from flask_admin import AdminIndexView, expose
from flask_admin.babel import gettext
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import FilterLike, FilterNotLike
from flask_admin.menu import MenuLink
from wtforms import validators, PasswordField
from werkzeug.security import generate_password_hash
from app.models import *
from app import db
from flask_login import current_user


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

        """ SELECT checkups.t_start, users.name, routes.name, facilities.name, checkups.completed FROM checkups
            JOIN users ON users.id=checkups.user_id
            JOIN routes ON routes.id=checkups.route_id
            JOIN facilities ON facilities.id=routes.facility_id
            WHERE facilities.id=1"""
        tab_body = {}
        for facility in facilities:
            checkups_list = []
            checkups = db.session.query(CheckupsDB.t_start, RoutesDB.name, UserDB.name,
                                        CheckupsDB.completed, CheckupsDB.id).\
                join(UserDB, UserDB.id == CheckupsDB.user_id).\
                join(RoutesDB, RoutesDB.id == CheckupsDB.route_id).\
                join(FacilitiesDB, FacilitiesDB.id == RoutesDB.facility_id).\
                filter(FacilitiesDB.id == facility.id).order_by(CheckupsDB.t_start.desc()).limit(6).all()[::-1]
            for item in checkups:
                markup_string = "<a href='/admin/checkupsdb/%s'>%s</a>" % (item[4], item[0])
                item_to_tab = list(i for i in item)
                item_to_tab[0] = markup_string
                checkups_list.append(item_to_tab)
            tab_body.update({facility.name: checkups_list})

        tab_header = ['????????',
                      '??????????????',
                      '??????????????????',
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
            if current_role.role_name == 'admin':
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
    column_labels = dict(name='??????', login='?????? ??????????', roles='????????', active='????????????????')
    form_columns = ('name', 'login', 'roles', 'password', 'active')
    form_extra_fields = {
        'password': PasswordField('????????????', [validators.DataRequired()])
    }
    column_filters = (FilterLike(RoleDB.role_name, '????????'),
                      FilterNotLike(RoleDB.role_name, '????????'),
                      'active')
    column_descriptions = dict(name='??????????????, ?????? ?? ????????????????')

    # Encrypt password before create/update
    def on_model_change(self, form, model, is_created):
        hashed_password = generate_password_hash(model.password)
        model.password = hashed_password


class FacilitiesCustom(BaseCustomView):
    column_labels = dict(name='????????????????????????')


class PlantsCustom(BaseCustomView):
    column_labels = dict(facilities='????????????????', name='?????????????????? / ????????????????????????')
    column_filters = [FilterLike(FacilitiesDB.name, '????????????????'),
                      FilterNotLike(FacilitiesDB.name, '????????????????'),
                      'name']


class CheckupsCustom(BaseCustomView):
    # Uncomment below in prod
    # can_delete = False
    # can_edit = False
    column_list = ('t_start', 'routes', 'users', 'completed')
    column_labels = dict(t_start='???????????? ????????????', routes='??????????????', users='??????????????????', completed='?????????? ??????????????')
    column_filters = [FilterLike(UserDB.name, '??????????????????'),
                      FilterNotLike(UserDB.name, '??????????????????'),
                      FilterLike(RoutesDB.name, '??????????????'),
                      FilterNotLike(RoutesDB.name, '??????????????'),
                      'completed']

    def is_accessible(self):
        try:
            current_role = RoleDB().query.get(current_user.role_id)
            if current_role.role_name in ('admin', 'user_webapp'):
                return current_user.is_authenticated
            return False
        except AttributeError:
            return redirect(url_for("admin_bp.login"))

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
    def checkup(self, checkup_id):
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

        list_title = list([f'????????????????: {get_title[0]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ??????????????: {get_title[1]}'])
        list_title.append(f'??????????????????????: {get_title[2]} ')
        list_title.append(f'???????????? ????????????: {get_title[3]} &nbsp;&nbsp;&nbsp; ?????????? ????????????: {get_title[4]}')
        if get_title[5]:
            list_title.append('<p style="color:#008000">?????????? ????????????????: ????</p>')
        else:
            list_title.append('<p style="color:#ff0000">?????????? ????????????????: ??????</p>')

        tab_header = ['??????????',
                      '??????????????????/????????????????????????',
                      '????????????????',
                      '??????.????????????????',
                      '?????????????? ????????????????',
                      '????????.????????????????',
                      '????.??????',
                      '??????????????????????']

        """
        SELECT checks.t_check, plants.name, val_params.name, val_params.min_value, 
        val_checks.value, val_params.max_value, val_units.name, checks.note from checks 
        JOIN nfc_tag ON nfc_tag.id = checks.nfc_id
        JOIN plants ON plants.id = nfc_tag.plant_id
        LEFT JOIN val_params ON val_params.nfc_id = nfc_tag.id
        LEFT JOIN val_units ON val_units.id = val_params.unit_id
        LEFT JOIN val_checks ON val_checks.check_id = checks.id
        WHERE checks.checkup_id = 2
        """
        get_body = db.session.query(ChecksDB.t_check, PlantsDB.name, ValParamsDB.name, ValParamsDB.min_value,
                                    ValChecksDB.value, ValParamsDB.max_value, ValUnitsDB.name, ChecksDB.note). \
            join(NfcTagDB, NfcTagDB.id == ChecksDB.nfc_id).join(PlantsDB, PlantsDB.id == NfcTagDB.plant_id). \
            outerjoin(ValParamsDB, ValParamsDB.nfc_id == NfcTagDB.id). \
            outerjoin(ValUnitsDB, ValUnitsDB.id == ValParamsDB.unit_id). \
            outerjoin(ValChecksDB, ValChecksDB.check_id == ChecksDB.id). \
            filter(ChecksDB.checkup_id == checkup_id)

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
    column_labels = dict(nfc_serial='???????????????? ??????????', plant='?????????????????? / ????????????????????????', active='????????????????')
    column_filters = [FilterLike(PlantsDB.name, '????????????????/????????????????????????'),
                      FilterNotLike(PlantsDB.name, '????????????????/????????????????????????'),
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
                    flash(gettext("?????? ???????? ???????????????? NFC ??????????. ?????? ?????????? ????????????????????"), 'error')


class RoutesCustom(BaseCustomView):
    column_list = ('name', 'facilities', 'active')
    column_labels = dict(name='???????????????????????? ????????????????', facilities='????????????????', active='??????????????')
    column_filters = [FilterLike(FacilitiesDB.name, '????????????????'),
                      FilterNotLike(FacilitiesDB.name, '????????????????'),
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
    def user_get(self, route_id):
        get_title = db.session.query(FacilitiesDB.name, RoutesDB.name).filter(RoutesDB.id == int(route_id)).first()
        title = [f'????????????????: {get_title} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ??????????????: {get_title[1]}']

        tab_header = ['?????????????? ????????????',
                      '??????????????????/????????????????????????',
                      'NFC',
                      '??????.????????????????',
                      '????????.????????????????',
                      '????.??????']
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
            join(NfcTagDB, NfcTagDB.id == RouteLinksDB.nfc_id).join(PlantsDB, PlantsDB.id == NfcTagDB.plant_id). \
            outerjoin(ValParamsDB, ValParamsDB.nfc_id == NfcTagDB.id).\
            outerjoin(ValUnitsDB, ValUnitsDB.id == ValParamsDB.unit_id).\
            filter(RouteLinksDB.route_id == route_id, RouteLinksDB.active == True).order_by(RouteLinksDB.order).all()

        return self.render('admin/list_custom.html', title=title, tab_header=tab_header, tab_body=tab_body)


class RouteLinksCustom(BaseCustomView):
    column_list = ('routes', 'nfctag', 'order', 'active')
    column_labels = dict(routes='??????????????', nfctag='NFC tag', order='??????????????', active='??????????????')
    column_default_sort = 'order'
    column_filters = [FilterLike(RoutesDB.name, '??????????????'),
                      FilterNotLike(RoutesDB.name, '??????????????'),
                      'active']


class ValParamsCustom(BaseCustomView):
    column_list = ('name', 'min_value', 'max_value', 'units', 'nfctag')
    column_labels = dict(name='????????????????????????', min_value='??????.????????.', max_value='????????.????????.',
                         units='????.??????.', nfctag='NFC tag')


class ValUnitsCustom(BaseCustomView):
    column_labels = dict(name='????????????????????????')
