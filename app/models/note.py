from datetime import datetime
from pymongo.errors import PyMongoError


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