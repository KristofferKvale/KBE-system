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


def execute_query(connection, query, get_id=False, fetch_all=False):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print(f'Query: {query} executed successfully')
        if get_id:
            return True, cursor.lastrowid
        if fetch_all:
            return True, cursor.fetchall()
        return True
    except Error as e:
        print(f"The error '{e}' occurred.")
        return False


def setup(connection):
    create_chair_reference_table = """
    CREATE TABLE IF NOT EXISTS chairs (
        chair_id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL,
        created DATE NOT NULL,
        sitting_height INTEGER DEFAULT 75,
        angle INTEGER DEFAULT 15
        );
    """
    create_customer_table = """
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        hashed_password TEXT NOT NULL
        );
    """

    create_WIP_table = """
    CREATE TABLE IF NOT EXISTS WIPs (
        WIP_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id int NOT NULL,
        chair_id int NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (chair_id) REFERENCES chairs(chair_id)
        );
    """

    create_order_table = """
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id int NOT NULL,
        chair_id int NOT NULL,
        count int NOT NULL,
        status text NOT NULL DEFAULT 'OPENED',
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (chair_id) REFERENCES chairs(chair_id)
        );
    """

    execute_query(connection, create_chair_reference_table, False)
    execute_query(connection, create_customer_table, False)
    execute_query(connection, create_WIP_table, False)
    execute_query(connection, create_order_table, False)


def add_chair(connection, file_path, datetime_now):
    add_chair_query = f"""
    INSERT INTO chairs (file_path, created)
    VALUES ('{file_path}', '{datetime_now}')
    ;
    """

    return execute_query(connection, add_chair_query, get_id=True)


def get_chair(connection, chair_id):
    get_chair_query = f"""
    SELECT sitting_height, angle, file_path
    FROM chairs
    WHERE chair_id = {chair_id}
    ;
    """

    return execute_query(connection, get_chair_query, fetch_all=True)


def update_chair(connection, chair_id, columns, values):
    # TODO: add check if current customer "owns" this chair
    queries = []
    if len(columns) != len(values):
        return -1
    for i in range(len(columns)):
        q = f"""
        UPDATE chairs
        SET {columns[i]} = {values[i]}
        WHERE chair_id = {chair_id}
        ;"""
        queries.append(q)

    all_success = True
    for query in queries:
        if not execute_query(connection, query):
            all_success = False

    return all_success


def delete_chair(connection, chair_id):
    delete_chair_querry = f"""
    DELETE FROM chairs
    WHERE chair_id = {chair_id}
    ;"""

    execute_query(connection, delete_chair_querry)


def add_customer(connection, username, hashed_password):
    add_customer_querry = f"""
    INSERT INTO customers (username, hashed_password)
    VALUES ({username}, {hashed_password})
    ;"""

    return execute_query(connection, add_customer_querry, get_id=True)


def delete_customer(connection, customer_id):
    delete_customer_querry = f"""
    DELETE FROM customers
    WHERE customer_id = {customer_id}
    ;"""

    execute_query(connection, delete_customer_querry)


def add_WIP(connection, customer_id, chair_id):
    add_WIP_querry = f"""
    INSERT INTO WIPs (customer_id, chair_id)
    VALUES ({customer_id}, {chair_id})
    ;"""

    return execute_query(connection, add_WIP_querry, get_id=True)


def delete_WIP(connection, WIP_id):
    delete_WIP_querry = f"""
    DELETE FROM WIPs
    WHERE WIP_id = {WIP_id}
    ;"""

    execute_query(connection, delete_WIP_querry)


def add_order(connection, customer_id, chair_id, count):
    add_order_querry = f"""
    INSERT INTO orders (customer_id, chair_id, count)
    VALUES ({customer_id}, {chair_id}, {count})
    ;"""

    return execute_query(connection, add_order_querry, get_id=True)


def confirm_order(connection, order_id):
    confirm_order_querry = f"""
    UPDATE orders
    SET status = 'CONFIRMED'
    WHERE order_id = {order_id}
    ;"""

    execute_query(connection, confirm_order_querry)


def close_order(connection, order_id):
    close_order_querry = f"""
    UPDATE orders
    SET status = 'CLOSED'
    WHERE order_id = {order_id}
    ;"""

    execute_query(connection, close_order_querry)


def delete_order(connection, order_id):
    delete_order_querry = f"""
    DELETE FROM orders
    WHERE order_id = {order_id}
    ;"""

    execute_query(connection, delete_order_querry)
