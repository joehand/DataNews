from .models import User
from ..utils import NAME_LEN_MIN, NAME_LEN_MAX, ILLEGAL_NAMES

from flask.ext.wtf import Form
from flask.ext.wtf.html5 import URLField, EmailField
from wtforms import TextField
from wtforms.validators import required, email, optional
from flask.ext.security import current_user
from flask.ext.security.forms import RegisterForm, LoginForm
from flask.ext.security.utils import verify_and_update_password

import re

class UserForm(Form):
    """ Form to edit the user
        Used only on editing, not creation
        TODO: Combine this and the form below
        TODO: This is not DRY
    """
    name = TextField('Name',  validators=[required()], description="Public display name (Unique)")
    email = EmailField('Email',   validators=[optional(), email()])
    twitter = TextField('Twitter Username',   validators=[optional()])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        validate_email = True
        validate_name = True
        validate_twitter = True

        if self.twitter.data and '@' in self.twitter.data:
            self.twitter.data = self.twitter.data.replace('@', '')

        name = self.name.data
        email = self.email.data
        twitter = self.twitter.data

        current_name = current_user.name
        current_email = current_user.email
        current_twitter = current_user.twitter_handle


        if email == current_email:
            validate_email = False
        if name == current_name:
            validate_name = False
        if twitter == current_twitter:
            validate_twitter = False

        if not re.match("^[a-zA-Z0-9_-]+$", name):
            self.name.errors.append('Only letters, digits, dashes, underscores allowed')
            return False

        if not re.search("[a-zA-Z0-9]", name):
            self.name.errors.append('Must have at least one letter or number')
            return False

        if not NAME_LEN_MIN < len(name) + 1 < NAME_LEN_MAX:
            self.name.errors.append('Must be between %s and %s characters'% (NAME_LEN_MIN,NAME_LEN_MAX)) 
            return False

        if name.lower() in ILLEGAL_NAMES:
            self.name.errors.append('Name not allowed. Please try another.')
            self.name.data = ''
            return False

        user = User.find_user_by_name(name).first()
        if validate_name and user is not None:
            name = User.make_unique_name(name)
            self.name.errors.append('Name already taken, perhaps %s suits you?' % name)
            self.name.data = name
            return False
        
        if validate_email and self.email.data and self.email.validate(self.email.data):
            user = User.find_user_by_email(self.email.data).first()
            if user is not None:
                self.email.errors.append('Email address already used')
                return False

        if validate_twitter and self.twitter.data:
            user = User.find_user_by_twitter(self.twitter.data).first()
            if user is not None:
                self.twitter.errors.append('Twitter username already used')
                return False

        return True

class ExtendedRegisterForm(RegisterForm):
    """ Extend the Flask-Security registration form
        Makes email optional and adds a Name
        TODO: This is not DRY
    """
    name = TextField('Display Name',  validators=[required()], description="Will be public")
    email = EmailField('Email (Optional)',  validators=[optional(), email()], description="Private, used for password reset")

    def validate(self):
        rv = RegisterForm.validate(self)
        if not rv:
            return False

        if self.email.data and self.email.validate(self.email.data):
            user = User.find_user_by_email(self.email.data).first()
            if user is not None:
                self.email.errors.append('Email address already used')
                return False

        
        name = self.name.data

        if name.lower() in ILLEGAL_NAMES:
            self.name.errors.append('Name not allowed. Please try another.')
            self.name.data = ''
            return False

        if not re.match("^[a-zA-Z0-9_-]+$", name):
            self.name.errors.append('Only letters, digits, dashes, underscores allowed')
            return False

        if not re.search("[a-zA-Z0-9]", name):
            self.name.errors.append('Must have at least one letter or number')
            return False

        if not NAME_LEN_MIN < len(name) + 1 < NAME_LEN_MAX:
            self.name.errors.append('Must be between %s and %s characters'% (NAME_LEN_MIN,NAME_LEN_MAX)) 
            return False

        user = User.find_user_by_name(name).first()
        if user is not None:
            name = User.make_unique_name(name)
            self.name.errors.append('Name already taken, perhaps %s suits you?' % name)
            self.name.data = name
            return False
        return True


class ExtendedLoginForm(LoginForm):
    """ Extend the Flask-Security registration form
        Makes email optional and adds a Name
    """
    name = TextField('Name OR Email',  validators=[required()])

    def validate(self):
        name = self.name.data
        self.name.errors = [] #not sure why errors are being passed in a tuples
        self.password.errors = []
        if name.strip() == '':
            self.name.errors.append('Please enter a name')
            return False   

        self.user = User.find_user_by_name(name).first()

        if self.user is None:
            self.user = User.find_user_by_email(email=name).first()
            if self.user is None:
                self.name.errors.append('User does not exist, please register')
                return False
        if not verify_and_update_password(self.password.data, self.user):
            self.password.errors.append('Password is not valid')
            return False
        if not self.user.is_active():
            self.name.errors.append('Account has been disabled')
            return False
        return True
