import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
import numpy as np

# Загружаем предобученную модель ResNet50 без верхних слоев
model = ResNet50(weights="imagenet", include_top=False, pooling="avg")

def extract_features(image):
    """
    Извлекает признаки из изображения с помощью ResNet50.
    :param image: Изображение в формате numpy array (224x224x3)
    :return: Вектор признаков (массив numpy)
    """
    image = preprocess_input(image)  # Предобработка изображения для ResNet50
    image = np.expand_dims(image, axis=0)  # Добавляем размерность батча
    features = model.predict(image)  # Извлекаем признаки
    return features.flatten()  # Преобразуем в одномерный массив