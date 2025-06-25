from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import EqualTo, Length, DataRequired


# Форма для профиля
class ProfileForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(message="Имя обязательно")])
    password = PasswordField('Новый пароль', validators=[
        Length(min=6, message='Пароль должен быть не менее 6 символов')
    ])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        EqualTo('password', message='Пароли должны совпадать')
    ])
    submit = SubmitField('Сохранить')





