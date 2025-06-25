from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import EqualTo, Length, DataRequired


# Форма для профиля
class ProfileForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Новый пароль (оставьте пустым, чтобы не менять)')
    confirm_password = PasswordField('Подтвердите новый пароль',
                                   validators=[EqualTo('password', message='Пароли должны совпадать')])
    submit = SubmitField('Сохранить')





