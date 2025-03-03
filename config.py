# Конфигурация базы данных
DATABASE_CONFIG = {
    'dbname': 'your_database_name',  # Имя базы данных
    'user': 'your_username',         # Имя пользователя
    'password': 'your_password',     # Пароль
    'host': 'localhost',             # Хост (обычно localhost)
    'port': 5432                     # Порт (по умолчанию 5432 для PostgreSQL)
}

# Порог схожести изображений (косинусное расстояние)
SIMILARITY_THRESHOLD = 0.2

# Размер батча для обработки изображений
BATCH_SIZE = 32

# Путь для сохранения логов (если нужно)
LOG_FILE = "app.log"