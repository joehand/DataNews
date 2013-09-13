import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security.signals import user_registered
from flask.ext.security import Security, SQLAlchemyUserDatastore, current_user
from flask.ext.mail import Mail
from flask.ext.assets import Environment
from flask.ext.compress import Compress
from datetime import datetime
from template_utils import get_domain, pretty_date

app = Flask(__name__, static_folder='static', static_url_path='')

if os.environ.get('HEROKU_PROD', False):
    app.config['HEROKU_PROD'] = True
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

# Create database connection object
db = SQLAlchemy(app)

from models import User, Role
from forms import ExtendedRegisterForm, ExtendedLoginForm

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# Add security blueprint with custom registration form (email optional)
security = Security(app, user_datastore,
                    register_form=ExtendedRegisterForm,
                    login_form=ExtendedLoginForm)

# Auto add role and creation time to new users
@user_registered.connect_via(app)
def user_registered_sighandler(app, user, confirm_token):
    default_role = user_datastore.find_role('user')
    user_datastore.add_role_to_user(user, default_role)
    user.created_at = datetime.utcnow()
    db.session.commit()


#Add various extensions
mail = Mail(app)
assets = Environment(app)

assets.auto_build = app.config['ASSETS_AUTO_BUILD']
assets.manifest = 'file'

compress = Compress(app)

# Set tempalate globals
app.jinja_env.globals['get_domain'] = get_domain
app.jinja_env.globals['pretty_date'] = pretty_date

from data_news import views, models, admin_views, api

if app.debug:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)
else:
    import logging
    from logging.handlers import SMTPHandler
    from logging import Formatter
    credentials = None
    if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
        credentials = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    mail_handler = SMTPHandler((app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                            'no-reply@' + app.config['MAIL_SERVER'], 
                            app.config['ADMINS'], 'data news error!!', credentials)
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(Formatter('''
    Message type:       %(levelname)s
    Location:           %(pathname)s:%(lineno)d
    Module:             %(module)s
    Function:           %(funcName)s
    Time:               %(asctime)s

    Message:

    %(message)s
    '''))
    app.logger.addHandler(mail_handler)
