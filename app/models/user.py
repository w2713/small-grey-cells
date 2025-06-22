from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.name = user_data.get('name', '')
        self.email = user_data['email']
        self.password_hash = user_data['password_hash']

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_email(email):
        user_data = db.users.find_one({'email': email})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def create(name, email, password):
        password_hash = generate_password_hash(password)
        result = db.users.insert_one({
            'name': name,
            'email': email,
            'password_hash': password_hash
        })
        return str(result.inserted_id)