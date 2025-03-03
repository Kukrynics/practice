from PIL import Image
import io
import numpy as np

def blob_to_image(media_blob):
    """
    Конвертирует BLOB-данные в изображение.
    :param media_blob: BLOB-данные из базы данных
    :return: Объект изображения (PIL.Image)
    """
    return Image.open(io.BytesIO(media_blob))

def preprocess_image(image):
    """
    Подготавливает изображение для подачи в нейронную сеть.
    :param image: Объект изображения (PIL.Image)
    :return: Изображение в формате numpy array (224x224x3)
    """
    image = image.resize((224, 224))  # Изменяем размер до 224x224
    image = np.array(image)           # Конвертируем в numpy array
    if image.shape[2] == 4:           # Если изображение с альфа-каналом, удаляем его
        image = image[:, :, :3]
    return image