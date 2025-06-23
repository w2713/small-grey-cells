from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import EqualTo, Length


# Форма для профиля
class ProfileForm(FlaskForm):
    name = StringField('Имя')
    password = PasswordField('Новый пароль', validators=[   Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль',
                                     validators=[EqualTo('password', message='Пароли должны совпадать')])
    submit = SubmitField('Сохранить')





