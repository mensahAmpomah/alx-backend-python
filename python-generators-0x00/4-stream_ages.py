import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def stream_user_ages():
    """
    Generator that yields ages of users one by one.

    Yields:
        int/float: The age of a single user.
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
        cursor.execute("SELECT age FROM user_data;")
        for age, in cursor:  # Unpack tuple (age,)
            yield age

    except mysql.connector.Error as err:
        print(f"Database error: {err}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def compute_average_age():
    """
    Computes the average age using the stream_user_ages generator.

    Prints:
        Average age of users: <average>
    """
    total_age = 0
    count = 0

    # Loop 1: iterate through generator
    for age in stream_user_ages():
        total_age += age
        count += 1

    # Avoid division by zero
    average_age = total_age / count if count > 0 else 0

    print(f"Average age of users: {average_age:.2f}")


if __name__ == "__main__":
    compute_average_age()
