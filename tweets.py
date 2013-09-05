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
                'title' : title.text.decode('utf-8'),
                'url' : url,
                }

    def clean_tweet_text(self, tweet):
        text = tweet['text']
        entities = tweet['entities']
        user = tweet['user']
        for url in entities['urls']:
            new_url = '<a href="' + url['expanded_url'] + '">' + url['display_url'] + '</a>'
            text = text.replace(url['url'], new_url)
        source = '<a class="text-muted" href="https://twitter.com/' \
                            + user['screen_name'] + '/status/' \
                            + tweet['id_str'] + '">' \
                            + '(via @' + user['screen_name'] + ')</a>'
        text = '<p>' + text + '<small> ' + source + '</small></p>'
        return text.decode('utf-8')
        
    def process_tweets(self, tweets, mentions=False):
        for tweet in tweets:

            url = tweet['entities']['urls'][0]['expanded_url']

            content = self.get_title_url(url)

            if not content:
                print 'silly robots will not let us visit'
                #TODO: Find better way of dealing with sites we can't visit because robots.txt
                continue

            url = content['url']
            post = Item.query.filter_by(url = url).first()
            if post:
                print 'duplicate post'
                continue

            text = self.clean_tweet_text(tweet)
            title = content['title']
            time = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            twitter_username = tweet['user']['screen_name']

            if not title:
                title = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', tweet['text'])

            if mentions:
              user = User.query.filter_by(twitter_handle=twitter_username).first()
              if not user:
                continue # skip the mention if we don't know who its from
            else:
              user = self.TWITTER_USER

            print 'Adding Post:'
            print '\t' + title
            print '\t' + url
            print '\t' + text
            print '\t' + twitter_username
            print '\t DataNews User:'
            print '\t ' + user.name

            print 'trying to add post'
            post = Item(url = url,
                           title = title,
                           kind = 'post',
                           text =  text,
                           timestamp = time,
                           user_id = user.id)

            db.session.add(post)
            db.session.commit()
            print 'post added'

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