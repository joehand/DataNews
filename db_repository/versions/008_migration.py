from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('email', String(length=255)),
    Column('password', String(length=255)),
    Column('name', String(length=255)),
    Column('active', Boolean),
    Column('created_at', DateTime),
    Column('confirmed_at', DateTime),
    Column('last_login_at', DateTime),
    Column('current_login_at', DateTime),
    Column('last_login_ip', String(length=255)),
    Column('current_login_ip', String(length=255)),
    Column('login_count', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['name'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['name'].drop()
