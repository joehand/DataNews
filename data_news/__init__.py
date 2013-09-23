import os

from flask import Flask, g, session, render_template

from .config import Config, DevelopmentConfig, ProductionConfig
from .utils import pretty_date, get_domain, local_time

from flask.ext.security import Security, SQLAlchemyUserDatastore, current_user
from flask.ext.security.signals import user_registered
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask.ext.mail import Mail
from flask.ext.assets import Environment
from flask.ext.compress import Compress
from flask.ext.cacheify import init_cacheify

from datetime import datetime


app = Flask(__name__, static_folder='static', static_url_path='')


"""Set our configuration"""
if os.environ.get('HEROKU_PROD', False):
    """Add a config to know if we are on heroku"""
    app.config['HEROKU_PROD'] = True
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

"""Create database connection object"""
db = SQLAlchemy(app)
cache = init_cacheify(app)

"""Import our blueprints"""
from .api import api
from .admin import admin
from .user import user
from .frontend import frontend


DEFAULT_BLUEPRINTS = (
    frontend,
    user,
)

"""Import Models/Forms we need to setup flask-security"""
from .user import User, Role, ExtendedRegisterForm, ExtendedLoginForm
from .frontend import Item

"""Setup Flask-Security"""
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
"""Add security blueprint with custom registration form (email optional)"""
security = Security(app, user_datastore,
                    register_form=ExtendedRegisterForm,
                    login_form=ExtendedLoginForm)

"""Auto add role and creation time to new users"""
@user_registered.connect_via(app)
def user_registered_sighandler(app, user, confirm_token):
    default_role = user_datastore.find_role('user')
    user_datastore.add_role_to_user(user, default_role)
    user.created_at = datetime.utcnow()
    db.session.commit()

"""Add various extensions"""
mail = Mail(app)
assets = Environment(app)
compress = Compress(app)

"""If we are in prod, don't autobuild"""
assets.auto_build = app.config['ASSETS_AUTO_BUILD']
assets.manifest = 'file'

"""Configure blueprints in views."""
for blueprint in DEFAULT_BLUEPRINTS:
    app.register_blueprint(blueprint)

def configure_template_filters(app):

    @app.template_filter()
    def time_ago(value):
        return pretty_date(value)

    @app.template_filter()
    def time(value):
        return local_time(value)

    @app.template_filter()
    def domain(value):
        return get_domain(value)

def configure_logging(app):
    """Set up logging or debugging"""
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

def configure_app_requests(app):
    @cache.cached(timeout=60*60*24*7, key_prefix='all_pages')
    def get_pages():
        """ Get the pages to show in footer
            These are special 'items' with kind=page or kind=external
            External ones are links to, you guessed it, external websites
        """
        pages = Item.query.filter(or_(Item.kind=='page', Item.kind=='external')).order_by(Item.title).all()
        return [page for page in pages]

    @app.before_first_request
    def before_first():
        """ Create a permanent session
            Track new login for authenticated users
        """
        session.permanent = True
        if current_user.is_authenticated():
            current_user.current_login_at = datetime.utcnow()
            db.session.commit()

    @app.before_request
    def before_request():
        """ Get our footer pages. 
            TODO: This should be done once in before_first but that wasn't working

            We check if user is anonymous and first time visitor to show a "welcome" message
        """
        g.pages = get_pages()
        if current_user.is_anonymous() and session.get('visited_index', False):
            session['return_anon'] = True


def configure_error_handlers(app):
    @app.errorhandler(404)
    def internal_404(error):
        return render_template('error/404.html'), 404

    @app.errorhandler(500)
    def internal_500(error):
        db.session.rollback()
        return render_template('error/500.html'), 500

configure_app_requests(app)
configure_template_filters(app)
configure_logging(app)
configure_error_handlers(app)
