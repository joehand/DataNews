import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

#Flask-Security Config
SECURITY_TRACKABLE = True
SECURITY_CHANGEABLE = True
SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_DEFAULT_REMEMBER_ME = True
SECURITY_SEND_REGISTER_EMAIL = False

#Mail config
MAIL_SERVER = 'smtp.example.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'username'
MAIL_PASSWORD = 'password'

# Bootstrap Config (https://github.com/mbr/flask-bootstrap#configuration-options)
BOOTSTRAP_USE_CDN = False #True when i have internet
BOOTSTRAP_FONTAWESOME = True

DEBUG_TB_PANELS = (
    'flask.ext.debugtoolbar.panels.versions.VersionDebugPanel',
    'flask.ext.debugtoolbar.panels.timer.TimerDebugPanel',
    'flask.ext.debugtoolbar.panels.headers.HeaderDebugPanel',
    'flask.ext.debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
    'flask.ext.debugtoolbar.panels.template.TemplateDebugPanel',
    'flask.ext.debugtoolbar.panels.logger.LoggingPanel'
)