from bson import ObjectId
from flask import current_app


def get_existing_tags(user_id):

    pipeline = [
        {'$match': {'user_id': ObjectId(user_id)}},
        {'$unwind': '$tags'},
        {'$group': {'_id': '$tags', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    return [tag['_id'] for tag in current_app.db.notes.aggregate(pipeline)]