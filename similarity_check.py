from sklearn.metrics.pairwise import cosine_similarity

def is_similar(feature1, feature2, threshold):
    """
    Проверяет, похожи ли два вектора признаков.
    :param feature1: Вектор признаков первого изображения
    :param feature2: Вектор признаков второго изображения
    :param threshold: Порог схожести
    :return: True, если изображения похожи, иначе False
    """
    similarity = cosine_similarity([feature1], [feature2])[0][0]
    return similarity > threshold