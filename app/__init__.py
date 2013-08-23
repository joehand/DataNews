from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.admin import Admin

app = Flask(__name__)


app.config.from_object('config')
app.debug = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

#Add various extensions
bootstrap = Bootstrap(app)
admin = Admin(app, name='Data News')

# Create database connection object
db = SQLAlchemy(app)

from models import User, Role

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from flask.ext.security.signals import user_registered
from datetime import datetime
@user_registered.connect_via(app)
def user_registered_sighandler(app, user, confirm_token):
    default_role = user_datastore.find_role('user')
    user_datastore.add_role_to_user(user, default_role)
    user.created_at = datetime.utcnow()
    db.session.commit()


import flask.ext.restless
# Create the Flask-Restless API manager.
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

if app.debug:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)

# Import the rest
from app import views, models, admin_views, api

from template_utils import get_domain
app.jinja_env.globals['get_domain'] = get_domain