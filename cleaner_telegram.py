import sqlite3

def reset_vectors_and_processing():
    # Подключаемся к базе данных
    conn = sqlite3.connect('DataBaseImgTest.db')
    cursor = conn.cursor()

    # Обновляем все записи, зануляем image_vector и столбец processing
    cursor.execute('''
    UPDATE telegram
    SET image_vector = NULL, processing = 0;
    ''')

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

if __name__ == '__main__':
    reset_vectors_and_processing()
