import sqlite3

def reset_best_img_table():
    # Подключаемся к базе данных
    conn = sqlite3.connect('DataBaseImgTest.db')
    cursor = conn.cursor()

    # Удаляем таблицу best_img, если она существует
    cursor.execute('''
    DROP TABLE IF EXISTS best_img;
    ''')

    # Создаем новую таблицу best_img
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS best_img (
        ip TEXT,
        group_id INTEGER,
        media TEXT
    );
    ''')

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

if __name__ == '__main__':
    reset_best_img_table()
