import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input

# tf.get_logger().setLevel('ERROR')

# Загрузка модели ResNet50
model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def extract_image_vector(img_path):
    """
    Извлекает вектор признаков изображения с помощью модели ResNet50.
    """
    # Загружаем изображение
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    # Извлекаем вектор признаков
    vector = model.predict(img_array)
    return vector.flatten()

def process_images_for_group(group_id):
    """
    Обрабатывает все изображения для группы с указанным group_id,
    извлекает их признаки и сохраняет в базе данных.
    """
    # Подключаемся к базе данных
    import sqlite3
    conn = sqlite3.connect('DataBaseImgTest.db')
    cursor = conn.cursor()

    # Извлекаем все изображения для группы из таблицы telegram
    cursor.execute("SELECT id, media FROM telegram WHERE group_id = ?", (group_id,))
    rows = cursor.fetchall()

    for row in rows:
        img_ids = row[0]
        media = row[1].split(", ")

        for img_path in media:
            vector = extract_image_vector(img_path)

            # Преобразуем вектор в строку (например, через base64 или просто как список строк)
            vector_str = ",".join(map(str, vector))

            # Сохраняем вектор в таблицу telegram
            cursor.execute('''
            UPDATE telegram SET image_vector = ?, processing = 1 WHERE id = ?
            ''', (vector_str, img_ids))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Пример вызова для группы с group_id = 1
    process_images_for_group(1)
