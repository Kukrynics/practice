import sqlite3

def create_database():
    # Подключение к базе данных (если файл не существует, он будет создан)
    conn = sqlite3.connect('DataBaseImgTest.db')
    cursor = conn.cursor()

    # Создание таблицы telegram
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS telegram (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        text TEXT,
        media TEXT,
        group_id INTEGER,
        processing BOOLEAN,
        image_vector TEXT
    );
    ''')

    # Создание таблицы group
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS best_img (
        ip TEXT,
        group_id INTEGER,
        media TEXT
    );
    ''')

    # Сохранение изменений и закрытие соединения
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
