import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
import numpy as np

# Загрузка модели ResNet50
model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def extract_image_vector(img_path):
    """
    Извлекает вектор признаков изображения с помощью модели ResNet50
    """
    # Загружаем изображение
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    # Извлекаем вектор признаков
    vector = model.predict(img_array)
    return vector.flatten()

if __name__ == '__main__':
    # Пример использования
    img_path = 'path_to_image.jpg'
    vector = extract_image_vector(img_path)
    print(vector)
