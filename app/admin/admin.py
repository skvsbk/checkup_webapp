from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from app.models import UserDB, RoleDB
from app.admin import login_manager
from app import db


admin_bp = Blueprint('admin_bp', __name__, template_folder='templates', static_folder='static')


@login_manager.user_loader
def load_user(user_id):
    user = db.session.query(UserDB).filter(UserDB.id == user_id).one()
    return user


@admin_bp.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('./')

    if request.method == 'POST':
        try:
            user = db.session.query(UserDB).filter(UserDB.login == request.form['user']).one()
            if check_password_hash(user.password, request.form['password']):
                role = db.session.query(RoleDB).filter(RoleDB.id == user.role_id).one()
                if role.role_name in ('admin', 'user_webapp'):
                    # if request.form.get('rememberme'):
                    #     login_user(user, remember=True, duration=timedelta(days=7))
                    # else:
                    #     login_user(user)
                    login_user(user)
                    return redirect('./')
                else:
                    flash("Не та роль", 'error')
            else:
                flash("Неверный пароль", 'error')
        except:
            flash("Пользователь не найден", 'error')

    return render_template('admin/login.html', title='Вход в систему электронных журналов')


@admin_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('admin_bp.login'))
