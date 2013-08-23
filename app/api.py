from app import manager
from models import User, Item


item_excludes = ['user']
user_includes = ['created_at', 'id', 'karma']

# Create API endpoints, which will be available at /api/v0/<tablename>
manager.create_api(User, 
                   url_prefix='/api/v0', 
                   methods=['GET'], 
                   include_columns=user_includes)

manager.create_api(Item, 
                   url_prefix='/api/v0', 
                   methods=['GET'], 
                   exclude_columns=item_excludes)
