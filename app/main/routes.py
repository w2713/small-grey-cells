from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .. import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    # Пример последних заметок (реализация будет в следующей части)
    notes = list(db.notes.find().sort('created_at', -1).limit(5))
    return render_template('main/home.html', notes=notes)

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Форма редактирования профиля (реализация в шаблоне)
    return render_template('main/profile.html')