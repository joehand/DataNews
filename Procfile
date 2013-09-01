web: gunicorn data_news:app -b "0.0.0.0:$PORT" -w 9 -k gevent
upgrade_db: alembic upgrade head
fetch_twitter: python manage.py twitter