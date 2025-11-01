from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import csv
import uuid
import json

import os
load_dotenv()


def connect_to_prodev():
    """Connect directly to ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host=os.environ['DB_host'],
            user=os.environ['DB_user'],             
            password=os.environ['DB_password'],
            database=os.environ['DB_name']
        )
        return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev: {e}")
        return None
    

def create_table(connection):
    """Create table user_data if not exists."""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id CHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL(3,0) NOT NULL,
                INDEX (user_id)
            )
        """)
        connection.commit()
        print("Table user_data created successfully")
    except Error as e:
        print(f"Error creating table: {e}")

def insert_data(connection, csv_file):
    """Insert data from CSV into the user_data table."""
    try:
        cursor = connection.cursor()
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                user_id = str(uuid.uuid4())
                name = row['name']
                email = row['email']
                age = row['age']

                # Check for duplicate email before inserting
                cursor.execute("SELECT * FROM user_data WHERE email = %s", (email,))
                result = cursor.fetchone()
                if not result:
                    cursor.execute("""
                        INSERT INTO user_data (user_id, name, email, age)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, name, email, age))
                    count += 1

        connection.commit()
        print(f"{count} new records inserted successfully.")
    except FileNotFoundError:
        print(f"The file '{csv_file}' was not found.")
    except Error as e:
        print(f"Error inserting data: {e}")
