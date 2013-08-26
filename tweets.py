from data_news import app
from data_news import db
from data_news.models import User, Item, Vote, Twitter
from twython import Twython
from pprint import pprint
from BeautifulSoup import BeautifulSoup
from mechanize import Browser
from datetime import datetime
from markdown import Markdown

md = Markdown(safe_mode='replace', 
                        html_replacement_text='--RAW HTML NOT ALLOWED--')


class TweetGetter():
    TWITTER_USER = User.query.get(8)
    api =  Twython('51ghURR9oSl4eRlbiEkA', 
                  'YyEnU1fUOzatFKTABN3rYQBjM6jWAi5p2AfTXg7XBZY',
                  '285652996-KCBSoeyXCkEo9GDku7A6u08FDA2TjSPelKvjOqdt', 
                  '6wP5wsNWOq47lmk83yiGKD5F6QPxkoXlDRxhGqRH6RY')

    def __init__(self):
        twitter = Twitter.query.limit(1).first()
        if twitter is None:
            twitter = Twitter(max_mention_id=0,max_fav_id=0)
            db.session.add(twitter)
            db.session.commit()
        self.twitter = twitter;
        self.max_mention_id = twitter.max_mention_id
        self.max_fav_id = twitter.max_fav_id

    def check_max_mention_id(self, tweetid):
        if self.max_mention_id < tweetid:
            print 'updating max mention id \n'
            self.max_mention_id = tweetid
            self.twitter.max_mention_id = tweetid
            db.session.commit()

    def check_max_fav_id(self, tweetid):
        if self.max_fav_id < tweetid:
            print 'updating max fav id \n'
            self.max_fav_id = tweetid
            self.twitter.max_fav_id = tweetid
            db.session.commit()


    def get_title(self, url):
        #This retrieves the webpage content
        br = Browser()
        res = br.open(url)
        data = res.get_data() 

        #This parses the content
        soup = BeautifulSoup(data, fromEncoding="UTF-8")
        title = soup.find('title')

        #This outputs the content :)
        return title.text

    def process_tweets(self, tweets, mentions=False):
        for tweet in tweets:
            if mentions:
                self.check_max_mention_id(tweet['id'])
            else:
                self.check_max_fav_id(tweet['id'])


            url = tweet['entities']['urls'][0]['expanded_url']
            post = Item.query.filter_by(url = url).first()
            if post:
                print 'duplicate post'
                continue

            text = tweet['text']
            title = self.get_title(url)
            time = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            twitter_username = tweet['user']['screen_name']

            print text
            print title
            print twitter_username

            if mentions:
              user = User.query.filter_by(twitter_handle=twitter_username).first()
              if not user:
                continue # skip the mention if we don't know who its from
            else:
              user = self.TWITTER_USER

            post = Item(url = url,
                           title = title,
                           kind = 'post',
                           text = md.convert(text),
                           timestamp = time,
                           user_id = user.id)

            db.session.add(post)
            db.session.commit()

            vote = Vote(user_from_id = user.id,
                           user_to_id = user.id,
                           item_id = post.id,
                           timestamp = time)

            db.session.add(vote)
            db.session.commit()
        return


    def get_mentions(self):
        print 'getting mentions'
        if self.max_mention_id > 0:
            self.process_tweets(
                self.api.get_mentions_timeline(since_id = self.max_mention_id, count=200),
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
        if self.max_fav_id > 0:
            self.process_tweets(
                self.api.get_favorites(since_id = self.max_fav_id, count=200)
            )
        else:
            self.process_tweets(self.api.get_favorites(count=200))
        return