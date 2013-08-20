from flask.ext.wtf import Form
from wtforms import TextField
from flask_wtf.html5 import URLField
from wtforms.validators import url, required


class SubmitForm(Form):
    title = TextField('Title', description='This is field one.',
                       validators=[required()])
    url = URLField('URL', description='This is field two.',
                       validators=[required(),url()])
