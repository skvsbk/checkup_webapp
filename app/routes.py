import flask
from flask import Blueprint, render_template


main_bp = Blueprint('main_blueprint', __name__)


# Include main page
# Подключение главной страницы
@main_bp.route('/')
def portfolio_home_route():
    # return 'Сайт работает.'
    return flask.redirect("/admin/")
    # return render_template('/admin/index.html')
