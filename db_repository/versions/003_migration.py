from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
vote = Table('vote', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('from_user_id', Integer),
    Column('to_user_id', Integer),
    Column('item_id', Integer),
)

item = Table('item', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('title', String),
    Column('url', String),
    Column('text', String),
    Column('timestamp', DateTime),
    Column('user_id', Integer),
    Column('votes', Integer),
    Column('kind', String),
    Column('parent_id', Integer),
)

user = Table('user', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('email', String),
    Column('password', String),
    Column('active', Boolean),
    Column('created_at', DateTime),
    Column('confirmed_at', DateTime),
    Column('last_login_at', DateTime),
    Column('current_login_at', DateTime),
    Column('last_login_ip', String),
    Column('current_login_ip', String),
    Column('login_count', Integer),
    Column('karma', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['vote'].create()
    pre_meta.tables['item'].columns['votes'].drop()
    pre_meta.tables['user'].columns['karma'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['vote'].drop()
    pre_meta.tables['item'].columns['votes'].create()
    pre_meta.tables['user'].columns['karma'].create()
