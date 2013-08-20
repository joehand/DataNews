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

from models import User, Role, Post

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

if app.debug:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)

# Import the rest
from app import views, models, admin_views