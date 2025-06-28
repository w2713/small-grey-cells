from bson import ObjectId
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, jsonify, request
from flask_login import login_required, current_user, login_user
from werkzeug.security import generate_password_hash

from ..models import User
from .forms import ProfileForm, NoteForm
from ..models.note import Note

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
    form = ProfileForm(obj=current_user)  # Автозаполнение формы
    if form.validate_on_submit():
        try:
            update_data = {'name': form.name.data}
            if form.password.data:
                if len(form.password.data) < 6:
                    flash('Пароль должен быть не менее 6 символов', 'danger')
                    return render_template('main/profile.html', form=form)

                update_data['password_hash'] = generate_password_hash(form.password.data)

            result = current_app.db.users.update_one(
                {'_id': ObjectId(current_user.id)},
                {'$set': update_data}
            )

            if result.modified_count > 0:
                # Обновляем данные в текущей сессии
                updated_user = current_app.db.users.find_one({'_id': ObjectId(current_user.id)})
                login_user(User(updated_user), remember=True)
                flash('Профиль успешно обновлён!', 'success')
            else:
                flash('Данные не были изменены', 'info')

            return redirect(url_for('main.profile_view'))

        except Exception as e:
            current_app.logger.error(f"Ошибка обновления профиля: {str(e)}")
            flash('Ошибка при обновлении профиля', 'danger')

    return render_template('main/profile.html', form=form)


@bp.route('/notes', methods=['GET'])
@login_required
def notes():
    notes = Note.get_user_notes(current_app.db, current_user.id)
    all_tags = current_app.db.tags.distinct('name')
    return render_template('main/notes.html', notes=notes, all_tags=all_tags)


@bp.route('/note/create', methods=['GET', 'POST'])
@login_required
def create_note():
    form = NoteForm()
    # Заполняем теги из базы
    form.tags.choices = [(tag, tag) for tag in current_app.db.tags.distinct('name')]
    if form.validate_on_submit():
        new_tags = [t.strip() for t in form.new_tags.data.split(',') if t.strip()]

        existing_tags = form.tags.data
        # Добавляем новые теги в базу
        for tag in new_tags:
            current_app.db.tags.update_one(
                {'name': tag},
                {'$set': {'name': tag}},
                upsert=True
            )

        Note.create(
            db=current_app.db,
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id,
            tags=list(set(existing_tags + new_tags)),
            category=form.category.data
        )
        flash('Заметка создана успешно!', 'success')
        return redirect(url_for('main.notes'))

    return render_template('main/note_form.html', form=form, title='Создать заметку')


@bp.route('/note/<note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.get_by_id(current_app.db, note_id)

    if not note or str(note['user_id']) != current_user.id:
        flash('Заметка не найдена', 'danger')
        return redirect(url_for('main.notes'))

    form = NoteForm(obj=note)
    form.tags.choices = [(tag, tag) for tag in current_app.db.tags.distinct('name')]

    if form.validate_on_submit():
        # new_tags = [tag for tag in form.tags.data if tag not in form.tags.choices]
        new_tags = [t.strip() for t in form.new_tags.data.split(',') if t.strip()]

        existing_tags = form.tags.data

        # Добавляем новые теги в базу
        for tag in new_tags:
            current_app.db.tags.update_one(
                {'name': tag},
                {'$set': {'name': tag}},
                upsert=True
            )

        Note.update(
            db=current_app.db,
            note_id=note_id,
            title=form.title.data,
            content=form.content.data,
            # tags=form.tags.data,
            tags=list(set(existing_tags + new_tags)),
            category=form.category.data
        )
        flash('Заметка обновлена успешно!', 'success')
        return redirect(url_for('main.notes'))

    return render_template('main/note_form.html', form=form, title='Редактировать заметку')


@bp.route('/note/<note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    try:
        note = Note.get_by_id(current_app.db, note_id)

        # Проверка прав доступа
        if not note or str(note['user_id']) != current_user.id:
            return jsonify({'success': False, 'message': 'Not found'}), 404

        # Удаляем заметку
        result = current_app.db.notes.delete_one({'_id': ObjectId(note_id)})
        if result.deleted_count > 0:
            return jsonify({'success': True})
        return jsonify({'success': False}), 500
    except Exception as e:
        current_app.logger.error(f"Delete note error: {str(e)}")
        return jsonify({'success': False}), 500


@bp.route('/note/<note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    try:
        data = request.get_json()
        note = Note.get_by_id(current_app.db, note_id)

        # Проверка прав доступа
        if not note or str(note['user_id']) != current_user.id:
            return jsonify({'success': False, 'message': 'Not found'}), 404

        # Обновляем теги: добавляем новые, если они есть
        new_tags = data.get('new_tags', [])
        if new_tags:
            new_tags = [t.strip() for t in new_tags.split(',') if t.strip()]
            tags_to_save = list(set(data.get('tags') + new_tags))
        else:
            tags_to_save = data.get('tags')

        existing_tags = current_app.db.tags.distinct('name')

        for tag in new_tags:
            if tag not in existing_tags:
                current_app.db.tags.update_one(
                    {'name': tag},
                    {'$set': {'name': tag}},
                    upsert=True
                )
        # Обновляем заметку
        success = Note.update(
            db=current_app.db,
            note_id=note_id,
            title=data.get('title'),
            content=data.get('content'),
            tags=tags_to_save,
            category=data.get('category')
        )

        if success:
            return jsonify({'success': True})
        return jsonify({'success': False}), 500

    except Exception as e:
        current_app.logger.error(f"Edit note error: {str(e)}")
        return jsonify({'success': False}), 500


@bp.route('/api/note/<note_id>', methods=['GET'])
@login_required
def get_note(note_id):
    note = Note.get_by_id(current_app.db, note_id)

    # Проверка прав доступа
    if not note or str(note['user_id']) != current_user.id:
        return jsonify({'error': 'Not found'}), 404

    # Преобразуем ObjectId и datetime для JSON
    note['_id'] = str(note['_id'])
    note['user_id'] = str(note['user_id'])
    note['created_at'] = note['created_at'].isoformat() if note.get('created_at') else None
    note['updated_at'] = note['updated_at'].isoformat() if note.get('updated_at') else None

    return jsonify(note)