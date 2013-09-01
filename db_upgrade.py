#!venv
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
api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
print 'Current database version: ' + str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO))