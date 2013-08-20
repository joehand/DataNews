from app import app, admin, db
from models import User, Post, Comment, Tag, Role
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.security import current_user


class AdminView(BaseView):
    def is_accessible(self):
        return current_user.is_admin()

    @expose('/')
    def index(self):
        return self.render('index.html')

# Create customized model view class
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_admin()

# Create customized model view class
class SuperModelView(ModelView):
    def is_accessible(self):
        return current_user.is_super()


admin.add_view(SuperModelView(User, db.session))
admin.add_view(SuperModelView(Role, db.session))
admin.add_view(AdminModelView(Post, db.session))
admin.add_view(AdminModelView(Tag, db.session))
admin.add_view(AdminModelView(Comment, db.session))