
from data_news import db, cache
from .models import User
from .forms import UserForm

from flask import (render_template, request, flash, Blueprint,
                   redirect, url_for)

from flask.ext.security import login_required, current_user
from flask.ext.classy import FlaskView, route
from flask.ext.cache import make_template_fragment_key

user = Blueprint('user', __name__, url_prefix='/user')

class UserView(FlaskView):
    """ Get the beautiful user page
        Also a user can edit their own info here
        Base url is /user
        TODO: Add about section? And gravatar option?
              If we do more complex stuff, 
              allow use to see 'public' profile via request arg
        TODO: Clean up user index & make userful
    """
    route_base = '/'

    @route('/')
    @route('/<int:page>')
    def index(self, page=1):
        """ Show list of all users. Pretty useless right now
        """
        users_obj = User.query.paginate(page)
        return render_template('item/list.html', items=users_obj)

    @route('/<name>', endpoint='user')
    def get(self, name):
        """ Show specific user
            Put in form for editing if user = current user
        """
        user = User.find_user_by_name(name).first_or_404()
        if user == current_user:
            form = UserForm()
            return render_template('user/user.html', user=user, form=form, title=user.name)
        return render_template('user/user.html', user=user, title=user.name)

    @route('/active', endpoint='active_user')
    @login_required
    def active_user(self):
        """ Quick link for going to profile of current user
        """
        return redirect(url_for('.user', name=current_user.name))

    def post(self, name):
        """ Submit changes for user.
            NOT used to create a new user (that is done via flask-security)
        """
        user = User.find_user_by_name(name).first_or_404()
        form = UserForm()
        if user == current_user and form.validate_on_submit(): 
            old_name = current_user.name
            if form.email.data != '':   
                user.email = form.email.data
            user.name = form.name.data
            user.twitter_handle = form.twitter.data
            db.session.commit()

            key = make_template_fragment_key("user", vary_on=[old_name])
            cache.delete(key)

            flash('Your edits are saved, thanks.', category = 'info')
            return redirect(url_for('.user', name=form.name.data)) 

#Register our View Class
UserView.register(user)