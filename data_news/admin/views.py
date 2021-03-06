from data_news import app, db
from ..user import User, Role
from ..frontend import Item, Vote
from ..background import Twitter

from flask import Blueprint

from flask.ext.admin import Admin, AdminIndexView, expose
from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.security import roles_required, current_user

# Create a base admin view with required authentication.
class AdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated() and current_user.is_admin

# Create out admin and add to app
admin = Admin(app, name='Data News', index_view = AdminView(), url='/admin')

# Create customized model view class
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated() and current_user.is_admin

# Create customized model view class
class SuperModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated() and current_user.is_super

admin.add_view(SuperModelView(User, db.session))
admin.add_view(SuperModelView(Role, db.session))
admin.add_view(SuperModelView(Twitter, db.session))
admin.add_view(AdminModelView(Item, db.session))
admin.add_view(AdminModelView(Vote, db.session))