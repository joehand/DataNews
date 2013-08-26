from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, current_user
from flask.ext.admin import Admin, AdminIndexView, expose
from flask.ext.assets import Environment
from flask.ext.security.signals import user_registered
from datetime import datetime
from flask.ext.restless import APIManager
from template_utils import get_domain, pretty_date

app = Flask(__name__)

app.config.from_object('config')
app.debug = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


# Create database connection object
db = SQLAlchemy(app)

from models import User, Role
from forms import ExtendedRegisterForm

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore,
                    register_form=ExtendedRegisterForm)

@user_registered.connect_via(app)
def user_registered_sighandler(app, user, confirm_token):
    default_role = user_datastore.find_role('user')
    user_datastore.add_role_to_user(user, default_role)
    user.created_at = datetime.utcnow()
    db.session.commit()


# Create the Flask-Restless API manager.
api_manager = APIManager(app, flask_sqlalchemy_db=db)

#Add various extensions
bootstrap = Bootstrap(app)
assets = Environment(app)

class AdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated() and current_user.is_admin


admin = Admin(app, name='Data News', index_view = AdminView())

# Set tempalate globals
app.jinja_env.globals['get_domain'] = get_domain
app.jinja_env.globals['pretty_date'] = pretty_date

from data_news import views, models, admin_views, api

if app.debug:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)