from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed
class OrderForm(FlaskForm):

    email = EmailField('Почта', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    content = TextAreaField("Что вы хотите заказать?")
    picture = FileField('AddPicture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Отправить заказ')
