def create_collections(db):
    collections = ['users', 'notes', 'categories', 'tags']

    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)

    # Индексы для пользователей
    db.users.create_index('email', unique=True)

    # Индексы для заметок
    db.notes.create_index('title')
    db.notes.create_index('tags')

    # Пример начальных категорий
    if db.categories.count_documents({}) == 0:
        default_categories = ['Работа', 'Личное', 'Учеба', 'Идеи']
        for cat in default_categories:
            db.categories.insert_one({'name': cat})

    print("Database initialized successfully")