from data_news import app, db, cache
from flask.ext.security import UserMixin, RoleMixin
from flask.ext.sqlalchemy import Pagination
from sqlalchemy import func, case
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from math import log

epoch = datetime(1970, 1, 1)

@cache.memoize(60*5)
def epoch_seconds(date):
    """Returns the number of seconds from the epoch to date."""
    td = date - epoch
    return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)

@cache.memoize(60*5)
def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

def paginate(query, page, per_page=20, error_out=True):
    if error_out and page < 1:
        abort(404)
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    if not items and page != 1 and error_out:
        abort(404)

    # No need to count if we're on the first page and there are fewer
    # items than we expected.
    if page == 1 and len(items) < per_page:
        total = len(items)
    else:
        total = query.order_by(None).count()

    return Pagination(query, page, per_page, total, items)


# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

class Vote(db.Model):
    """ We keep track of very vote
        Pretty simple here, we have:
            an item they voted on, 
            the voting user (user_from) 
            and the author (user_to)
            and the timestamp =)
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

class User(db.Model, UserMixin):
    """ Users!
        Nothing too crazy here
        The confirmed_at through login_count columns are updated by Flask-Security
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(255), unique=True)
    active = db.Column(db.Boolean())
    created_at = db.Column(db.DateTime())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.Integer)
    twitter_handle = db.Column(db.String(20))
    karma = db.relationship('Vote', backref="user_to", primaryjoin="Vote.user_to_id==User.id")
    votes = db.relationship('Vote', backref="user_from", primaryjoin="Vote.user_from_id==User.id")
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<Item %r>' % (self.name)

    def __str__(self):
        return self.name

    @property
    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

    @property
    @cache.memoize(60*5)
    def is_admin(self):
        for role in self.roles:
            if role.name == 'admin' or role.name == 'super':
                return True
        return False

    @property
    @cache.memoize(60*5)
    def is_super(self):
        for role in self.roles:
            if role.name == 'super':
                return True
        return False

    @classmethod
    def find_user_by_name(cls, name):
        """ Finds user by name, making sure to look in all lowercase
            Returns Query object not user! Then can use first_or_404 if I want.
        """
        user_query = cls.query.filter(
                    func.lower(cls.name) == func.lower(name))
        return user_query

    @classmethod
    def find_user_by_email(cls, email):
        """ Finds user by EMAIL, making sure to look in all lowercase
            Returns Query object not user! Then can use first_or_404 if I want.
        """
        user_query = cls.query.filter(
                    func.lower(cls.email) == func.lower(email))
        return user_query

    @classmethod
    def find_user_by_twitter(cls, twitter):
        """ Finds user by EMAIL, making sure to look in all lowercase
            Returns Query object not user! Then can use first_or_404 if I want.
        """
        user_query = cls.query.filter(
                    func.lower(cls.twitter_handle) == func.lower(twitter))
        return user_query

    @classmethod
    def make_unique_name(cls, name):
        """ Checks if name is being used. If it is, returns a new version.
        """
        if not cls.find_user_by_name(name).first():
            return name
        version = 2
        while True:
            new_name = name + str(version)
            if not cls.find_user_by_name(new_name).first():
                break 
            version += 1
        return new_name


class Item(db.Model):
    """ An item is any kind of post or comment
        It should either have a url/title or have text
        TODO: Right now kind is just a simple string ('post' or 'comment')
              It should probably be another table, similar to Role
        TODO?: There is no easy way to get the parent post for a deep nested comment
               You have to do recursion on each parent. Should I make this a column?
               parent currently refers to just the immediate parent (post or comment)
    """

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(140))
    url = db.Column(db.String(), unique=True)
    text = db.Column(db.String(3818))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='items', lazy='joined')
    kind = db.Column(db.String)
    votes = db.relationship('Vote', backref="item", primaryjoin="Vote.item_id==Item.id")
    parent_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    children = db.relationship('Item',
                        backref=db.backref("parent", 
                                            remote_side='Item.id', 
                                            lazy='immediate',
                                            join_depth=9,
                                            ),
                        lazy='immediate',
                        join_depth=9,
                    ) 

    def __repr__(self):
        return '<Item %r>' % (self.id)
        
    def __str__(self):
        return str(self.id)

    @cache.memoize(30)
    def get_children(self):
        """ Get all the children of an item, recusively.
            Returns a list of tuples=(item object, depth).
        """
        recursiveChildren = []
        def recurse(item, depth):
            if depth != 0:
                recursiveChildren.append((item, depth))
            children = sorted(item.children, key=lambda x: x.comment_score, reverse=True)
            for child in children:
                recurse(child, depth + 1)

        recurse(self, 0)
        return recursiveChildren

    @cache.memoize(60*5)
    def voted_for(self, user_id):
        vote = Vote.query.filter_by(item_id = self.id, user_from_id = user_id).first()
        if vote:
            return True
        return False

    @property
    def post_score(self):
        """The hot formula from Reddit."""
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
        """Give comments a score based on votes, replies."""
        votes = len(self.votes)
        comments = len(Item.query.filter_by(parent_id = self.id).all())
        s = votes * comments/10
        order = log(max(abs(s), 1), 10)
        sign = 1 if votes > 0 else -1 if votes < 0 else 0.1
        return round(order + sign, 7)

    @classmethod
    @cache.memoize(30)
    def get_item_and_children(cls, id):
        """ Get an item
            Make sure everything we will need loads, since we are caching
        """
        item = cls.query.options(
                                 db.joinedload('user'),
                                 db.joinedload('votes'),
                                ).get_or_404(id)
        return item

    @classmethod
    @cache.memoize(30)
    def ranked_posts(cls, page):
        """ Returns the top ranked posts by post_score
            Load all necessary sub-queries so we can cache
            TODO: This should be an sqlalchemy query, but I kept breaking that =(
        """
        items = cls.query.options(db.joinedload('user'), 
                                  db.joinedload('votes')
                                 ).filter_by(kind = 'post').order_by(cls.timestamp.desc())
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


    @classmethod
    def find_by_title(cls, title, kind='page'):
        """ Find a page by title
            Replace _ with spaces. Used to make nice URLs
        """
        title = title.replace('_', ' ')
        item_query = cls.query.filter_by(kind=kind).filter(
                    func.lower(cls.title) == func.lower(title))
        return item_query


class Twitter(db.Model):
    """ Keep track of a few max id's for fetching via Twitter ID.
        Should only be one row in this table
    """
    id = db.Column(db.Integer, primary_key = True)
    mention_id = db.Column(db.BigInteger)
    fav_id = db.Column(db.BigInteger)

