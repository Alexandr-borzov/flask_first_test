from flask import Blueprint, request, render_template, redirect, url_for, flash, send_file
from flask_login import current_user, login_required
from io import BytesIO

from app.extensions import db
from app.models import Profile, Otdel, Pribor, Promer, Oborudovanie, Users


user = Blueprint('user', __name__, template_folder='templates', static_folder='static')


@user.route('/profile/<int:id>/update', methods=['POST', 'GET'])
@login_required
def profile_update(id):
    profile = Profile.query.get_or_404(id)
    otdel_info = Otdel.query.all()
    if request.method == 'POST':
        profile.name = request.form['name']
        profile.surname = request.form['surname']
        profile.otdel_id = request.form['otdel_id']
        try:
            db.session.commit()
            return redirect(url_for('.profile'))
        except:
            return 'Произошла ошибка при добавлении записи'
    else:
        return render_template('user/profile_update.html',
                               title='Изменить информацию профиля',
                               profile=profile,
                               otdel_info=otdel_info)


@user.route('/profile')
@login_required
def profile():
    u = Users.query.filter(Users.id == current_user.get_id()).one()
    if u.login == 'admin':
        return redirect(url_for('admin.admin_index'))
    user_info = db.session.query(Profile, Otdel).join(Otdel, Otdel.id == Profile.otdel_id).\
        filter(Profile.user_id == current_user.get_id()).one()
    kalibr_info = db.session.query(Oborudovanie, Pribor).join(Pribor, Pribor.id == Oborudovanie.pribor_id).\
        filter(Oborudovanie.otdel_id == user_info.Profile.otdel_id).all()
    promer_info = db.session.query(Otdel, Promer).join(Otdel, Otdel.id == Promer.otdel_id).\
        filter(Promer.otdel_id == user_info.Profile.otdel_id).order_by(Promer.id.desc()).all()
    return render_template('user/profile.html',
                           title='Личный кабинет пользователя',
                           user_info=user_info,
                           kalibr_info=kalibr_info,
                           promer_info=promer_info)


@user.route('/profile/add_pribor', methods=['POST', 'GET'])
@login_required
def user_add_pribor():
    prbor_info = Pribor.query.all()
    if request.method == 'POST':
        pribor_id = request.form['pribor_id']
        number = request.form['number']
        u = Profile.query.filter(Profile.user_id == current_user.get_id()).one()
        if Oborudovanie.query.filter(Oborudovanie.pribor_id == pribor_id, Oborudovanie.number == number).all():
            flash("Данный прибор уже имеется в базе, для перемещения обратитесь к администратору", category='danger')
            return render_template('user/add_pribor.html',
                                   title='Добавить информацию о приборах',
                                   pribor_info=prbor_info)
        else:
            pribor = Oborudovanie(pribor_id=pribor_id,
                                  number=number,
                                  otdel_id=u.otdel_id)
            try:
                db.session.add(pribor)
                db.session.commit()
                return redirect(url_for('.profile'))
            except:
                return 'Произошла ошибка при добавлении записи'
    else:
        return render_template('user/add_pribor.html',
                               title='Добавить информацию о приборах',
                               pribor_info=prbor_info)


@user.route('/user/<int:id>/download')
@login_required
def user_kalibrovka_download(id):
    try:
        kalibr = Oborudovanie.query.get_or_404(id)
        if kalibr.sertificat:
            pribor = Pribor.query.get_or_404(kalibr.pribor_id)
            filename = f'{pribor.type} №{kalibr.number} ({kalibr.date}).pdf'
            return send_file(BytesIO(kalibr.sertificat),
                             download_name=filename, as_attachment=True)
        else:
            flash("Данный сертификат отсутствует в базе", category='danger')
            return redirect(url_for('.profile'))
    except:
        return 'Ошибка при загрузке1'