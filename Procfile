web: gunicorn data_news:app -b "0.0.0.0:$PORT" -w 9 -k gevent
fetch_twitter: python manage.py twitter
db_upgrade: python manage.py db_upgrade
db_migrate: python manage.py db_migrate