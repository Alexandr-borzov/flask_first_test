from io import BytesIO
from flask import Blueprint, request, redirect, render_template, url_for, flash, send_file
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Pribor, Otdel, Promer, Oborudovanie, Users

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

menu = [{'url': 'main.index', 'title': 'Главная страница'},
        {'url': '.users', 'title': 'Пользователи'},
        {'url': '.promer', 'title': 'Промер'},
        {'url': '.kalibrovka', 'title': 'Калибровка'},
        {'url': '.pribor', 'title': 'Типы оборудования'},
        {'url': '.otdel', 'title': 'Отделы'},
        {'url': 'registration.user_logout', 'title': 'Выйти'}]


def is_admin():
    u = Users.query.filter(Users.id == current_user.get_id()).one()
    return True if u.login == 'admin' else False


@admin.route('/')
@login_required
def admin_index():
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    return render_template('admin/index.html', menu=menu, title='Админ-панель')


@admin.route('/promer')
@login_required
def promer():
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    try:
        names = db.session.query(Otdel, Promer).join(Otdel, Otdel.id == Promer.otdel_id).order_by(Promer.id.desc()).all()
    except:
        return 'Ошибка получения данных'
    return render_template('admin/promer.html', menu=menu, title='Данные о промере', names=names)


@admin.route('/promer_add', methods=['POST', 'GET'])
@login_required
def promer_add():
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    otdel_set = Otdel.query.all()
    if request.method == 'POST':
        otdel_id = request.form['name']
        lenght = request.form['lenght']
        prom = request.form['prom']
        date = request.form['date']

        promer = Promer(otdel_id=otdel_id,
                        lenght=lenght,
                        prom=prom,
                        date=date)
        try:
            db.session.add(promer)
            db.session.commit()
            return redirect(url_for('.promer'))
        except:
            return 'Произошла ошибка при добавлении записи'

    return render_template('admin/promer_add.html',
                           menu=menu,
                           title='Добавить данные о промере',
                           otdel_set=otdel_set)


@admin.route('/promer/<int:id>/del')
@login_required
def promer_delet(id):
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    promer = Promer.query.get_or_404(id)
    try:
        db.session.delete(promer)
        db.session.commit()
        return redirect(url_for('.promer'))
    except:
        return 'Произошла ошибка при удалении записи'


@admin.route('/promer/<int:id>/update', methods=['POST', 'GET'])
@login_required
def promer_update(id):
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    otdel_set = Otdel.query.all()
    promer = Promer.query.get_or_404(id)
    if request.method == 'POST':
        promer.otdel_id = request.form['name']
        promer.lenght = request.form['lenght']
        promer.prom = request.form['prom']
        promer.date = request.form['date']

        try:
            db.session.commit()
            return redirect(url_for('.promer'))
        except:
            return 'Произошла ошибка при изменении записи'
    else:
        return render_template('admin/promer_update.html',
                               title='Изменить данные о промере',
                               menu=menu,
                               promer=promer,
                               otdel_set=otdel_set)


@admin.route('/kalibrovka')
@login_required
def kalibrovka():
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    try:
        no_kalibr = db.session.query(Otdel, Pribor, Oborudovanie).\
            join(Otdel, Otdel.id == Oborudovanie.otdel_id).\
            join(Pribor, Pribor.id == Oborudovanie.pribor_id).\
            filter(Oborudovanie.sertificat == b'').\
            order_by(Oborudovanie.pribor_id).all()
        kalibr = db.session.query(Otdel, Pribor, Oborudovanie).\
            join(Otdel, Otdel.id == Oborudovanie.otdel_id).\
            join(Pribor, Pribor.id == Oborudovanie.pribor_id).\
            order_by(Oborudovanie.pribor_id).all()
    except:
        return 'Ошибка получения данных'

    return render_template('admin/kalibrovka.html',
                           menu=menu,
                           title='Данные о калибровке приборов',
                           kalibr=kalibr,
                           no_kalibr=no_kalibr)


@admin.route('/kalibrovka_add', methods=['POST', 'GET'])
@login_required
def kalibrovka_add():
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    otdel_set = Otdel.query.all()
    pribor_set = Pribor.query.all()
    if request.method == 'POST':
        pribor_id = request.form['pribor_type']
        number = request.form['number']
        date = request.form['date']
        next_date = request.form['next_date']
        sertificat = request.files['file']
        otdel_id = request.form['name']
        if Oborudovanie.query.filter(Oborudovanie.pribor_id == pribor_id, Oborudovanie.number == number).all():
            flash("Данный прибор уже имеется в базе", category='error')
            return render_template('admin/kalibrovka_add.html',
                                   menu=menu,
                                   title='Добавить данные о калибровке прибора',
                                   otdel_set=otdel_set,
                                   pribor_set=pribor_set)
        else:
            kalibr = Oborudovanie(pribor_id=pribor_id,
                                  number=number,
                                  date=date,
                                  next_date=next_date,
                                  sertificat=sertificat.read(),
                                  otdel_id=otdel_id)
            try:
                db.session.add(kalibr)
                db.session.commit()
                return redirect(url_for('.kalibrovka'))
            except:
                return 'Произошла ошибка при добавлении записи'

    return render_template('admin/kalibrovka_add.html',
                           menu=menu,
                           title='Добавить данные о калибровке прибора',
                           otdel_set=otdel_set,
                           pribor_set=pribor_set)


@admin.route('/kalibrovka/<int:id>/update', methods=['POST', 'GET'])
@login_required
def kalibrovka_update(id):
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    kalibr = Oborudovanie.query.get_or_404(id)
    otdel = Otdel.query.get_or_404(kalibr.otdel_id)
    pribor_type = Pribor.query.get_or_404(kalibr.pribor_id)
    otdel_set = Otdel.query.filter(Otdel.id != otdel.id).all()
    pribor_set = Pribor.query.filter(Pribor.id != pribor_type.id).all()

    if request.method == 'POST':
        kalibr.pribor_id = request.form['pribor_type']
        kalibr.number = request.form['number']
        kalibr.date = request.form['date']
        kalibr.next_date = request.form['next_date']
        kalibr.sertificat = request.files['file'].read()
        kalibr.otdel_id = request.form['name']

        try:
            db.session.commit()
            return redirect(url_for('.kalibrovka'))
        except:
            return 'Произошла ошибка при изменении записи'
    else:
        return render_template('admin/kalibrovka_update.html',
                               title='Изменить данные о калибровке',
                               menu=menu,
                               kalibr=kalibr,
                               pribor_type=pribor_type,
                               otdel=otdel,
                               otdel_set=otdel_set,
                               pribor_set=pribor_set)


@admin.route('/kalibrovka/<int:id>/del')
@login_required
def kalibrovka_delet(id):
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    kalibr = Oborudovanie.query.get_or_404(id)
    try:
        db.session.delete(kalibr)
        db.session.commit()
        return redirect(url_for('.kalibrovka'))
    except:
        return 'Произошла ошибка при удалении записи'


@admin.route('kalibrovka/<int:id>/download')
@login_required
def kalibrovka_download(id):
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    try:
        kalibr = Oborudovanie.query.get_or_404(id)
        if kalibr.sertificat:
            pribor = Pribor.query.get_or_404(kalibr.pribor_id)
            filename = f'{pribor.type} №{kalibr.number} ({kalibr.date}).pdf'
            return send_file(BytesIO(kalibr.sertificat),
                             download_name=filename, as_attachment=True)
        else:
            return "Данный сертификат отсутствует в базе"
    except:
        return 'Ошибка при загрузке'


@admin.route('/pribor')
@login_required
def pribor():
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    names = Pribor.query.all()
    return render_template('admin/pribor.html', menu=menu, title='Типы оборудования', names=names)


@admin.route('/pribor_add', methods=['POST', 'GET'])
@login_required
def pribor_add():
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        name = request.form['name']
        pribor = Pribor(type=name)
        try:
            db.session.add(pribor)
            db.session.commit()
            return redirect(url_for('.pribor'))
        except:
            return 'Произошла ошибка при добавлении записи'

    return render_template('admin/pribor_add.html', menu=menu, title='Добавить прибор')


@admin.route('/pribor/<int:id>/del')
@login_required
def pribor_delet(id):
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    pribor = Pribor.query.get_or_404(id)
    try:
        db.session.delete(pribor)
        db.session.commit()
        return redirect(url_for('.pribor'))
    except:
        return 'Произошла ошибка при удалении записи'


@admin.route('/pribor/<int:id>/update', methods=['POST', 'GET'])
@login_required
def update_pribor(id):
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    pribor = Pribor.query.get_or_404(id)
    if request.method == 'POST':
        pribor.type = request.form['name']
        try:
            db.session.commit()
            return redirect(url_for('.pribor'))
        except:
            return 'Произошла ошибка при добавлении записи'
    else:
        return render_template('admin/pribor_update.html', menu=menu, title='Изменить прибор', pribor=pribor)


@admin.route('/otdel')
@login_required
def otdel():
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    names = Otdel.query.all()
    return render_template('admin/otdel.html', menu=menu, title='Подразделения', names=names)


@admin.route('/otdel_add', methods=['POST', 'GET'])
@login_required
def otdel_add():
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        name = request.form['name']
        otdel = Otdel(work=name)
        try:
            db.session.add(otdel)
            db.session.commit()
            return redirect(url_for('.otdel'))
        except:
            return 'Произошла ошибка при добавлении записи'

    return render_template('admin/otdel_add.html', menu=menu, title='Добавить отдел')


@admin.route('/otdel/<int:id>/del')
@login_required
def otdel_delet(id):
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    otdel = Otdel.query.get_or_404(id)
    try:
        db.session.delete(otdel)
        db.session.commit()
        return redirect(url_for('.otdel'))
    except:
        return 'Произошла ошибка при удалении записи'


@admin.route('/otdel/<int:id>/update', methods=['POST', 'GET'])
@login_required
def otdel_update(id):
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    otdel = Otdel.query.get_or_404(id)
    if request.method == 'POST':
        otdel.work = request.form['name']
        try:
            db.session.commit()
            return redirect(url_for('.otdel'))
        except:
            return 'Произошла ошибка при добавлении записи'
    else:
        return render_template('admin/otdel_update.html', menu=menu, title='Изменить отдел', otdel=otdel)


@admin.route('/users')
@login_required
def users():
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    user = Users.query.all()
    return render_template('admin/users.html', menu=menu, title='Подразделения', users=user)

@admin.route('/users/<int:id>/del')
@login_required
def user_delet(id):
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    user = Users.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('.users'))
    except:
        return 'Произошла ошибка при удалении записи'


@admin.route('/users/<int:id>/update', methods=['POST', 'GET'])
@login_required
def user_update(id):
    if not is_admin():
        flash('Доступ запрещен', category='danger')
        return redirect(url_for('main.index'))
    user = Users.query.get_or_404(id)
    if request.method == 'POST':
        if request.form['psw'] == request.form['psw2']:
            user.psw = generate_password_hash(request.form['psw'])
            try:
                db.session.commit()
                return redirect(url_for('.users'))
            except:
                return 'Произошла ошибка при добавлении записи'
        else:
            flash('Пароли не совпадают', category='error')
    else:
        return render_template('admin/psw_update.html', menu=menu, title='Изменить пароль')