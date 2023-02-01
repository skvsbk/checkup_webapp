from flask import Blueprint, request, redirect, url_for, render_template, session, flash


admin_bp = Blueprint('admin_bp', __name__, template_folder='templates', static_folder='static')

# Simple login system
#
# def login_admin():
#     session['admin_logged'] = 1
#
# def isLogged():
#     return True if session.get('admin_logged') else False
#
# def logout_admin():
#     session.pop('admin_logged', None)
#
#
# @admin_bp.route('/login', methods=['POST', 'GET'])
# def login():
#     if request.method == 'POST':
#         if request.form['user'] == 'admin' and request.form['password'] == '12345':
#             login_admin()
#             return redirect('./')
#         else:
#             flash("Wrong login or password", 'error')
#
#     return render_template('admin/login.html', title='Admin-pannel')
#
# @admin_bp.route('/logout', methods=['POST', 'GET'])
# def logout():
#     if isLogged():
#         return redirect(url_for('.login'))
#
#     logout_admin()
#
#     return redirect(url_for('.login'))