from app import app, db
from datetime import datetime
from flask.ext.security import UserMixin, RoleMixin

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
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    created_at = db.Column(db.DateTime())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.Integer)
    karma = db.Column(db.Integer)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    items = db.relationship('Item', backref='user',
                                lazy='dynamic')

    def __str__(self):
        return self.email

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

    def is_admin(self):
        for role in self.roles:
            if role.name == 'admin' or role.name == 'super':
                return True
        return False

    def is_super(self):
        for role in self.roles:
            if role.name == 'super':
                return True
        return False



class Item(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(140))
    url = db.Column(db.String(), unique=True)
    text = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    votes = db.Column(db.Integer)
    kind = db.Column(db.String)
    parent_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    parent = db.relation('Item', remote_side=id, backref="children")

    def __repr__(self):
        return '<Item %r>' % (self.id)
        
    def __str__(self):
        return str(self.id)


    def get_children(self, length=False):
        """ Get all the children of an item, recusively.
            Returns a list of tuples=(item object, depth).
        """
        recursiveChildren = []
        def recurse(item, depth):
            if depth != 0:
                recursiveChildren.append((item, depth))
            for child in item.children:
                recurse(child, depth + 1)

        recurse(self, 0)
        if length:
            return len(recursiveChildren)
        return recursiveChildren


