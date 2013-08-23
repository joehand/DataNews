from app import app, admin, db
from models import User, Item, Role
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.security import login_required, current_user


class AdminView(BaseView):
    def is_accessible(self):
        if current_user.is_anonymous():
            return False
        return current_user.is_admin()

    @expose('/')
    @login_required
    def index(self):
        return self.render('index.html')

# Create customized model view class
class AdminModelView(ModelView):
    def is_accessible(self):
        if current_user.is_anonymous():
            return False
        return current_user.is_admin()

# Create customized model view class
class SuperModelView(ModelView):
    def is_accessible(self):
        if current_user.is_anonymous():
            return False
        return current_user.is_super()


admin.add_view(SuperModelView(User, db.session))
admin.add_view(SuperModelView(Role, db.session))
admin.add_view(AdminModelView(Item, db.session))