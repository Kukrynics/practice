# README.md

# Система парсинга новостей из RSS-лент и Telegram-каналов

## Описание проекта

Данный проект представляет собой систему для автоматического парсинга новостей из RSS-лент и Telegram-каналов. Система позволяет собирать актуальные новости, хранить их в базе данных PostgreSQL и медиа-контент в облачном хранилище MEGA. Парсер запускается автоматически с интервалом в 5-10 часов, что обеспечивает актуальность собранной информации.

## Функциональные возможности

- Парсинг новостей из RSS-лент.
- Парсинг сообщений из Telegram-каналов.
- Хранение новостей и комментариев в базе данных PostgreSQL.
- Хранение медиа-контента (фото и видео) в облачном хранилище MEGA.
- Периодический запуск парсера для обновления данных.
- Возможность фильтрации и извлечения новостей из базы данных.

## Установка

### Требования

- Python 3.7 или выше
- PostgreSQL
- MEGA API
- Библиотеки Python:
  - `feedparser`
  - `telethon`
  - `psycopg2`
  - `mega`
  - `schedule`
  - `logging`

### Установка зависимостей

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/yourusername/news-parser.git
   cd news-parser
   ```

2. Установите необходимые библиотеки:

   ```bash
   pip install -r requirements.txt
   ```

### Настройка базы данных

1. Установите PostgreSQL и создайте базу данных:

   ```bash
   sudo -u postgres psql
   CREATE DATABASE news_db;
   CREATE USER news_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE news_db TO news_user;
   ```

2. Создайте таблицы в базе данных:

   ```sql
   CREATE TABLE news (
       id SERIAL PRIMARY KEY,
       title VARCHAR(255) NOT NULL,
       content TEXT,
       source VARCHAR(50) NOT NULL,
       published_at TIMESTAMP NOT NULL,
       url VARCHAR(255) UNIQUE NOT NULL,
       media_url VARCHAR(255),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   CREATE TABLE comments (
       id SERIAL PRIMARY KEY,
       news_id INT REFERENCES news(id),
       user VARCHAR(100),
       content TEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

### Настройка MEGA

1. Зарегистрируйтесь на [MEGA](https://mega.nz/) и получите учетные данные для API.
2. Вставьте свои учетные данные в коде, где используется библиотека `mega`.

### Настройка Telegram

1. Зарегистрируйтесь на [Telegram](https://telegram.org/) и получите API ID и API Hash.
2. Вставьте свои учетные данные в коде, где используется библиотека `Telethon`.

## Запуск парсера

Для запуска парсера выполните команду:

```bash
python src/main.py
```

Парсер будет автоматически запускаться с интервалом в 5-10 часов.

## Использование

После запуска парсера вы можете выполнять SQL-запросы к базе данных PostgreSQL для извлечения новостей и комментариев. Пример запроса для получения всех новостей:

```sql
SELECT * FROM news ORDER BY published_at DESC;
```

## Тестирование

Для запуска тестов используйте команду:

```bash
python -m unittest discover -s tests
```

## Логирование

Все действия парсера записываются в файл `parser.log`. Вы можете просмотреть этот файл для отслеживания работы системы и выявления возможных ошибок.

## Перспективы развития

В будущем планируется:

- Добавление поддержки других источников новостей.
- Улучшение алгоритмов фильтрации и анализа данных.
- Разработка пользовательского интерфейса для удобного доступа к новостям.
- Создание мобильного приложения для доступа к собранным новостям.

## Лицензия

Этот проект лицензирован под MIT License. См. файл [LICENSE](LICENSE) для получения дополнительной информации.

## Контакты

Если у вас есть вопросы или предложения, вы можете связаться со мной по электронной почте: your_email@example.com.

---

Спасибо за интерес к проекту! Надеюсь, он будет полезен для вас.
