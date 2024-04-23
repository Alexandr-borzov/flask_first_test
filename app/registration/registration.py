from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required

from app.extensions import db, manager
from app.models import Users, Profile, Otdel


registration = Blueprint('registration', __name__, template_folder='templates', static_folder='static')


@manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@registration.route('/login', methods=['POST', 'GET'])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('user.profile'))
    login = request.form.get('log')
    pasword = request.form.get('psw')
    if login and pasword:
        user_log = Users.query.filter(Users.login == login).one()
        if user_log and check_password_hash(user_log.psw, pasword):
            rm = True if request.form.get('remember_me') else False
            login_user(user_log, remember=rm)
            return redirect(url_for('main.index'))
        else:
            flash("Неверная пара логин/пароль", category='danger')

        return render_template('registration/login.html', title='Авторизация пользователя')
    else:
        return render_template('registration/login.html', title='Авторизация пользователя')


@registration.route('/logout')
@login_required
def user_logout():
    logout_user()
    return redirect(url_for('main.index'))


@registration.route('/registration', methods=['POST', 'GET'])
def user_registration():
    otdel_set = Otdel.query.all()
    if request.method == 'POST':
        log = request.form.get('username')
        pasw = request.form.get("pass")
        pasw2 = request.form.get('pass2')
        name = request.form.get('name')
        surname = request.form.get('surname')
        otd = request.form.get('otdel')
        print([log, pasw, pasw2, name, surname, otd])
        if all([log, pasw, pasw2, name, surname, otd]):
            chek_log = Users.query.filter(Users.login == log).all()
            if not chek_log:
                if pasw == pasw2:
                    try:
                        hash = generate_password_hash(pasw)
                        u = Users(login=log, psw=hash)
                        db.session.add(u)
                        db.session.flush()

                        p = Profile(name=name, surname=surname,
                                    otdel_id=otd, user_id=u.id)
                        db.session.add(p)
                        db.session.commit()
                        flash('Регистрация пользователя прошла успешно', category='success')
                    except:
                        db.session.rollback()
                        print("Ошибка добавления в БД")
                    return redirect(url_for('registration.user_login'))
                else:
                    flash('Пароли не совпадают', category='danger')
            else:
                flash('Данный логин уже используется', category='danger')
        else:
            flash('Заполните все поля', category='danger')
    return render_template('registration/registration.html',
                           title='Регистрация пользователя',
                           otdel_set=otdel_set)