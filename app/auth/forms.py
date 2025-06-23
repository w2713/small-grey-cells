from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegistrationForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Введите корректный email адрес')
    ])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль',
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')



