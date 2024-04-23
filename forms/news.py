from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    content = TextAreaField("Содержание")
    picture = FileField('AddPicture', validators=[FileAllowed(['jpg', 'png'])])
    is_private = BooleanField("Личное")
    submit = SubmitField('Отправить')