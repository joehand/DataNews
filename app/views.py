from app import app, db, user_datastore
from flask import render_template, request, flash, redirect, url_for
from flask.ext.security import login_required, current_user
from datetime import datetime
from models import Post
from forms import SubmitForm

@app.before_first_request
def create_user():
    return

# Views
@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html',
        posts = posts)

# Views
@app.route('/submit', methods = ['GET', 'POST'])
@login_required
def submit():
    form = SubmitForm()
    if request.method == 'POST' and form.validate_on_submit():
        post = Post.query.filter_by(url = form.url.data).first()

        if post:
            flash('URL already submitted')
            return redirect(url_for('index')) #change this to post

        post = Post(url = form.url.data,
                    title = form.title.data,
                    timestamp = datetime.utcnow(),
                    user_id = current_user.id)

        db.session.add(post)
        db.session.commit()
        flash('Thanks for the submission!')
        return redirect(url_for('index')) #change this to post
    return render_template('submit.html', form=form)
