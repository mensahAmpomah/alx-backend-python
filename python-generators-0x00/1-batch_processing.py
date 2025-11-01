import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables (MySQL credentials)
load_dotenv()


def stream_users_in_batches(batch_size):
    """
    Generator that streams rows from the 'user_data' table in batches.

    Args:
        batch_size (int): Number of rows to fetch per batch.

    Yields:
        list: A list (batch) of rows from the 'user_data' table.
    """
    try:
        # 1️⃣ Connect to the MySQL database
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database="ALX_prodev",
            port=os.getenv("MYSQL_PORT")
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_data;")

        # 2️⃣ Fetch and yield data in batches
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch

    except mysql.connector.Error as err:
        print(f"Database error: {err}")

    finally:
        # 3️⃣ Close connection
        if connection.is_connected():
            cursor.close()
            connection.close()


def batch_processing(batch_size):
    """
    Processes each batch to filter users over the age of 25.

    Args:
        batch_size (int): Number of users to fetch per batch.

    Yields:
        list: A filtered batch containing only users aged > 25.
    """
    # Use the first generator to get batches
    for batch in stream_users_in_batches(batch_size):
        filtered = [user for user in batch if user[3] > 25]  # user[3] = age column
        yield filtered