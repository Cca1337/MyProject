from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_admin import Admin
import os
from logging import FileHandler, WARNING
import flask_monitoringdashboard as dashboard
from flask_caching import Cache

db = SQLAlchemy()
DB_NAME = "database.db"

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'Uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpeg', 'gif'}

config_cache = {
    "DEBUG": True,          
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300}

cache = Cache(config=config_cache)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = b"YOURSECRETKEYGOESHERE"
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
    from .models import User, Note, Obrazok, Role, MyModelView, MyAdminIndexView

    create_database(app)

# CREATE MONITORING DASHBOARD
    dashboard.config.init_from(file=f'{APP_ROOT}/static/config/config.cfg')
    dashboard.bind(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)


    admin = Admin(app, index_view=MyAdminIndexView())

    admin.add_view(MyModelView(User, db.session))
    admin.add_view(MyModelView(Role, db.session))
    admin.add_view(MyModelView(Note, db.session))
    admin.add_view(MyModelView(Obrazok, db.session))

    cache.init_app(app)

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
