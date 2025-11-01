import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def paginate_users(page_size, offset=0):
    """
    Fetch a page of users starting from the given offset.

    Args:
        page_size (int): Number of rows per page.
        offset (int): Starting row index for pagination.

    Returns:
        list: A list of user rows for the current page.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database="ALX_prodev",
            port=os.getenv("MYSQL_PORT")
        )
        cursor = connection.cursor()
        query = "SELECT * FROM user_data LIMIT %s OFFSET %s;"
        cursor.execute(query, (page_size, offset))
        rows = cursor.fetchall()
        return rows

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return []

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def lazy_paginate(page_size):
    """
    Generator function that lazily fetches users page by page.

    Args:
        page_size (int): Number of rows per page.

    Yields:
        list: A page of user rows.
    """
    offset = 0
    while True:  # Only one loop is used
        page = paginate_users(page_size, offset)
        if not page:  # No more rows
            break
        yield page
        offset += page_size  # Move to next page
