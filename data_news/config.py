import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """ This is the default configuration used in both production and developement
    """
    PROJECT = 'datanews'

    # administrator list
    # First administrator is automatically added with db_create
    ADMINS = ['joe.a.hand@gmail.com']
    TESTING = False

    #Flask-Security Config
    SECURITY_TRACKABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_DEFAULT_REMEMBER_ME = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
    SECURITY_EMAIL_SUBJECT_PASSWORD_RESET = 'DataNews: password reset instructions'
    SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE = 'DataNews: your password has been reset'
    SECURITY_EMAIL_SUBJECT_PASSWORD_CHANGE_NOTICE =  'DataNews: your password changed'

    SECURITY_PASSWORD_HASH = 'bcrypt'

    ASSETS_AUTO_BUILD = True
    JS_VERSION = 'v0.01'
    
class ProductionConfig(Config):
    """ Production Config, overwrites above as necessary
    """
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    SECURITY_PASSWORD_SALT = os.environ.get('PASSWORD_SALT')

    #Mail config
    MAIL_SERVER = os.environ.get('MAILGUN_SMTP_SERVER')
    MAIL_PORT = int(os.environ.get('MAILGUN_SMTP_PORT', 587))
    MAIL_USERNAME = os.environ.get('MAILGUN_SMTP_LOGIN')
    MAIL_PASSWORD = os.environ.get('MAILGUN_SMTP_PASSWORD')
    SECURITY_EMAIL_SENDER = 'joe@joehand.org'

    ASSETS_AUTO_BUILD = False
    SEND_FILE_MAX_AGE_DEFAULT = 2592000

    GOOGLE_ANALYTICS_ID = 'UA-43826604-1'
    GOOGLE_ANALYTICS_DOMAIN = 'datanews.co'

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'this_is_so_secret' #used for development, reset in prod

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

    SECURITY_PASSWORD_SALT = '/2aX16zPnnIgfMwkOjGX4S'

    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PANELS = (
        'flask.ext.debugtoolbar.panels.versions.VersionDebugPanel',
        'flask.ext.debugtoolbar.panels.timer.TimerDebugPanel',
        'flask.ext.debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask.ext.debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask.ext.debugtoolbar.panels.template.TemplateDebugPanel',
        'flask.ext.debugtoolbar.panels.logger.LoggingPanel'
    )


class TestingConfig(Config):
    TESTING = True
