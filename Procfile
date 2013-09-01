web: gunicorn data_news:app -b "0.0.0.0:$PORT" -w 9 -k gevent
init: python db_create.py
upgrade: python db_upgrade.py
fetch_twitter: python manage.py twitter