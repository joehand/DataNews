import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'this_is_so_secret' #used for development, reset in prod

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

    #Flask-Security Config
    SECURITY_TRACKABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_DEFAULT_REMEMBER_ME = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_EMAIL_SUBJECT_PASSWORD_RESET = 'DataNews: password reset instructions'
    SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE = 'DataNews: your password has been reset'
    SECURITY_EMAIL_SUBJECT_PASSWORD_CHANGE_NOTICE =  'DataNews: your password changed'

    WHOOSH_BASE = os.path.join(basedir, 'search.db')

class ProductionConfig(Config):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    #Mail config
    MAIL_SERVER = os.environ.get('MAILGUN_SMTP_SERVER')
    MAIL_PORT = os.environ.get('MAILGUN_SMTP_PORT')
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAILGUN_SMTP_LOGIN')
    MAIL_PASSWORD = os.environ.get('MAILGUN_SMTP_PASSWORD')

class DevelopmentConfig(Config):
    DEBUG = True

    DEBUG_TB_PANELS = (
        'flask.ext.debugtoolbar.panels.versions.VersionDebugPanel',
        'flask.ext.debugtoolbar.panels.timer.TimerDebugPanel',
        'flask.ext.debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask.ext.debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask.ext.debugtoolbar.panels.template.TemplateDebugPanel',
        'flask.ext.debugtoolbar.panels.logger.LoggingPanel'
    )

    DEBUG_TB_INTERCEPT_REDIRECTS = False


class TestingConfig(Config):
    TESTING = True
