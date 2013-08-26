# manage.py
from data_news import app
from flask.ext.script import Manager
from tweets import TweetGetter
import os

manager = Manager(app)
tweets = TweetGetter()

@manager.command
def hello():
    print "hello"

@manager.command
def twitter():
    tweets.get_mentions();
    tweets.get_favorites();
    print 'all done!'

#runs the app
if __name__ == '__main__':
    manager.run()