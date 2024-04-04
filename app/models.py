from flask_login import UserMixin

from app.extensions import db


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False, unique=True)
    psw = db.Column(db.String(500), nullable=False)


class Pribor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), unique=True)


class Otdel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work = db.Column(db.String(50), unique=True)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    otdel_id = db.Column(db.Integer, db.ForeignKey('otdel.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Promer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    otdel_id = db.Column(db.Integer, db.ForeignKey('otdel.id'))
    lenght = db.Column(db.Integer, nullable=False)
    prom = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(50))


class Oborudovanie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pribor_id = db.Column(db.Integer, db.ForeignKey('pribor.id'))
    number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(50))
    next_date = db.Column(db.String(50))
    sertificat = db.Column(db.LargeBinary)
    otdel_id = db.Column(db.Integer, db.ForeignKey('otdel.id'))