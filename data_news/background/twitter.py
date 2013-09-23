from data_news import db

from ..user import User
from ..frontend import Item, Vote
from .models import Twitter

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
    """ Class to get new tweets via api
        Can get favorite tweets or mentions
        Keeps track of max ids for both in DB
        Uses Twython to connect to twitter API
        Favorites get posted as user DataNews
    """
    try:
        TWITTER_USER = User.query.filter_by(name='DataNews').first()
    except:
        TWITTER_USER = None

    api =  Twython(TWITTER_KEY, 
                   TWITTER_SECRET,
                   TWITTER_OAUTH_TOKEN, 
                   TWITTER_OAUTH_SECRET)

    def __init__(self):
        """ Make sure we have an entry in the database
        """
        twitter = Twitter.query.limit(1).first()
        if twitter is None:
            twitter = Twitter(mention_id=0,fav_id=0)
            db.session.add(twitter)
            db.session.commit()
        self.twitter = twitter;
        self.mention_id = twitter.mention_id
        self.fav_id = twitter.fav_id

    def _check_mention_id(self, tweetid):
        """ Check where we are for mentions compared to new tweets
        """
        if self.mention_id < tweetid:
            print 'updating max mention id \n'
            self.mention_id = tweetid
            self.twitter.mention_id = tweetid
            db.session.commit()

    def _check_fav_id(self, tweetid):
        """ Check where we are for favorites compared to new tweets
        """
        if self.fav_id < tweetid:
            print 'updating max fav id \n'
            self.fav_id = tweetid
            self.twitter.fav_id = tweetid
            db.session.commit()


    def _get_title_url(self, url):
        """ Visits page to get title and real url from twitter URL
        """
        print 'getting title and content'
        br = Browser()
        try:
            res = br.open(url)
        except:
            return False
        url = res.geturl()
        data = res.get_data() 

        #Parse the content
        soup = BeautifulSoup(data, from_encoding="UTF-8")
        title = soup.find('title')

        #Outputs the content :)
        return {
                'title' : title.text.encode('utf-8'),
                'url' : url.encode('utf-8'),
                }

    def _clean_tweet_text(self, tweet):
        """ Clean up the tweet text
            Replaces short urls with display urls
            Makes urls links
            Adds a source
        """
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
        return text.encode('utf-8')
        
    def _process_tweets(self, tweets, mentions=False):
        """ Process tweets we got from API
            - Gets title, url
            - Cleans tweet text
            - Finds user
            - Submits to DB as new posts
        """
        for tweet in tweets:
            # TODO: Get urls besides just first, or deal with this better
            url = tweet['entities']['urls'][0]['expanded_url']

            content = self._get_title_url(url)

            if not content:
                print 'silly robots will not let us visit'
                #TODO: Find better way of dealing with sites we can't visit because robots.txt
                continue

            url = content['url']
            post = Item.query.filter_by(url = url).first()
            if post:
                #TODO: Add as comment to post?
                print 'duplicate post'
                continue

            text = self._clean_tweet_text(tweet)
            title = content['title']
            time = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            twitter_username = tweet['user']['screen_name']

            # Make the tweet text the title (minus links)
            # TODO: Remove user name too
            if not title:
                title = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', tweet['text'])

            if mentions:
              user = User.query.filter_by(twitter_handle=twitter_username).first()
              if not user:
                continue # skip the mention if we don't know who its from
            elif self.TWITTER_USER:
              user = self.TWITTER_USER
            else:
                continue

            print 'Adding Post:'
            print '\t' + title
            print '\t' + url
            print '\t' + text
            print '\t' + twitter_username
            print '\tDataNews User:'
            print '\t' + user.name

            post = Item(url = url.decode('utf-8'),
                           title = title.decode('utf-8'),
                           kind = 'post',
                           text =  text.decode('utf-8'),
                           timestamp = time,
                           user_id = user.id)

            db.session.add(post)
            db.session.commit()
            print 'post added'

            if mentions:
                self._check_mention_id(tweet['id'])
            else:
                self._check_fav_id(tweet['id'])
        return


    def get_mentions(self):
        """ Get mentions and run through processor
        """
        print 'getting mentions'
        if self.mention_id > 0:
            self._process_tweets(
                self.api.get_mentions_timeline(since_id = self.mention_id, count=200),
                mentions=True
            )
        else:
            self._process_tweets(
                self.api.get_mentions_timeline(count=200),
                mentions=True
            )
        print '\n'
        return

    def get_favorites(self):
        """ Get favs and run through processor
        """
        print 'getting favs'
        if self.fav_id > 0:
            self._process_tweets(
                self.api.get_favorites(since_id = self.fav_id, count=200)
            )
        else:
            self._process_tweets(self.api.get_favorites(count=200))
        return