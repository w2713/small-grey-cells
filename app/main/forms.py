from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

# Форма для профиля
class ProfileForm(FlaskForm):
    name = StringField('Имя')
    password = PasswordField('Новый пароль')
    confirm_password = PasswordField('Подтвердите пароль',
                                     validators=[EqualTo('password', message='Пароли должны совпадать')])
    submit = SubmitField('Сохранить')





