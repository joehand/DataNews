from flask.ext.wtf import Form
from wtforms import TextField, SelectMultipleField, HiddenField
from flask_wtf.html5 import URLField
from wtforms.validators import url, required


class PostForm(Form):
    title = TextField('Title', description='This is field one.',
                       validators=[required()])
    url = URLField('URL', description='This is field two.',
                       validators=[required(),url()])
    text = TextField('')
    kind = HiddenField('')

class CommentForm(Form):
    text = TextField('')
    kind = HiddenField('')