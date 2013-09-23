from data_news import db, cache
from ..utils import ALLOWED_TAGS, SUPER_TAGS

from .models import Item, Vote
from .forms import PostForm, CommentForm

from flask import (render_template, request, flash, Blueprint,
                   redirect, url_for, jsonify, session, make_response)

from flask.ext.security import login_required, current_user
from flask.ext.classy import FlaskView, route
from flask.ext.cache import make_template_fragment_key

from markdown import Markdown
from markdownify import markdownify
from bleach import clean

from urlparse import urlparse
from datetime import datetime
import json
import urllib

frontend = Blueprint('frontend', __name__)

md = Markdown()

class ItemView(FlaskView):
    """ Our base ViewClass for any Item related endpoings (posts, comments, pages)
        Base is root of app
        Get routes and post routes are all separate functions
    """
    route_base = '/'

    def _commentForm(self, request):
        return CommentForm(request.values, kind="comment")

    def _clean_text(self, text):
        """ Cleans up submitted text from users
        """
        if current_user.is_super:
            text = clean(md.convert(text), SUPER_TAGS)
        else:
            text = clean(md.convert(text), ALLOWED_TAGS)
        
        return text

    def _submit_item(self, url=None, title=None, text=None, 
                            kind='comment', parent_id=None):
        """ Submits an item (post or comment) to db
            TODO: Some kind of bad language filter?
        """ 
        text = self._clean_text(text)

        if kind=='comment' and not parent_id:
            return None

        item = Item(url = url,
                    title = title,
                    text = text,
                    kind = kind,
                    parent_id = parent_id,
                    timestamp = datetime.utcnow(),
                    last_changed = datetime.utcnow(),
                    user_id = current_user.id)

        db.session.add(item)
        db.session.commit()

        # TODO : Need to delete cache of just related items, not all
        cache.delete_memoized(Item.ranked_posts)
        cache.delete_memoized(Item.get_item_and_children)
        cache.delete_memoized(Item.get_children)

        return item

    def before_index(self, page=1):
        """ Used to mark a visit of index page and remove welcome screen
            TODO: Optimize by running this only when necessary (is that possible?)
        """ 
        if current_user.is_anonymous() and not session.get('visited_index', False):
            session['visited_index'] = True


    @route('/', endpoint='index')
    @route('/<int:page>', endpoint='index')
    def index(self, page=1):
        """ Our main index view.
            Returns the top 20 ranked posts and paginates if necessary

            TODO: More awesomeness!
        """
        posts = Item.ranked_posts(page)
        return render_template('item/list.html',
            items = posts, title='Home')

    @route('/item/<int:id>', endpoint='item')
    def get_item(self, id):
        """ View for a singular item (post or comment)
            Form is used to comment on that post or comment
        """
        item = Item.get_item_and_children(id)
        commentForm = self._commentForm(request)

        #TODO: Having trouble with cache. Delete if we can't find votes/user info and get again
        try:
            print item.votes
            print item.user.name
        except:
            print 'Could not get votes or user info'
            cache.delete_memoized(Item.ranked_posts)
            cache.delete_memoized(Item.get_item_and_children)
            item = Item.get_item_and_children(id)

        title = item.title
        if item.kind == 'comment':
            title = item.user.name + ' comment'
        return render_template('item/item.html',
            item = item, form = commentForm, title=title)

    @route('/<title>', endpoint='page')
    def get_page(self, title):
        """ View for a singular page (similar to item view but uses title)
            Form is used to comment on that post or comment
        """
        page = Item.find_by_title(title)
        commentForm = self._commentForm(request)
        return render_template('item/item.html',
            item = page, form = commentForm, title=page.title)

    @route('/items', endpoint='items')
    @route('/items/<int:page>', endpoint='items')
    def get_items(self, page=1):
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
        return render_template('item/list.html', items=items_obj, filters=filters, title='Recent')


    @route('/item/edit/<int:id>', endpoint='item_edit')
    @login_required  #TODO: change to user = owner
    def get_edit(self, id):
        """ Get route for Editing an Item
            TODO: Make decorator for "owership" of item
        """
        item = Item.query.get_or_404(id)
        if current_user.id == item.user_id:
            commentForm = self._commentForm(request)
            commentForm.text.data = markdownify(item.text)
            commentForm.edit.data = True

            return render_template('item/item.html',
                item = item, form = commentForm, title=item.title, edit=True)
        else:
            return redirect(url_for('.item', id=id))


    @route('/reply/<int:id>', endpoint='item_comment')
    def get_comment_form(self, id):
        """
            Returns the comment reply form html via JSON
            Requires the header to be set (via js) : formJSON = True
        """
        if request.headers.get('formJSON', False):
            item = Item.query.get_or_404(id)
            commentForm = self._commentForm(request)
            return jsonify(html = render_template('item/_comment_form.html',
                        item = item, form = commentForm))
        else:
            return redirect(url_for('.item', id=id))

    @route('/submit', endpoint='submit')
    @login_required
    def get_submit(self):
        """ Get page for submitting new post!
        """
        form = PostForm(request.values, kind="post")
        return render_template('item/submit.html', form=form, title='Submit')


    @route('/submit', methods=['POST'])
    @login_required
    def post_submit(self):
        """ Post route for submitting new post
        """
        form = PostForm(request.values, kind="post")
        if form.validate_on_submit():
            post = Item.query.filter_by(url = form.url.data).first()

            if post:
                flash('URL already submitted', category = 'warning')
                return redirect(url_for('.item', id=post.id))

            if current_user.is_super and form.kind.data:
                kind = form.kind.data
            else:
                kind = 'post'


            post = self._submit_item(url = form.url.data,
                               title = form.title.data, 
                               text = form.text.data,
                               kind = kind)

            flash('Thanks for the submission!', category = 'success')

            # Make new response and set url header for PJAX
            response = make_response(self.get_item(post.id))
            response.headers['X-PJAX-URL'] = url_for('frontend.item', id=post.id)
            return response
        else:
            return render_template('item/submit.html', form=form, title='Submit')

    @route('/item/<int:id>', methods=['POST'])
    @route('/<title>', methods=['POST'])
    @login_required
    def post_item_comment(self, id=None, title=None):
        """ Post route for creating new comment on any item or page
        """
        commentForm = self._commentForm(request)
        if not id:
            id = Item.find_by_title(title).id
        if commentForm.validate_on_submit():
            comment = self._submit_item(text=commentForm.text.data, parent_id=id)

            if comment.id and comment.parent_id:
                flash('Thanks for adding to the discussion!', category = 'success')
            else:
                flash('Something went wrong adding your comment. Please try again', category='error')
                return render_template('item/submit.html', form=form, title='Submit')

            # Figure out what url we submitted from so we can keep them there
            next_url = request.headers.get('source_url', request.url)
            path = urlparse(next_url)[2]
            next_id = path[path.rfind('/') + 1:]
            next_url = path + '#item-' + str(comment.id)

            #Redefine the items to pass to template for PJAX
            if 'item' in path:
                item = Item.query.get_or_404(next_id)
            else:
                #TODO: Delete only necessary item
                cache.delete_memoized(Item.find_by_title)
                next_id = urllib.unquote(next_id)
                item = Item.find_by_title(next_id)

            commentForm = self._commentForm(request)
            commentForm.text.data = '' #form data isn't clearing, so do it manually

            # Make new response and set url header for PJAX
            response = make_response(render_template('item/item.html',
                                    item = item, form = commentForm, title=item.title))
            response.headers['X-PJAX-URL'] = next_url
            return response
        else:
            return render_template('item/submit.html', form=form, title='Submit')



    @route('/item/edit/<int:id>', methods=['POST'])
    @login_required #change to user = owner
    def post_edit(self, id):
        """ Post Route for Edit an item
            TODO: Ability to edit title/url for posts
        """
        commentForm = self._commentForm(request)
        item = Item.query.get_or_404(id)
        if commentForm.validate_on_submit():
            item.text = self._clean_text(commentForm.text.data)
            item.last_changed = datetime.utcnow()
            item = db.session.merge(item)
            db.session.commit()

            #TODO: Delete only necessary items
            cache.delete_memoized(Item.get_children)
            cache.delete_memoized(Item.get_item_and_children)
            key = make_template_fragment_key("item_text", vary_on=[item.__str__(), item.changed])
            cache.delete(key)

            flash('Edit saved', 'info')
            response = make_response(render_template('item/item.html',
                        item = item, form = commentForm, title=item.title, edit=True))
            next_url = url_for('frontend.item_edit', id=item.id)

            response.headers['X-PJAX-URL'] = next_url
            return response
        else:
            return render_template('item/item.html',
                        item = item, form = commentForm, title=item.title, edit=True)

    @route('/vote/<int:id>', methods=['POST'], endpoint='vote')
    @login_required
    def post_vote(self, id):
        """ Post Route for adding a vote
            Submitted via AJAX
        """
        new_vote = json.loads(request.data)
        vote = Vote(timestamp = datetime.utcnow(),
                    user_from_id = current_user.id,
                    user_to_id =  new_vote['user_to_id'],
                    item_id =  new_vote['item_id']
                )

        db.session.add(vote)
        db.session.commit()

        #TODO: Delete only necessary items
        cache.delete_memoized(Item.voted_for)
        cache.delete_memoized(Item.get_children)
        cache.delete_memoized(Item.get_item_and_children)
        cache.delete_memoized(Item.ranked_posts)

        return jsonify(vote.serialize)

#Register our View Classes
ItemView.register(frontend)

