from flask import Blueprint, redirect
from flask_login import current_user


main_bp = Blueprint('main_blueprint', __name__)


@main_bp.route('/')
def admin_route():
    if current_user.is_authenticated:
        return redirect('/admin')
    return redirect('/admin/login')
