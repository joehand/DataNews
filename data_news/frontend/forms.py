from flask.ext.wtf import Form
from flask.ext.wtf.html5 import URLField
from wtforms import TextField, HiddenField, TextAreaField
from wtforms.validators import url, required, optional


class PostForm(Form):
    """ Form to submit a Post
        TODO: Put a note in about Markdown formatting?
    """
    title = TextField('Title', description='',
                       validators=[required()])
    url = URLField('URL', description='',
                       validators=[url(), optional()])
    text = TextAreaField('Text', description='',
                       validators=[])
    kind = TextField('Kind')

class CommentForm(Form):
    """ Form to submit a Comment
        TODO: Put a note in about Markdown formatting?
    """
    text = TextAreaField('',validators=[required()])
    kind = HiddenField('')
    parent_id = HiddenField('')
    edit = HiddenField('')
