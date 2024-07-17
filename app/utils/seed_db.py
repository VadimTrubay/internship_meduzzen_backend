import psycopg2
from faker import Faker
import hashlib
from app.conf.config import settings

# Загрузка переменных окружения из .env файлаКонфигурация подключения к базе данных PostgreSQL
DB_NAME = settings.DB_NAME
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT

# Количество фейковых записей для создания
NUM_FAKE_RECORDS = 54

# Инициализация генератора фейковых данных
fake = Faker()


# Функция для генерации хешированного пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Подключение к базе данных
try:
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    cursor = conn.cursor()
    print("Connected to the database successfully.")

    # Создание таблицы, если она не существует
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE,
        UNIQUE (email),
        UNIQUE (username)
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    print("Table created successfully.")

    # Генерация и вставка фейковых данных
    insert_query = """
    INSERT INTO users (id, email, username, password, is_admin) VALUES (%s, %s, %s, %s, %s);
    """
    for _ in range(NUM_FAKE_RECORDS):
        id = fake.uuid4()
        email = fake.email()
        username = fake.user_name()
        password = hash_password(fake.password())
        is_admin = fake.boolean()
        cursor.execute(insert_query, (id, email, username, password, is_admin))

    conn.commit()
    print(f"{NUM_FAKE_RECORDS} fake records inserted successfully.")

except Exception as e:
    print(f"Error: {e}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    print("Database connection closed.")
