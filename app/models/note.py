from bson import ObjectId
from datetime import datetime
from pymongo.errors import PyMongoError

class Note:
    @staticmethod
    def create(db, title, content, user_id, tags=[], category=None):
        try:
            note_data = {
                'title': title,
                'content': content,
                'user_id': ObjectId(user_id),
                'tags': tags,
                'category': category,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            result = db.notes.insert_one(note_data)
            return str(result.inserted_id)
        except PyMongoError as e:
            print(f"Note creation error: {str(e)}")
            return None

    @staticmethod
    def update(db, note_id, title, content, tags, category):
        try:
            result = db.notes.update_one(
                {'_id': ObjectId(note_id)},
                {'$set': {
                    'title': title,
                    'content': content,
                    'tags': tags,
                    'category': category,
                    'updated_at': datetime.utcnow()
                }}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            print(f"Note update error: {str(e)}")
            return False

    @staticmethod
    def get_by_id(db, note_id):
        try:
            return db.notes.find_one({'_id': ObjectId(note_id)})
        except PyMongoError:
            return None

    @staticmethod
    def get_user_notes(db, user_id):
        try:
            return list(db.notes.find({'user_id': ObjectId(user_id)}).sort('updated_at', -1))
        except PyMongoError:
            return []

def create_note(db, title, content, user_id, tags=[], category=None):
    if db is None:
        raise ConnectionError("No database connection")

    try:
        note_data = {
            'title': title,
            'content': content,
            'user_id': user_id,
            'tags': tags,
            'category': category,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        db.notes.insert_one(note_data)
        return note_data
    except PyMongoError as e:
        print(f"Note creation error: {str(e)}")
        return None

def get_existing_tags(db, user_id):
    pipeline = [
        {'$match': {'user_id': ObjectId(user_id)}},
        {'$unwind': '$tags'},
        {'$group': {'_id': '$tags', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    return [tag['_id'] for tag in db.notes.aggregate(pipeline)]