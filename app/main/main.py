from flask import Blueprint, render_template, flash, send_file, redirect, url_for, request
from flask_login import login_required
from io import BytesIO
from sqlalchemy import func

from app.extensions import db
from app.models import Pribor, Otdel, Promer, Oborudovanie

main = Blueprint('main', __name__, template_folder='templates', static_folder='static')

@main.route('/')
def index():
    return render_template('main/index.html', title='Главная страница')


@main.route('/kalibrovka')
@login_required
def kalibrovka_main():

    try:
        kalibr = db.session.query(Otdel, Pribor, Oborudovanie).\
            join(Otdel, Otdel.id == Oborudovanie.otdel_id).\
            join(Pribor, Pribor.id == Oborudovanie.pribor_id).\
            filter(Oborudovanie.sertificat != b'').\
            order_by(Oborudovanie.pribor_id).all()
    except:
        return 'Ошибка получения данных'

    return render_template('main/kalibrovka.html', title='Данные о калибровке приборов', kalibr=kalibr)


@main.route('/kalibrovka/<int:id>/download')
@login_required
def kalibrovka_download(id):
    try:
        kalibr = Oborudovanie.query.get_or_404(id)
        if kalibr.sertificat:
            pribor = Pribor.query.get_or_404(kalibr.pribor_id)
            filename = f'{pribor.type} №{kalibr.number} ({kalibr.date}).pdf'
            return send_file(BytesIO(kalibr.sertificat),
                             download_name=filename, as_attachment=True)
        else:
            flash("Данный сертификат отсутствует в базе", category='danger')
            return redirect(request.args.get("next") or url_for('.kalibrovka_main'))
    except:
        return 'Ошибка при загрузке1'

@main.route('/promer')
@login_required
def promer_main():
    try:
        names = db.session.query(Otdel, Promer).join(Otdel, Otdel.id == Promer.otdel_id).order_by(Promer.id.desc()).all()
        last = db.session.query(Otdel, Promer).join(Otdel, Otdel.id == Promer.otdel_id).group_by(Promer.otdel_id).having(func.max(Promer.id)).all()
    except:
        return 'Ошибка получения данных'
    return render_template('main/promer.html',
                           title='Данные о промере',
                           names=names,
                           last=last)


@main.errorhandler(401)
def unauthorized(error):
    return render_template('main/error401.html',
                           title='Ошибка авторизации')