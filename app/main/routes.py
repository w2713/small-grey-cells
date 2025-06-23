from flask import Blueprint, render_template, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from pymongo.errors import PyMongoError

from main.forms import ProfileForm

bp = Blueprint('main', __name__)


@bp.route('/')
def home():
    try:
        # Проверяем доступность БД
        if current_app.db is None:
            return render_template('errors/db_connection.html'), 500

        # Пример последних заметок
        notes = list(current_app.db.notes.find().sort('created_at', -1).limit(5))
        return render_template('main/home.html', notes=notes)

    except PyMongoError as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return render_template('errors/db_connection.html'), 500


@bp.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html')



@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()

    if form.validate_on_submit():
        try:
            update_data = {'name': form.name.data}

            # Обновляем пароль, если он указан
            if form.password.data:
                from werkzeug.security import generate_password_hash
                update_data['password_hash'] = generate_password_hash(form.password.data)

            current_app.db.users.update_one(
                {'_id': current_user.id},
                {'$set': update_data}
            )
            flash('Профиль успешно обновлен', 'success')
            return redirect(url_for('main.profile'))

        except Exception as e:
            current_app.logger.error(f"Error updating profile: {str(e)}")
            flash('Ошибка при обновлении профиля', 'danger')

    # Заполняем форму текущими данными
    form.name.data = current_user.name
    return render_template('main/profile.html', form=form)
