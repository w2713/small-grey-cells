from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from pymongo.errors import PyMongoError


class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.name = user_data.get('name', '')
        self.email = user_data['email']
        self.password_hash = user_data['password_hash']

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


def get_user_by_email(db, email):
    if db is None:
        raise ConnectionError("No database connection")

    try:
        user_data = db.users.find_one({'email': email})
        if user_data:
            return User(user_data)
        return None
    except PyMongoError as e:
        print(f"Database error: {str(e)}")
        return None


def create_user(db, name, email, password):
    if db is None:
        raise ConnectionError("No database connection")

    password_hash = generate_password_hash(password)
    try:
        result = db.users.insert_one({
            'name': name,
            'email': email,
            'password_hash': password_hash
        })
        return str(result.inserted_id)
    except PyMongoError as e:
        print(f"User creation error: {str(e)}")
        return None


def load_user(app, user_id):
    if app.db is None:
        return None

    try:
        user_data = app.db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None
    except PyMongoError:
        return None