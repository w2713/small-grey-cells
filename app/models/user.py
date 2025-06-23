from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from pymongo.errors import PyMongoError
from datetime import datetime


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
            'password_hash': password_hash,
            'created_at': datetime.utcnow()  # Добавляем дату создания
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



def update_user(db, user_id, update_data):
    try:
        result = db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Update user error: {str(e)}")
        return False



@property
def created_at(self):
    # Добавьте это поле в вашу MongoDB коллекцию users
    return self.user_data.get('created_at')