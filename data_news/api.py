from data_news import app, db
from models import User, Item, Vote
from flask.ext.restless import APIManager

# Create the Flask-Restless API manager.
api_manager = APIManager(app, flask_sqlalchemy_db=db)


item_excludes = ['user', 'user_from', 'user_to']
user_includes = ['created_at', 'id', 'karma']

# Create API endpoints, which will be available at /api/v0/<tablename>
api_manager.create_api(User, 
                   url_prefix='/api/v0', 
                   methods=['GET'], 
                   include_columns=user_includes)

api_manager.create_api(Item, 
                   url_prefix='/api/v0', 
                   methods=['GET'], 
                   exclude_columns=item_excludes)

api_manager.create_api(Vote, 
                   url_prefix='/api/v0', 
                   methods=['GET', 'POST'], 
                   exclude_columns=item_excludes)
