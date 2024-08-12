import psycopg2
from faker import Faker
import hashlib

from loguru import logger

from app.conf.config import settings

DB_NAME = settings.DB_NAME
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT

NUM_FAKE_RECORDS = 54

fake = Faker()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


try:
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    cursor = conn.cursor()
    logger.info("Connected to the database successfully.")
    print("Connected to the database successfully.")

    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        UNIQUE (email),
        UNIQUE (username)
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    logger.info("Table created successfully.")
    print("Table created successfully.")

    insert_query = """
    INSERT INTO users (id, email, username, password) VALUES (%s, %s, %s, %s, %s);
    """
    for _ in range(NUM_FAKE_RECORDS):
        id = fake.uuid4()
        email = fake.email()
        username = fake.user_name()
        password = hash_password(fake.password())
        cursor.execute(insert_query, (id, email, username, password))

    conn.commit()
    logger.info(f"{NUM_FAKE_RECORDS} fake records inserted successfully.")
    print(f"{NUM_FAKE_RECORDS} fake records inserted successfully.")

except Exception as e:
    print(f"Error: {e}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    logger.info("Database connection closed.")
    print("Database connection closed.")
