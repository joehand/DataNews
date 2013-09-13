# manage.py
from data_news import app
from flask.ext.script import Manager, Shell
from tweets import TweetGetter
import os

manager = Manager(app)
tweets = TweetGetter()

@manager.command
def twitter():
    tweets.get_mentions();
    tweets.get_favorites();
    print 'all done!'

@manager.command
def db_upgrade():
    os.system('alembic upgrade head')

@manager.option('-m', '--message', dest='message', default='')
def db_migrate(message):
    print message
    os.system('alembic revision --autogenerate -m "%s"' % message)

@manager.command
def build_js():
    os.system('cd data_news/static/js && node ../../../r.js -o app.build.js')

def shell_context():
    return dict(app=app)          

#runs the app
if __name__ == '__main__':
    manager.add_command('shell', Shell(make_context=shell_context))
    manager.run()