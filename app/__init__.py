from flask import Flask
from flask_login import LoginManager
from pymongo import MongoClient
from config import Config

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Инициализация MongoDB
    client = MongoClient(app.config['MONGO_URI'])
    app.db = client.get_database()

    # Создание коллекций при необходимости
    from .utils.database import create_collections
    create_collections(app.db)

    login_manager.init_app(app)

    # Регистрация блюпринтов
    from .main.routes import main_bp
    from .auth.routes import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app