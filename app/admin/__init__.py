from flask_admin import Admin, AdminIndexView
from flask_admin.menu import MenuLink
from flask_babelex import Babel

from app import app
from app.models import *
from .customview import *


admin = Admin(app, name='Журнал обходов', template_mode='bootstrap4')

babel = Babel(app)


@babel.localeselector
def get_locale():
    return 'ru'


admin.add_view(UserCustom(model=UserDB, name='Пользователи', session=db.session,
                          menu_icon_type='fa', menu_icon_value='fa-users'))
admin.add_view(NFCTagCustom(model=NfcTagDB, session=db.session, name='NFC метки',
                            menu_icon_type='fa', menu_icon_value='fa-tags'))
admin.add_view(ValParamsCustom(model=ValParamsDB, session=db.session, name='Параметры',
                               category='Параметры', menu_icon_type='fa', menu_icon_value='fa-sliders'))
admin.add_view(ValUnitsCustom(model=ValUnitsDB, session=db.session, name='Ед.измерения',
                              category='Параметры', menu_icon_type='fa', menu_icon_value='fa-wrench'))
admin.add_view(RoutesCustom(model=RoutesDB, session=db.session, name='Список маршрутов',
                            category='Маршруты', menu_icon_type='fa', menu_icon_value='fa-list'))
admin.add_view(RouteLinksCustom(model=RouteLinksDB, session=db.session, name='Точки маршрутов',
                                category='Маршруты', menu_icon_type='fa', menu_icon_value='fa-dot-circle-o'))
admin.add_view(FacilitiesCustom(model=FacilitiesDB, session=db.session, name='Площадки',
                                category='Расположения', menu_icon_type='fa', menu_icon_value='fa-map-o'))
admin.add_view(PlantsCustom(model=PlantsDB, session=db.session, name='Оборудование',
                            category='Расположения', menu_icon_type='fa', menu_icon_value='fa-tachometer'))

admin.add_view(CheckupsCustom(model=CheckupsDB, session=db.session, name='Обходы',
                              menu_icon_type='fa', menu_icon_value='fa-check-square-o'))



admin.add_link(MenuLink(name='Выход', category='', url='./logout'))





# Custom view example
# from flask_admin import BaseView, expose
# from flask import url_for
#
# class MyView(BaseView):
#     @expose('/')
#     def index(self):
#         # url = url_for('.help')
#         # print(url)
#         # return self.render('admin/index1.html')
#         url = url_for('.help')
#         return self.render('admin/index1.html', url=url)
#
#     @expose('/help/')
#     def help(self):
#         return self.render('admin/help.html')
#
#
# admin.add_view(MyView(name='Hello'))
