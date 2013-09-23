from data_news import app, db
from ..user import User
from ..frontend import Item, Vote

from flask import Blueprint
from flask.ext.restless import APIManager

api = APIManager(app, flask_sqlalchemy_db=db)

URL_PREFIX = '/api/v0'

item_excludes = ['user', 'user_from', 'user_to']
user_includes = ['created_at', 'id', 'karma']

# Create API endpoints, which will be available at api/v0/<tablename>
api.create_api(User, 
                   url_prefix=URL_PREFIX, 
                   methods=['GET'], 
                   include_columns=user_includes)

api.create_api(Item, 
                   url_prefix=URL_PREFIX, 
                   methods=['GET'], 
                   exclude_columns=item_excludes)

api.create_api(Vote, 
                   url_prefix=URL_PREFIX, 
                   methods=['GET'], 
                   exclude_columns=item_excludes)
