from data_news import app, admin, db
from models import User, Item, Role, Vote, Twitter
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.security import roles_required, current_user


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