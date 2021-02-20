import sqlite3 as sql
from sqlite3 import Error


def create_connection(path):
    connection = None
    try:
        connection = sql.connect(path)
        print('Successfully connected to database.')
    except Error as e:
        print(f"The error '{e}' occurred.")

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print('Query executed successfully')
    except Error as e:
        print(f"The error '{e}' occurred.")


def setup(connection):
    create_chair_reference_table = """
    CREATE TABLE IF NOT EXISTS chairs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL,
        created DATETIME NOT NULL
        );
    """

    execute_query(connection, create_chair_reference_table)


def add_chair(connection, file_path, datetime_now):
    add_chair_query = f"""
    INSERT INTO chairs (file_path, created)
    VALUES ({file_path}, {datetime_now})
    );
    """

    execute_query(connection, add_chair_query)
