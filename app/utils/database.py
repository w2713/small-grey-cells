from pymongo.errors import PyMongoError


def create_collections(db):
    if db is None:
        raise ConnectionError("No database connection")

    collections = ['users', 'notes', 'categories', 'tags']

    try:
        existing_collections = db.list_collection_names()

        for collection in collections:
            if collection not in existing_collections:
                db.create_collection(collection)

        # Индексы для пользователей
        if 'email' not in db.users.index_information():
            db.users.create_index('email', unique=True)

        # Индексы для заметок
        if 'title' not in db.notes.index_information():
            db.notes.create_index('title')

        if 'tags' not in db.notes.index_information():
            db.notes.create_index('tags')

        # Пример начальных категорий
        if db.categories.count_documents({}) == 0:
            default_categories = ['Работа', 'Личное', 'Учеба', 'Идеи']
            for cat in default_categories:
                db.categories.insert_one({'name': cat})

        if db.tags.count_documents({}) == 0:
            default_tags = ['Работа', 'Личное', 'Мысли', 'Идеи']
            for ta in default_tags:
                db.tags.insert_one({'name': ta})
        print("Database initialized successfully")

    except PyMongoError as e:
        print(f"Database initialization error: {str(e)}")
        raise