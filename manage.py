# manage.py
from data_news import app
from data_news import db, cache
from data_news.user import User, Role
from flask.ext.script import Manager, Shell
from flask.ext.security import SQLAlchemyUserDatastore
from flask.ext.security.utils import encrypt_password
import os
import gzip
import bcrypt
from datetime import datetime

manager = Manager(app)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
try: 
    from data_news.background import TweetGetter
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
    """ Gets new tweets from list of favorites and mentions
        This can be run with a scheduled job
    """
    tweets.get_mentions();
    tweets.get_favorites();
    print 'all done!'

@manager.command
def db_create():
    """ Create a new database
        Add some default roles
        Create an initial admin user
    """
    db.drop_all()
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

    print 'creating first admin user, login information:'
    print '\tname: admin'
    print '\temail: %s' % app.config['ADMINS'][0]
    print '\tpassword: password'
    admin = user_datastore.create_user(
            email=app.config['ADMINS'][0],
            name='admin',
            password=encrypt_password('password')
            )

    print 'adding roles to user'
    user_datastore.add_role_to_user(admin, superAdmin)
    user.created_at = datetime.utcnow()
    admin.created_at = datetime.utcnow()
    print 'finishing up'
    db.session.commit()


@manager.command
def db_upgrade():
    """ Upgrade the DB using alembic (run after db_migrate)
    """
    os.system('alembic upgrade head')

@manager.option('-m', '--message', dest='message', default='')
def db_migrate(message):
    """ Migrate db with new model changes
    """
    print message
    os.system('alembic revision --autogenerate -m "%s"' % message)

@manager.option('-g', '--gzip', dest='gzip', default=False)
def build_js(gzip):
    """ Builds the js for production
        Update JS_VERSION before doing this
        Optionally, gzip the javascript (must change how served)
        TODO: Build css here too. Right now flask-assets and flask-script don't play well
    """
    jsfile = 'app.min.' + app.config['JS_VERSION'] + '.js'
    os.system('cd data_news/static/js && node lib/r.js -o app.build.js out=%s'%jsfile)
    jsfile = 'data_news/static/js/' + jsfile
    require = 'data_news/static/js/require.js'
    if gzip:
        compress(jsfile)
        compress(require)

@manager.command
def clear_cache():
    """ Clears the whole applicaiton cache
        Useful for development, hard changes on prod
    """
    with app.app_context():
        cache.clear()

def shell_context():
    return dict(app=app)   

#runs the app
if __name__ == '__main__':
    manager.add_command('shell', Shell(make_context=shell_context))
    manager.run()