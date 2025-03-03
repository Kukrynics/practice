from database import fetch_images, update_marker, save_feature_vector
from image_processing import blob_to_image, preprocess_image
from feature_extraction import extract_features
from similarity_check import is_similar
from config import SIMILARITY_THRESHOLD


def main():
    """
    Основная функция программы.
    """
    # Извлекаем изображения из базы данных
    images = fetch_images()

    # Словарь для хранения обработанных признаков
    processed_features = {}

    for post_id, media_blob in images:
        # Конвертируем BLOB в изображение
        image = blob_to_image(media_blob)

        # Предобрабатываем изображение
        processed_image = preprocess_image(image)

        # Извлекаем признаки
        features = extract_features(processed_image)

        # Проверяем, есть ли похожие изображения
        is_copy = False
        for existing_id, existing_features in processed_features.items():
            if is_similar(features, existing_features, SIMILARITY_THRESHOLD):
                is_copy = True
                break

        # Обновляем маркер в базе данных
        if is_copy:
            update_marker(post_id, "Copy")
        else:
            update_marker(post_id, "True")
            processed_features[post_id] = features

        # Сохраняем вектор признаков в базу данных
        save_feature_vector(post_id, features)

if __name__ == "__main__":
    main()