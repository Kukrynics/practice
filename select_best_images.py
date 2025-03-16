import sqlite3
import numpy as np
import imagehash
from PIL import Image
import os

def calculate_image_hash(image_path):
    """
    Вычисляет перцептуальный хеш изображения.
    """
    img = Image.open(image_path)
    return imagehash.phash(img)

def compare_images_by_hash(hash1, hash2, threshold=3):  # Уменьшаем порог для большего различия
    """
    Сравнивает два изображения по их перцептуальным хешам.
    Если разница в хешах меньше порога, изображения считаются похожими.
    """
    return hash1 - hash2 < threshold

def compare_image_vectors(vector1, vector2):
    """
    Сравнивает два вектора изображений (например, с помощью евклидова расстояния).
    Чем меньше расстояние, тем более похожи изображения.
    """
    return np.linalg.norm(vector1 - vector2)

def select_best_images_for_group():
    """
    Выбирает лучшие изображения для каждой группы на основе векторов признаков и хешей.
    """
    # Подключаемся к базе данных
    conn = sqlite3.connect('DataBaseImgTest.db')
    cursor = conn.cursor()

    # Извлекаем все изображения для всех групп из таблицы telegram
    cursor.execute("SELECT group_id, media, image_vector FROM telegram WHERE group_id IS NOT NULL AND image_vector IS NOT NULL")
    rows = cursor.fetchall()

    if len(rows) == 0:
        print("Нет данных для обработки.")
        conn.close()
        return

    all_vectors = {}
    image_paths = {}
    initial_image_count = {}  # Словарь для хранения количества картинок в постах внутри каждой группы

    # Для каждой записи в таблице
    for row in rows:
        group_id = row[0]
        media = row[1].split(", ")  # Разделяем на список путей к картинкам
        if group_id not in initial_image_count:
            initial_image_count[group_id] = []
        initial_image_count[group_id].append(len(media))  # Сохраняем количество картинок в постах по группе

        vector = None

        # Проверяем, есть ли значение в image_vector
        if row[2]:  # Если image_vector не пустой
            vector = np.array(list(map(float, row[2].split(","))))

        # Если вектор существует, добавляем его в список
        if vector is not None:
            if group_id not in all_vectors:
                all_vectors[group_id] = []
                image_paths[group_id] = []
            for img_path in media:
                all_vectors[group_id].append(vector)
                image_paths[group_id].append(img_path)

    # Обработка картинок по группам
    for group_id in all_vectors:
        # Вычисляем среднее количество картинок для группы
        avg_images = sum(initial_image_count[group_id]) // len(initial_image_count[group_id])

        print(f"Для группы {group_id}: среднее количество картинок на пост = {avg_images}")

        # Фильтруем дубликаты и обрезанные картинки
        selected_images = list(set(image_paths[group_id]))  # Убираем дубликаты

        hashes = []
        final_images = []

        for img_path in selected_images:
            if os.path.exists(img_path):  # Проверяем, существует ли изображение
                print(f"Изображение найдено: {img_path}")

                # Вычисляем хеш для изображения
                img_hash = calculate_image_hash(img_path)
                is_duplicate = False

                # Сравниваем с уже добавленными изображениями на основе хешей
                for selected_img in final_images:
                    existing_img_hash = hashes[final_images.index(selected_img)]
                    if compare_images_by_hash(existing_img_hash, img_hash):  # Используем более строгий порог
                        is_duplicate = True
                        break

                # Если изображения не похожи, добавляем в итоговый список
                if not is_duplicate:
                    final_images.append(img_path)
                    hashes.append(img_hash)

        final_images = final_images[:avg_images]  # Ограничиваем количество изображений

        print(f"Выбрано {len(final_images)} изображений для группы {group_id}.")

        # Запись лучших картинок в таблицу best_img
        cursor.execute('''
        DELETE FROM best_img WHERE group_id = ?
        ''', (group_id,))

        # Вставляем одну запись с выбранными изображениями
        cursor.execute('''
        INSERT INTO best_img (group_id, media) VALUES (?, ?)
        ''', (group_id, ", ".join(final_images)))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    select_best_images_for_group()
