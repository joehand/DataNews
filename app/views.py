from app import app, db
from flask import render_template, request, flash, redirect, url_for
from flask.ext.security import login_required, current_user
from datetime import datetime
from models import Item
from forms import PostForm, CommentForm

@app.before_first_request
def create_user():
    return

# Views
@app.route('/')
def index():
    posts = Item.query.filter_by(kind = 'post')
    return render_template('index.html',
        posts = posts)

# Views
@app.route('/item/<int:id>', methods = ['GET', 'POST'])
def item(id):
    form = CommentForm(request.values, kind="comment")
    item = Item.query.get(id)
    if request.method == 'POST' and form.validate_on_submit():
        comment = Item(text = form.text.data,
                       kind = form.kind.data,
                       parent_id = item.id,
                       parent = item,
                       timestamp = datetime.utcnow(),
                       user_id = current_user.id)

        db.session.add(comment)
        db.session.commit()
        flash('Thanks for the submission!', category = 'info')
        return redirect(url_for('item', id=item.id)) #change this to post
    return render_template('item.html',
        item = item, form = form)

# Views
@app.route('/submit', methods = ['GET', 'POST'])
@login_required
def submit():
    form = PostForm(request.values, kind="post")
    if request.method == 'POST' and form.validate_on_submit():
        post = Item.query.filter_by(url = form.url.data).first()

        if post:
            flash('URL already submitted', category = 'warning')
            return redirect(url_for('item', id=post.id)) #change this to post

        post = Item(url = form.url.data,
                    title = form.title.data,
                    kind = form.kind.data,
                    text = form.text.data,
                    timestamp = datetime.utcnow(),
                    user_id = current_user.id)

        db.session.add(post)
        db.session.commit()
        flash('Thanks for the submission!', category = 'info')
        return redirect(url_for('item', id=post.id)) #change this to post
    return render_template('submit.html', form=form)
