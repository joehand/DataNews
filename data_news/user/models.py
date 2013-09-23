from data_news import db, cache
from ..utils import ILLEGAL_NAMES

from flask.ext.security import UserMixin, RoleMixin
from sqlalchemy import func

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

class User(db.Model, UserMixin):
    """ Users!
        Nothing too crazy here
        The confirmed_at through login_count columns are updated by Flask-Security
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
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
            Returns Query object not user! Then can use first_or_404.
        """
        user_query = cls.query.filter(
                    func.lower(cls.name) == func.lower(name))
        return user_query

    @classmethod
    def find_user_by_email(cls, email):
        """ Finds user by EMAIL, making sure to look in all lowercase
            Returns Query object not user! Then can use first_or_404.
        """
        user_query = cls.query.filter(
                    func.lower(cls.email) == func.lower(email))
        return user_query

    @classmethod
    def find_user_by_twitter(cls, twitter):
        """ Finds user by EMAIL, making sure to look in all lowercase
            Returns Query object not user! Then can use first_or_404.
        """
        user_query = cls.query.filter(
                    func.lower(cls.twitter_handle) == func.lower(twitter))
        return user_query

    @classmethod
    def make_unique_name(cls, name):
        """ Checks if name is being used. If it is, returns a new version.
        """
        if name in ILLEGAL_NAMES:
            name = name + str(1)
        if not cls.find_user_by_name(name).first():
            return name
        version = 2
        while True:
            new_name = name + str(version)
            if not cls.find_user_by_name(new_name).first():
                break 
            version += 1
        return new_name
