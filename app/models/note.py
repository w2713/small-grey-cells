from datetime import datetime

class Note:
    @staticmethod
    def create(title, content, user_id, tags=[], category=None):
        return {
            'title': title,
            'content': content,
            'user_id': user_id,
            'tags': tags,
            'category': category,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }