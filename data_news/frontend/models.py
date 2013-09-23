from data_news import db, cache

from ..utils import epoch_seconds

from flask.ext.sqlalchemy import Pagination
from sqlalchemy import func

from datetime import datetime
from math import log

class Vote(db.Model):
    """ We keep track of very vote
        Pretty simple here, we have:
            an item they voted on, 
            the voting user (user_from) 
            and the author (user_to)
            and the timestamp =)
        TODO: Add a value (if we want down votes)
    """
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    user_from_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_to_id =  db.Column(db.Integer, db.ForeignKey('user.id'))
    item_id =  db.Column(db.Integer, db.ForeignKey('item.id'))
    
    def __str__(self):
        return str(self.id)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id' : self.id,
           'timestamp' : dump_datetime(self.timestamp),
           'item_id' : self.item_id,
       }

class Item(db.Model):
    """ An item is any kind of post or comment
        It should either have a url/title or have text
        TODO: Right now kind is just a simple string ('post' or 'comment' or 'page' or 'external')
              It should probably be another table, similar to Role
        TODO?: There is no easy way to get the parent post for a deep nested comment
               You have to do recursion on each parent. Should I make this a column?
               parent currently refers to just the immediate parent (post or comment)
        TODO: Children is not working great with caching. How to make that nicer?
        TODO: user/votes is not working great with caching. How to make that nicer?
    """

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(140))
    url = db.Column(db.String(), unique=True)
    text = db.Column(db.String(3818))
    timestamp = db.Column(db.DateTime)
    last_changed = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='items', lazy='joined')
    kind = db.Column(db.String)
    votes = db.relationship('Vote', backref="item", primaryjoin="Vote.item_id==Item.id", lazy='joined')
    parent_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    children = db.relationship('Item',
                        backref=db.backref("parent", 
                                            remote_side='Item.id', 
                                            lazy='immediate',
                                            ),
                        lazy='dynamic',
                        order_by=db.desc('Item.timestamp')
                    ) 

    def __repr__(self):
        return '<Item %r>' % (self.id)
        
    def __str__(self):
        return str(self.id)

    @property
    def changed(self):
        return str(self.last_changed)

    @cache.memoize(60*5)
    def get_children(self):
        """ Get all the children of an item, recusively.
            Returns a list of tuples=(item object, depth).
        """
        recursiveChildren = []
        def recurse(item, depth):
            if depth != 0:
                recursiveChildren.append((item,depth))
            children = sorted(item.children, key=lambda x: x.comment_score, reverse=True)
            for child in children:
                recurse(child, depth + 1)

        recurse(self, 0)
        return recursiveChildren

    @cache.memoize(60*5)
    def voted_for(self, user_id):
        """ Check if an item was voted for by a user
        """
        vote = Vote.query.filter_by(item_id = self.id, user_from_id = user_id).first()
        if vote:
            return True
        return False

    @property
    def post_score(self):
        """Kinda from hot formula from Reddit.
           TODO: Actually think about this
        """
        votes = len(self.votes)
        comments = len(Item.query.filter_by(parent_id = self.id).all())
        date = self.timestamp
        s = votes * comments/10
        order = log(max(abs(s), 1), 10)
        sign = 1 if votes > 0 else -1 if votes < 0 else 0.1
        seconds = epoch_seconds(date) - 1134028003
        return round(order + sign * seconds / 45000, 7)

    @property
    def comment_score(self):
        """ Give comments a score based on votes, replies.
            TODO: Use brain.
        """
        votes = len(self.votes)
        comments = len(Item.query.filter_by(parent_id = self.id).all())
        s = votes * comments/10
        order = log(max(abs(s), 1), 10)
        sign = 1 if votes > 0 else -1 if votes < 0 else 0.1
        return round(order + sign, 7)

    @staticmethod
    @cache.memoize(60)
    def get_item_and_children(id):
        """ Get an item
            Make sure everything we will need loads, since we are caching
            TODO: Still not playing nice with cache
        """
        item = Item.query.options(
                                 db.joinedload('user'),
                                 db.joinedload('votes'),
                                ).get_or_404(id)
        return item

    @staticmethod
    @cache.memoize(60)
    def ranked_posts(page):
        """ Returns the top ranked posts by post_score
            (Kinda) Load all necessary sub-queries so we can cache
            TODO: This should be an combined with post_score to be a 
                  sqlalchemy query, but I keep breaking that =(
        """
        items = Item.query.options(db.joinedload('user'), 
                                  db.joinedload('votes')
                                 ).filter_by(kind = 'post').order_by(Item.timestamp.desc())
        items_paged = items.paginate(page)
        start = items_paged.per_page * (items_paged.page - 1)
        end = items_paged.per_page + start
        items_paged.items = sorted(items, 
                                   key=lambda x: x.post_score, 
                                   reverse=True)[start:end]
        #items_paged.adf
        return {'items' : items_paged.items, 
                'has_next' : items_paged.has_next,
                'next_num' : items_paged.next_num,
                }

    @staticmethod
    @cache.memoize(60*5)
    def find_by_title(title, kind='page'):
        """ Find a page by title
            Replace _ with spaces. Used to make nice URLs
        """
        title = title.replace('_', ' ')
        item_query = Item.query.filter_by(kind=kind).filter(
                    func.lower(Item.title) == func.lower(title)).first_or_404()
        return item_query


