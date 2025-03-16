import sqlite3

def update_group_id():
    # Подключение к базе данных
    conn = sqlite3.connect('DataBaseImgTest.db')
    cursor = conn.cursor()

    # Обновление значений group_id
    cursor.execute("UPDATE telegram SET group_id = 1 WHERE id IN (1, 4, 6)")
    cursor.execute("UPDATE telegram SET group_id = 2 WHERE id IN (3, 7)")
    cursor.execute("UPDATE telegram SET group_id = 3 WHERE id IN (5, 9)")

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

if __name__ == '__main__':
    update_group_id()


