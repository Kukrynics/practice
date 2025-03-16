import sqlite3

def view_db():
    # Подключение к базе данных
    conn = sqlite3.connect('DataBaseImgTest.db')
    cursor = conn.cursor()

    # Вывод таблицы telegram
    cursor.execute('SELECT id, media, processing, group_id, image_vector FROM telegram')
    telegram_rows = cursor.fetchall()

    print("Table: telegram")
    if telegram_rows:
        for row in telegram_rows:
            print(row)
    else:
        print("id | media | processing | group_id")

    print("\nTable: best_img")
    cursor.execute('SELECT * FROM best_img')
    group_rows = cursor.fetchall()

    if group_rows:
        for row in group_rows:
            print(row)
    else:
        print("ip | group_id | media")

    conn.close()

if __name__ == '__main__':
    view_db()
