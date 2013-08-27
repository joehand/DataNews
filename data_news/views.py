from data_news import app, db
from flask import render_template, request, flash, redirect, url_for, jsonify, session
from flask.ext.security import login_required, current_user
from datetime import datetime
from markdown import Markdown
from bleach import clean
from models import Item, User, Vote
from forms import PostForm, CommentForm, UserForm


def submit_item(url=None, title=None, text=None, 
                    kind='comment', parent_id=None):
    """ Submits an item (post or comment) to db
    """      
    md = Markdown()
    allowed_tags = ['p','em','strong','code','pre','blockquote','ul','li','ol']
    item = Item(url = url,
                title = title,
                text = clean(md.convert(text), allowed_tags),
                kind = kind,
                parent_id = parent_id,
                timestamp = datetime.utcnow(),
                user_id = current_user.id)

    db.session.add(item)
    db.session.commit()

    return item

@app.route('/')
@app.route('/<int:page>')
def index(page = 1):
    """ Our main index view.
        Returns the top 20 ranked posts and paginates if necessary

        TODO: More awesomeness!
    """

    posts = Item.ranked_posts(page)
    if current_user.is_anonymous() and page==1:
        flash('Welcome! <a class="alert-link" href="%s" data-pjax>Register here</a> to start contributing or just browse.' % url_for("security.register"))
    return render_template('index.html',
        items = posts)

@app.route('/item/<int:id>', methods = ['GET', 'POST'])
def item(id):
    """ View for a singular item (post or comment)
        Form is used to comment on that post or comment

        TODO: Redirect to orginal URL after comment instead of parent_id like we do now
              (user can come from many places, like a post-item page or comment-item page)
    """
    item = Item.query.get_or_404(id)

    form = CommentForm(request.values, kind="comment")
    if form.validate_on_submit():
        next_url = request.headers.get('source_url', None)
        comment = submit_item(text=form.text.data, parent_id=item.id)

        flash('Thanks for adding to the discussion!', category = 'success')

        if next_url:
            return redirect(next_url + '#item-' + str(comment.id))
        else:
            return redirect(request.url + '#item-' + str(comment.id))
    return render_template('item.html',
        item = item, form = form, title=item.title)


@app.route('/items')
@app.route('/items/<int:page>')
def items(page = 1):
    """ Returns a sequential list of posts
        Add optional filters (used to get a user posts/comments)

        TODO: Change sort order via request args
    """
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
    """ Submit a new post!

        TODO?: Where should I redirect to after this?
    """
    form = PostForm(request.values, kind="post")
    if form.validate_on_submit():
        post = Item.query.filter_by(url = form.url.data).first()

        if post:
            flash('URL already submitted', category = 'warning')
            return redirect(url_for('item', id=post.id))

        post = submit_item(url = form.url.data,
                           title = form.title.data, 
                           text = form.text.data,
                           kind = 'post')

        flash('Thanks for the submission!', category = 'success')
        return redirect(url_for('item', id=post.id)) 
    return render_template('submit.html', form=form, title='Submit')


@app.route('/comment/<int:id>', methods = ['GET', 'POST'])
@login_required
def comment(id):
    """ Get/Submit an inline comment (vs the above item page comments)
        GET returns json containing form HTML
        This page is accessed via ajax when hitting 'reply' link on comment
        No humans should come here. No big deal if they do, its just not exciting =).

        TODO: Same note as above - the redirecting one.
    """
    # Intercept and Redirect human access to item/parent_id for commenting
    if request.method == 'GET' and not request.headers.get('returnJSON', False):
        return redirect(url_for('item', id=id))

    #Otherwise send html form over json
    item = Item.query.get_or_404(id)


    form = CommentForm(request.values, kind="comment")
    if form.validate_on_submit():
        next_url = request.headers.get('source_url', None)

        comment = submit_item(text=form.text.data, parent_id=item.id)

        flash('Thanks for keeping the discussion alive!', category = 'success')

        if next_url:
            return redirect(next_url + '#item-' + str(comment.id))
        else:
            return redirect(url_for('item', id=id) + '#item-' + str(comment.id))
    return jsonify(html = render_template('_comment_form.html',
        item = item, form = form))


@app.route('/vote/<int:id>', methods = ['POST'])
@login_required
def vote(id):
    """ Vote for something. Woot. Page is actually not used...
        Should I send AJAX vote here or use the API like I am right now?
    """
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
    """ Get the beautiful use page
        Also a user can edit their own info here
        TODO: Handle upper/lower case in names better
        TODO: Add about section? And gravatar option?
              If we do more complex stuff, 
              allow use to see 'public' profile via request arg
    """
    user = User.query.filter_by(name = name).first_or_404()
    if user == current_user:
        form = UserForm()
        if form.validate_on_submit():    
            user.email = form.email.data
            user.name = form.name.data
            user.twitter_handle = form.twitter.data
            db.session.commit()
            flash('Your edits are saved, thanks.', category = 'info')
            return redirect(url_for('user', name=form.name.data)) 
        return render_template('user.html', user=user, form=form, title=user.name)
    return render_template('user.html', user=user, title=user.name)
