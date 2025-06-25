from flask import Flask, render_template
from flask_login import LoginManager
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import Config
import logging
from flask_wtf.csrf import generate_csrf, CSRFProtect

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Настройка логгера
    logging.basicConfig(level=logging.INFO)

    # Инициализация базы данных
    init_database(app)

    csrf = CSRFProtect(app)
    # csrf.init_app(app)
    @app.context_processor
    def inject_csrf_token():
        return dict(generate_csrf=generate_csrf)

    login_manager.init_app(app)

    # Регистрация блюпринтов
    from .main.routes import bp as main_bp
    from .auth.routes import bp as auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Регистрируем загрузчик пользователей
    from .models.user import load_user

    @login_manager.user_loader
    def user_loader(user_id):
        return load_user(app, user_id)

    # Обработчик ошибки подключения к БД
    @app.errorhandler(500)
    def handle_db_error(e):
        if app.db is None:
            return render_template('errors/db_connection.html'), 500
        return e

    return app


def init_database(app):
    """Инициализация подключения к базе данных"""
    try:
        client = MongoClient(
            app.config['MONGO_URI'],
            serverSelectionTimeoutMS=5000
        )
        client.server_info()
        app.db = client.get_database()
        app.logger.info("Successfully connected to MongoDB")

        # Инициализация коллекций
        from .utils.database import create_collections
        create_collections(app.db)

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        app.logger.error(f"MongoDB connection error: {str(e)}")
        app.db = None