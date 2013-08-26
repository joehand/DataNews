from data_news import app, db
from flask import render_template, request, flash, redirect, url_for, jsonify, session
from flask.ext.security import login_required, current_user
from datetime import datetime
from markdown import Markdown
from models import Item, User, Vote
from forms import PostForm, CommentForm, UserForm

md = Markdown(safe_mode='replace', 
                        html_replacement_text='--RAW HTML NOT ALLOWED--')

# Views
@app.route('/')
@app.route('/<int:page>')
def index(page = 1):
    posts = Item.ranked_posts(page)
    if current_user.is_anonymous() and page==1:
        flash('Welcome! <a class="alert-link" href="%s">Register here</a> to start contributing or just browse.' % url_for("security.register"))
    return render_template('index.html',
        items = posts)

@app.route('/item/<int:id>', methods = ['GET', 'POST'])
def item(id):
    form = CommentForm(request.values, kind="comment")
    item = Item.query.get(id)
    if request.method == 'POST' and form.validate_on_submit():
        comment = Item(text = md.convert(form.text.data),
                       kind = "comment",
                       parent_id = item.id,
                       parent = item,
                       timestamp = datetime.utcnow(),
                       user_id = current_user.id)

        db.session.add(comment)
        db.session.commit()

        vote = Vote(user_from_id = current_user.id,
                    user_to_id = current_user.id,
                    item_id = comment.id,
                    timestamp = datetime.utcnow())

        db.session.add(vote)
        db.session.commit()
        flash('Thanks for keeping the discussion alive!', category = 'success')
        return redirect(url_for('item', id=item.id) + '#item-' + str(comment.id)) 
    return render_template('item.html',
        item = item, form = form, title=item.title)


@app.route('/items')
@app.route('/items/<int:page>')
def items(page = 1):
    items = Item.query.order_by(Item.timestamp.desc()).paginate(page)
    filters = {}
    if request.args:
        for key, val in request.args.iteritems():
            filters[key] = val
        if 'name' in filters:
            filters['user_id'] = User.query.filter_by(name=request.args['name']).first().id
            filters.pop('name')

        items = Item.query.order_by(Item.timestamp.desc()).filter_by(**filters).paginate(page)
    return render_template('index.html', items=items, filters=filters)

@app.route('/submit', methods = ['GET', 'POST'])
@login_required
def submit():
    form = PostForm(request.values, kind="post")
    if form.validate_on_submit():
        post = Item.query.filter_by(url = form.url.data).first()

        if post:
            flash('URL already submitted', category = 'warning')
            return redirect(url_for('item', id=post.id))

        post = Item(url = form.url.data,
                    title = form.title.data,
                    kind = 'post',
                    text = md.convert(form.text.data),
                    timestamp = datetime.utcnow(),
                    user_id = current_user.id)
        db.session.add(post)
        db.session.commit()

        vote = Vote(user_from_id = current_user.id,
                    user_to_id = current_user.id,
                    item_id = post.id,
                    timestamp = datetime.utcnow())

        db.session.add(vote)
        db.session.commit()
        flash('Thanks for the submission!', category = 'success')
        return redirect(url_for('item', id=post.id)) 
    return render_template('submit.html', form=form, title='Submit')


@app.route('/comment/<int:id>', methods = ['GET', 'POST'])
@login_required
def comment(id):
    form = CommentForm(request.values, kind="comment")
    item = Item.query.get(id)
    if request.method == 'POST' and form.validate_on_submit():
        comment = Item(text = md.convert(form.text.data),
                       kind = "comment",
                       parent_id = item.id,
                       parent = item,
                       timestamp = datetime.utcnow(),
                       user_id = current_user.id)

        db.session.add(comment)
        db.session.commit()

        vote = Vote(user_from_id = current_user.id,
                    user_to_id = current_user.id,
                    item_id = comment.id,
                    timestamp = datetime.utcnow())

        db.session.add(vote)
        db.session.commit()
        flash('Thanks for keeping the discussion alive!', category = 'success')
        return redirect(url_for('item', id=item.id) + '#item-' + str(comment.id)) 
    return jsonify(html = render_template('_comment_form.html',
        item = item, form = form))


@app.route('/vote/<int:id>', methods = ['POST'])
@login_required
def vote(id):
    if request.method == 'POST':
        
        vote = Vote(user_from_id = current_user.id,
                    user_to_id = Item.query.get(id).user_id,
                    item_id = id,
                    timestamp = datetime.utcnow())

        db.session.add(vote)
        db.session.commit()
        flash('Thanks for the vote!', category = 'info')
        return redirect(url_for('item', id=id)) 
    return redirect(url_for('index'))

@app.route('/user/<name>', methods = ['GET', 'POST'])
def user(name):
    user = User.query.filter_by(name = name).first()
    if not user:
        flash('User does not exist', category='danger')
        return redirect(url_for('index'))
    if user == current_user:
        form = UserForm()
        if form.validate_on_submit():    
            user.email = form.email.data
            user.name = form.name.data
            user.twitter_handle = form.twitter.data
            db.session.commit()
            flash('Your edits are saved, thanks.', category = 'info')
            return redirect(url_for('user', name=name)) 
        return render_template('user.html', user=user, form=form, title=user.name)
    return render_template('user.html', user=user, title=user.name)
