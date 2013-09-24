# DataNews

[DataNews.co](http://datanews.co) is a web application for posting and discussing data-oriented news.

Built with:

* Python/Flask
* SQLalchemy
* Backbone.js
* Require.js
* Twitter Bootstrap

## Development

DataNews uses Flask and several Flask extensions. 

### Local Development

* Clone the repository
* Create and activate a virtual environment
* Install packages with `pip install -r requirements.txt`
* Create database with `python manage.py db_create`. This will create a local sqlite database.
* Run local webserver with `python manage.py runserver`

### Script Commands

There are several commands available in manage.py. Each can be run with `python manage.py command`.

| Command       | Description  | Options  |
| ------------- | -------------| -----    |
| `runserver`   | Runs Flask's development server at [localhost:5000](http://localhost:5000).| |
| `db_create`   | Drops all old tables and creates a new database. Will also create a super-admin user with un: *admin* and pw: *password*. This account is associated with the first admin listed in the config file. ||
| `db_migrate`  | Creates a db migration script using Alembic. Option | `-m` allows you to add a migration message.|
| `db_upgrade`  | Upgrades db using most recent migration script.||
| `build_js`    |Builds the JS using r.js. Outputs a minified JS file to app.min.VERSION_NUMBER.js. Option `-g` allows you to gzip JS files (app.min.js and require.js).||
| `clear_cache` |Clears the application cache.||
| `twitter`     |Fetches posts submitted via twitter. Can be run as a background process. ||


