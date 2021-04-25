from . import db
from flask import redirect, url_for
from flask_login import UserMixin, current_user
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView



class Obrazok(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text)
    pic_date = db.Column(db.DateTime, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    obrazky = db.relationship('Obrazok')
    roles = db.relationship('Role')

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(100), unique=True)


# show all dbs
class MyModelView(ModelView):
    def is_accessible(self):
        try:
            kontrola = User.query.get(current_user.id).roles

        except AttributeError as err:
            print(err)
        return current_user.is_authenticated and kontrola

# show db attributes if current user is authorized else redirect to home screen
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('views.home'))

# HOME ADMIN SCREEN
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        try:
            kontrola = User.query.get(current_user.id).roles

        except AttributeError as err:
            print(err)
        return current_user.is_authenticated and kontrola

