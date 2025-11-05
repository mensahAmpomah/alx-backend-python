import time
import sqlite3
import functools

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()
            print("[LOG] Database connection closed.")
    return wrapper


def retry_on_failure(retries=3, delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    print(f"[LOG] Attempt {attempt + 1} of {retries}")
                    return func(*args, **kwargs)  # Try to run the DB operation
                except sqlite3.OperationalError as e:
                    # Handles transient errors (like "database is locked" or connection lost)
                    attempt += 1
                    print(f"[WARNING] Database operation failed: {e}")
                    if attempt < retries:
                        print(f"[LOG] Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        print("[ERROR] All retries failed.")
                        raise
        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


users = fetch_users_with_retry()
print(users)