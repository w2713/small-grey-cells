from bson import ObjectId
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user, login_user
from werkzeug.security import generate_password_hash

from models.user import User
from .forms import ProfileForm

# Создаем Blueprint с уникальным именем
bp = Blueprint('main', __name__, template_folder='templates/main')

@bp.route('/')
def home():
    try:
        if current_app.db is None:
            return render_template('errors/db_connection.html'), 500

        notes = list(current_app.db.notes.find().sort('created_at', -1).limit(5))
        return render_template('main/home.html', notes=notes)

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return render_template('errors/db_connection.html'), 500


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_view():
    form = ProfileForm()

    # Обработка GET-запроса или невалидной формы
    if not form.validate_on_submit():
        form.name.data = current_user.name  # Заполняем форму текущими данными
        return render_template('main/profile.html', form=form)

    # Обработка POST-запроса с валидными данными
    try:
        update_data = {'name': form.name.data}

        if form.password.data:
            if len(form.password.data) < 6:
                flash('Пароль должен содержать минимум 6 символов', 'danger')
                return render_template('main/profile.html', form=form)
            update_data['password_hash'] = generate_password_hash(form.password.data)

        # Обновляем данные в базе
        result = current_app.db.users.update_one(
            {'_id': ObjectId(current_user.id)},
            {'$set': update_data}
        )

        if result.modified_count == 0:
            flash('Данные не были изменены', 'info')
            return redirect(url_for('main.profile_view'))

        # Обновляем сессию пользователя
        updated_user = current_app.db.users.find_one({'_id': ObjectId(current_user.id)})
        login_user(User(updated_user), remember=True)

        flash('Профиль успешно обновлен', 'success')
        return redirect(url_for('main.profile_view'))

    except Exception as e:
        current_app.logger.error(f"Ошибка обновления профиля: {str(e)}")
        flash('Произошла ошибка при обновлении профиля', 'danger')
        return render_template('main/profile.html', form=form)