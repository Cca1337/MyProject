from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os
from logging import FileHandler, WARNING

db = SQLAlchemy()
DB_NAME = "database.db"

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'Uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpeg', 'gif'}


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = b"YOURsuperSECRETKEY"
    app.static_folder = 'static'

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['UPLOAD_EXTENSIONS'] = ALLOWED_EXTENSIONS
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    file_handler = FileHandler('error.log')
    file_handler.setLevel(WARNING)
    app.logger.addHandler(file_handler)

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # creating database if doesnt exist
    from .models import User, Note, Obrazok

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
