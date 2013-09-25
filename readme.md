# DataNews

[DataNews.co](http://datanews.co) is a web application for posting and discussing data-oriented news.

Built with:

* Python/Flask
* SQLalchemy
* Backbone.js
* Require.js
* Twitter Bootstrap

## Features

* Post and discuss URLs or Text
* Vote up any post or comment
* Nested discussions
* Permalinks for every post or comment
* User pages
* Admin section
* API
* Submit via Twitter

### Items (Post, Comment, Page, External)

The central part of DataNews is an ***item***. There are several kinds of items: `post`, `comment`, `page`, `external`. Each item can be accessed at a specific url: `/item/17`, where 17 is the item id number. 

Other notes:

* Every item has an owner, the user who created it.
* On the page for each item you can add comments, edit (if you are the owner), or upvote the item.

#### Posts, Comments

Posts and comments generally function the same. There is slightly different formatting and stying for Posts.

Every post has a Title and either a URL or Text. Comment consists of just text.

#### Page, External

Pages and External links are used to add links to the footer (held in Flask's global object). A page is an internal DataNews page (e.g. About). An external link is used to link outside the site.

Only super admins can add pages.

### Users

Login is required for anything except viewing pages. A logged in user can submit posts, comments, and up vote items. Every user has a unique URL to view their information. They can also use this page to change their username, email, or twitter handle.

We use Flask-Security to handle most of user creation and authetication (with some modification).

#### Roles

There are three types of user roles:

| Role       | Description  | Access  |
| ---------- | -------------| -----    |
| user       | The basic role given to all users. | Can submit posts and comment. |
| admin      | Basic admin role for editing comments or posts. | Can access basic admin panel for `Items` and `Votes`. |
| super      | Full-privilege admin to access the whole world. | Can access `User`, `Role`, and `Twitter` panels in admin area |

### Votes

Currently votes are only positive. A vote includes the user who votes, the item voted for, the user who created the item, and the timestamp.

### Submit Via Twitter

Users can submit via Twitter by adding their twitter handle to their user page (currently no verification). Then they tweet @DataNews.

There is a schedule process which checks for new mentions. If we have new mentions and we find a user with a handle then we begin the submission process. See background > twitter.py for full documentation.

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
| `db_migrate`  | Creates a db migration script using Alembic | `-m` allows you to add a migration message.|
| `db_upgrade`  | Upgrades db using most recent migration script.||
| `build_js`    |Builds the JS using r.js. Outputs a minified JS file to app.min.VERSION_NUMBER.js|`-g` allows you to gzip JS files (app.min.js and require.js).|
| `clear_cache` |Clears the application cache.||
| `twitter`     |Fetches posts submitted via twitter. Can be run as a background process. ||


## License

BSD license, Copyright (c) 2013 by Joe Hand. See license file for details.
