from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField, BooleanField
from wtforms.validators import DataRequired

class UploadForm(FlaskForm):
    name = StringField('Название')
    description = TextAreaField('Описание')
    file = FileField('Картинка', validators=[DataRequired()])
    is_private = BooleanField('Приватный пост')
    submit = SubmitField('Загрузить')