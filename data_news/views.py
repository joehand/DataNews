from data_news import app, db
from flask import render_template, request, flash, abort, \
                 redirect, url_for, jsonify, session, make_response, g
from flask.ext.security import login_required, current_user
from flask.ext.classy import FlaskView, route
from urlparse import urlparse
from datetime import datetime
from markdown import Markdown
from markdownify import markdownify
from bleach import clean
from models import Item, User, Vote
from forms import PostForm, CommentForm, UserForm, SearchForm


md = Markdown()
allowed_tags = ['a', 'p','em','strong','code','pre','blockquote','ul','li','ol']
super_tags = ['a', 'p','em','strong','code','pre','blockquote','ul','li','ol','h3','h4','h5','h6','img']

def clean_text(text):
    if current_user.is_super:
        return clean(md.convert(text), super_tags)
    else:
        return clean(md.convert(text), allowed_tags)

def submit_item(url=None, title=None, text=None, 
                    kind='comment', parent_id=None):
    """ Submits an item (post or comment) to db
    """ 
    text = clean_text(text)

    if kind=='comment' and not parent_id:
        return None

    item = Item(url = url,
                title = title,
                text = text,
                kind = kind,
                parent_id = parent_id,
                timestamp = datetime.utcnow(),
                user_id = current_user.id)

    db.session.add(item)
    db.session.commit()

    return item

@app.before_request
def before_request():
    session.permanent = True
    g.user = current_user
    if g.user.is_authenticated():
        g.user.current_login_at = datetime.utcnow()
        db.session.commit()
    elif request.endpoint == 'index':
        session['visited_index'] = True
    elif session.get('visited_index', False):
        session['return_anon'] = True
    g.search_form = SearchForm()
    g.pages = Item.query.filter_by(kind='page').order_by(Item.title)


class ItemView(FlaskView):
    route_base = '/'

    @route('/', endpoint='index')
    @route('/<int:page>')
    def index(self, page=1):
        """ Our main index view.
            Returns the top 20 ranked posts and paginates if necessary

            TODO: More awesomeness!
        """
        posts = Item.ranked_posts(page)
        return render_template('list.html',
            items = posts)

    @route('/item/<int:id>', endpoint='item')
    def get(self, id):
        """ View for a singular item (post or comment)
            Form is used to comment on that post or comment
            TODO: Make form a part of this class?
        """
        item_obj = Item.query.get_or_404(id)
        commentForm = CommentForm(request.values, kind="comment")
        return render_template('item.html',
            item = item_obj, form = commentForm, title=item_obj.title)

    @route('/<title>', endpoint='page')
    def get_page(self, title):
        """ View for a singular page (similar to item view but uses title)
            Form is used to comment on that post or comment
        """
        item_obj = Item.find_by_title(title).first_or_404()
        commentForm = CommentForm(request.values, kind="comment")
        return render_template('item.html',
            item = item_obj, form = commentForm, title=item_obj.title)

    def post(self, id):
        return 'hello'

ItemView.register(app)



@app.route('/title/<title>', methods = ['GET', 'POST'])
@app.route('/item2/<int:id>', methods = ['GET', 'POST'])
def page2(id=None,title=None):
    if request.args.get('edit', False) and current_user.id == item_obj.user_id:
        commentForm.text.data = markdownify(item_obj.text)
        commentForm.edit.data = True

        return render_template('item.html',
                item = item_obj, form = commentForm, title=item_obj.title, edit=True)

    if request.method == 'GET' and request.headers.get('formJSON', False):
        #Get only the comment reply form and return via JSON
        return jsonify(html = render_template('_comment_form.html',
        item = item_obj, form = commentForm))

    if commentForm.validate_on_submit():
        if commentForm.edit.data:
            item_obj.text = clean_text(commentForm.text.data)
            item_obj = db.session.merge(item_obj)
            db.session.commit()

            flash('Edit saved', 'info')
            response = make_response(render_template('item.html',
                        item = item_obj, form = commentForm, title=item_obj.title, edit=True))

            if item_obj.kind == 'page':
                next_url = url_for('item', title=item_obj.title, edit=True)
            else: 
                next_url = url_for('item', id=item_obj.id, edit=True)

            response.headers['X-PJAX-URL'] = next_url
            return response
        
        comment = submit_item(text=commentForm.text.data, parent_id=item_obj.id)

        if comment.id and comment.parent_id:
            flash('Thanks for adding to the discussion!', category = 'success')
        else:
            flash('Something went wrong adding your comment. Please try again', category='error')

        next_url = request.headers.get('source_url', request.url)
        path = urlparse(next_url)[2]
        next_id = path[path.rfind('/') + 1:]
        next_url = path + '#item-' + str(comment.id)

        #Redefine the items to pass to template for PJAX
        if 'item' in path:
            item_obj = Item.query.get_or_404(next_id)
        else: 
            item_obj = Item.find_by_title(next_id).first_or_404()
        commentForm = CommentForm()
        commentForm.text.data = '' #form data isn't clearing, so do it manually

        response = make_response(render_template('item.html',
                                item = item_obj, form = commentForm, title=item_obj.title))

        response.headers['X-PJAX-URL'] = next_url
        return response


@app.route('/items')
@app.route('/items/<int:page>')
def items(page = 1):
    """ Returns a sequential list of posts
        Add optional filters (used to get a user posts/comments)

        TODO: Change sort order via request args
    """
    filters = {}
    if request.args:
        for key, val in request.args.iteritems():
            filters[key] = val
        if 'name' in filters:
            filters['user_id'] = User.find_user_by_name(request.args['name']).first().id
            filters.pop('name')

        if '_pjax' in filters:
            filters.pop('_pjax')

        items_obj = Item.query.order_by(Item.timestamp.desc()).filter_by(**filters).paginate(page)
    else:
        items_obj = Item.query.order_by(Item.timestamp.desc()).paginate(page)
    return render_template('list.html', items=items_obj, filters=filters)

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

        if current_user.is_super and form.kind.data:
            kind = form.kind.data
        else:
            kind = 'post'

        post = submit_item(url = form.url.data,
                           title = form.title.data, 
                           text = form.text.data,
                           kind = kind)

        flash('Thanks for the submission!', category = 'success')

        return redirect(url_for('index'))
    return render_template('submit.html', form=form, title='Submit')


class UserView(FlaskView):
    """ Get the beautiful user page
        Also a user can edit their own info here
        TODO: Add about section? And gravatar option?
              If we do more complex stuff, 
              allow use to see 'public' profile via request arg
        TODO: Clean up user index & make userful
    """
    @route('/')
    @route('/<int:page>')
    def index(self, page=1):
        users_obj = User.query.paginate(page)
        return render_template('list.html', items=users_obj)

    @route('/<name>', endpoint='user')
    def get(self, name):
        user = User.find_user_by_name(name).first_or_404()
        if user == current_user:
            form = UserForm()
            return render_template('user.html', user=user, form=form, title=user.name)
        return render_template('user.html', user=user, title=user.name)

    def post(self, name):
        user = User.find_user_by_name(name).first_or_404()
        form = UserForm()
        if user == current_user and form.validate_on_submit():    
            user.email = form.email.data
            user.name = form.name.data
            user.twitter_handle = form.twitter.data
            db.session.commit()
            flash('Your edits are saved, thanks.', category = 'info')
            return redirect(url_for('user', name=form.name.data)) 

UserView.register(app)


@app.route('/search', methods = ['GET', 'POST'])
@app.route('/search/<query>')
@app.route('/search/<query>/<int:page>')
def search(query=None, page=1):
    if g.search_form.validate_on_submit():
        return redirect(url_for('search', query=g.search_form.search.data))
    if request.args.get('query', None):
        query = request.args.get('query')

    results = Item.paged_search(query, page)
    print results
    return render_template('list.html',
        query = query,
        items = results)


@app.errorhandler(404)
def internal_404(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_500(error):
    db.session.rollback()
    return render_template('500.html'), 500
