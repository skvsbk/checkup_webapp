from flask import Blueprint, render_template, redirect


main_bp = Blueprint('main_blueprint', __name__)

# Include main page
# Подключение главной страницы
@main_bp.route('/')
def admin_route():
    # return 'Сайт работает.'
    if True:
        return redirect("/admin/login")
    return redirect("/admin")
    # return redirect("/")
    # return render_template('index.html')

