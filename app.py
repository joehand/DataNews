import os

from data_news import app

#runs the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host ='0.0.0.0', port = port)