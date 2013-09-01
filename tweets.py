from data_news import app
from data_news import db
from data_news.models import User, Item, Vote, Twitter
from twython import Twython
from pprint import pprint
from markdown import Markdown
from bs4 import BeautifulSoup
from mechanize import Browser
from datetime import datetime
import re
import os 

TWITTER_KEY = os.environ.get('TWITTER_KEY')
TWITTER_SECRET = os.environ.get('TWITTER_SECRET')
TWITTER_OAUTH_TOKEN = os.environ.get('TWITTER_OAUTH_TOKEN')
TWITTER_OAUTH_SECRET = os.environ.get('TWITTER_OAUTH_SECRET')


md = Markdown()
class TweetGetter():
    TWITTER_USER = User.query.filter_by(name='DataNews').first()
    api =  Twython(TWITTER_KEY, 
                   TWITTER_SECRET,
                   TWITTER_OAUTH_TOKEN, 
                   TWITTER_OAUTH_SECRET)

    def __init__(self):
        twitter = Twitter.query.limit(1).first()
        if twitter is None:
            twitter = Twitter(mention_id=0,fav_id=0)
            db.session.add(twitter)
            db.session.commit()
        self.twitter = twitter;
        self.mention_id = twitter.mention_id
        self.fav_id = twitter.fav_id

    def check_mention_id(self, tweetid):
        if self.mention_id < tweetid:
            print 'updating max mention id \n'
            self.mention_id = tweetid
            self.twitter.mention_id = tweetid
            db.session.commit()

    def check_fav_id(self, tweetid):
        if self.fav_id < tweetid:
            print 'updating max fav id \n'
            self.fav_id = tweetid
            self.twitter.fav_id = tweetid
            db.session.commit()


    def get_title_url(self, url):
        #This retrieves the webpage content
        br = Browser()
        try:
            res = br.open(url)
        except:
            return False
        url = res.geturl()
        data = res.get_data() 


        #This parses the content
        soup = BeautifulSoup(data, from_encoding="UTF-8")
        title = soup.find('title')

        #This outputs the content :)
        return {
                'title' : title.text,
                'url' : url,
                }

    def process_tweets(self, tweets, mentions=False):
        for tweet in tweets:

            url = tweet['entities']['urls'][0]['expanded_url']
            post = Item.query.filter_by(url = url).first()
            if post:
                print 'duplicate post'
                continue


            content = self.get_title_url(url)

            if not content:
                print 'silly robots will not let us visit'
                #TODO: Find better way of dealing with sites we can't visit because robots.txt
                continue

            title = content['title']
            url = content['url']
            text = tweet['text']
            time = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            twitter_username = tweet['user']['screen_name']

            if not title:
                title = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', text)

            if mentions:
              user = User.query.filter_by(twitter_handle=twitter_username).first()
              if not user:
                continue # skip the mention if we don't know who its from
            else:
              user = self.TWITTER_USER

            print 'Adding Post:'
            print title, url, text, twitter_username
            print 'DataNews User:'
            print user.name

            post = Item(url = url,
                           title = title,
                           kind = 'post',
                           text =  md.convert(tweet['text']),
                           timestamp = time,
                           user_id = user.id)

            db.session.add(post)
            db.session.commit()

            if mentions:
                self.check_mention_id(tweet['id'])
            else:
                self.check_fav_id(tweet['id'])
        return


    def get_mentions(self):
        print 'getting mentions'
        if self.mention_id > 0:
            self.process_tweets(
                self.api.get_mentions_timeline(since_id = self.mention_id, count=200),
                mentions=True
            )
        else:
            self.process_tweets(
                self.api.get_mentions_timeline(count=200),
                mentions=True
            )
        print '\n'
        return

    def get_favorites(self):
        print 'getting favs'
        if self.fav_id > 0:
            self.process_tweets(
                self.api.get_favorites(since_id = self.fav_id, count=200)
            )
        else:
            self.process_tweets(self.api.get_favorites(count=200))
        return