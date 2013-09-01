from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
vote = Table('vote', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('from_user_id', Integer),
    Column('to_user_id', Integer),
    Column('item_id', Integer),
)

vote = Table('vote', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_from_id', Integer),
    Column('user_to_id', Integer),
    Column('item_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['vote'].columns['from_user_id'].drop()
    pre_meta.tables['vote'].columns['to_user_id'].drop()
    post_meta.tables['vote'].columns['user_from_id'].create()
    post_meta.tables['vote'].columns['user_to_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['vote'].columns['from_user_id'].create()
    pre_meta.tables['vote'].columns['to_user_id'].create()
    post_meta.tables['vote'].columns['user_from_id'].drop()
    post_meta.tables['vote'].columns['user_to_id'].drop()
