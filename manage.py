# manage.py
from data_news import app, db, user_datastore, cache
from data_news.models import User, Role
from flask.ext.script import Manager, Shell
from flask.ext.s3 import create_all
from flask.ext.security.utils import encrypt_password
import os
import gzip
import bcrypt
from datetime import datetime

if not os.environ.get('HEROKU_PROD', False):
    from rootkey import *

manager = Manager(app)

try: 
    from tweets import TweetGetter
    tweets = TweetGetter()
except:
    print 'cannot import twitter stuff'
    pass

def compress(file_path):
    """
    Gzip a single file in place.
    """
    f_in = open(file_path, 'rb')
    contents = f_in.readlines()
    f_in.close()
    f_out = gzip.open(file_path, 'wb')
    f_out.writelines(contents)
    f_out.close()

@manager.command
def twitter():
    tweets.get_mentions();
    tweets.get_favorites();
    print 'all done!'

@manager.command
def db_create():
    db.create_all()
    roles = [('user', 'Generic user role'),
             ('admin', 'Regular Admin'),
             ('super', 'Super secret admin'),
            ]
    print 'making roles'
    for role_name, role_desc in roles:
        role = user_datastore.create_role(name=role_name, description=role_desc)
        db.session.commit()

    user = user_datastore.find_role('user')
    superAdmin = user_datastore.find_role('super')

    print 'making user'
    user = user_datastore.create_user(
            email='joe@joehand.org',
            name='DataNews',
            password=encrypt_password('password')
            )
    joe = user_datastore.create_user(
            email='joe.a.hand@gmail.com',
            name='jh',
            password=encrypt_password('password')
            )

    print 'adding roles to user'
    user_datastore.add_role_to_user(joe, superAdmin)
    user.created_at = datetime.utcnow()
    joe.created_at = datetime.utcnow()
    print 'finishing up'
    db.session.commit()


@manager.command
def db_upgrade():
    os.system('alembic upgrade head')

@manager.option('-m', '--message', dest='message', default='')
def db_migrate(message):
    print message
    os.system('alembic revision --autogenerate -m "%s"' % message)

@manager.command
def build_js():
    jsfile = 'app.min.' + app.config['JS_VERSION'] + '.js'
    os.system('cd data_news/static/js && node ../../../r.js -o app.build.js out=%s'%jsfile)
    jsfile = 'data_news/static/js/' + jsfile
    require = 'data_news/static/js/require.js'
    #compress(jsfile)
    #compress(require)

@manager.command
def upload_static():
    create_all(app, user=AccessKey, password=SecretKey)

@manager.command
def clear_cache():
    with app.app_context():
        cache.clear()

def shell_context():
    return dict(app=app)   

#runs the app
if __name__ == '__main__':
    manager.add_command('shell', Shell(make_context=shell_context))
    manager.run()