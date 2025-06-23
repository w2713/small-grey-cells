from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user
from ..models.user import get_user_by_email, create_user
from .forms import RegistrationForm, LoginForm

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = get_user_by_email(current_app.db, form.email.data)
        if user:
            flash('Email уже зарегистрирован', 'danger')
        else:
            create_user(
                current_app.db,
                name=form.name.data,
                email=form.email.data,
                password=form.password.data
            )
            flash('Регистрация прошла успешно!', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_email(current_app.db, form.email.data)
        if user and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.home'))
        flash('Неверный email или пароль', 'danger')

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))