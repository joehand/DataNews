
from migrate.versioning import api
import os

if os.environ.get('HEROKU_PROD', False):
    from config import ProductionConfig
    config = ProductionConfig
else:
    from config import DevelopmentConfig
    config = DevelopmentConfig

SQLALCHEMY_DATABASE_URI = config.SQLALCHEMY_DATABASE_URI
SQLALCHEMY_MIGRATE_REPO = config.SQLALCHEMY_MIGRATE_REPO

v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
api.downgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, v - 1)
print 'Current database version: ' + str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO))