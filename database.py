import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")  # DB_HOST = localhost
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")

try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(  # mysql
        pool_name="app",
        pool_size=5,  # duplicates
        host=DB_HOST,  # -h
        user=DB_USER,  # -u
        password=DB_PASSWORD, # -p
        database=DB_NAME,  # USE DB_NAME
    )
    print("Database connection pool created successfully.")
except mysql.connector.Error as err:
    print(f"Error creating connection pool: {err}")


# @contextmanager
def get_db_connection():
    connection = None
    try:
        connection = db_pool.get_connection()
        yield connection
    # except mysql.connector.Error as err:
    #     print(f"Database Error: {err}")
    #     if connection:
    #         connection.rollback()
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection returned to pool.")