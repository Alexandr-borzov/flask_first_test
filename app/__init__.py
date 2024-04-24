from flask import Flask
import os

from app.extensions import db, manager
from app.admin.admin import admin
from app.user.user import user
from app.main.main import main
from app.registration.registration import registration


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metrology.db'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/metrology.db'
    # app.config['SECRET_KEY'] = os.environ ['SECRET_KEY']

    db.init_app(app)
    manager.init_app(app)
    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(user)
    app.register_blueprint(registration)

    return app

