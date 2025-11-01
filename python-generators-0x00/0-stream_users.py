import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables (MYSQL credentials)
load_dotenv()


def stream_users():
    """
    Connects to the 'ALX_prodev' database and streams rows
    from the 'user_data' table one at a time using a generator.

    Yields:
        tuple: A row from the user_data table.
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

        
        cursor.execute("SELECT * FROM user_data;")

        
        for row in cursor:
            yield row

    except mysql.connector.Error as err:
        print(f"Database error: {err}")

    finally:
        
        if connection.is_connected():
            cursor.close()
            connection.close()