from models import User
from flask.ext.wtf import Form
from wtforms import TextField, SelectMultipleField, HiddenField, TextAreaField
from flask_wtf.html5 import URLField, EmailField
from wtforms.validators import url, required, email
from flask_security.forms import RegisterForm
from sqlalchemy import func


class PostForm(Form):
    title = TextField('Title', description='',
                       validators=[required()])
    url = URLField('URL', description='',
                       validators=[url()])
    text = TextAreaField('Text', description='',
                       validators=[])
    kind = HiddenField('')

class CommentForm(Form):
    text = TextAreaField('',validators=[required()])
    kind = HiddenField('')
    parent_id = HiddenField('')

class UserForm(Form):
    name = TextField('Name',  validators=[required()], description="Public display name (Unique)")
    email = EmailField('Email',   validators=[email()])
    twitter = TextField('Twitter Username',   validators=[])

    def validate(self):
            rv = Form.validate(self)
            if not rv:
                return False
            user = User.query.filter(
                func.lower('name') == func.lower(self.name.data)).first()
            if user is None:
                return True
            else:
                print False
                name = User.make_unique_name(self.name.data)
                self.name.errors = ('Name already taken, perhaps %s suits you?' % name, '')
                return False
            if self.twitter.data and '@' in self.twitter.data:
                    self.twitter.data = self.twitter.data.replace('@', '')
            return True

class ExtendedRegisterForm(RegisterForm):
    name = TextField('Display Name',  validators=[required()], description="Will be public")
    email = EmailField('Email (Optional)',  validators=[], description="Private, used for password reset")

    def validate(self):
        rv = RegisterForm.validate(self)
        if not rv:
            return False

        if self.email.data:
            return self.email.validate(self.email.data)

        user = User.query.filter(
            func.lower('name') == func.lower(self.name.data)).first()
        if user is None:
            return True
        else:
            name = User.make_unique_name(self.name.data)
            self.name.errors.append('Name already taken, perhaps %s suits you?' % name)
            self.name.data = name
            return False
        return True
