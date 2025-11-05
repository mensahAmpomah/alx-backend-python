import time
import sqlite3
import functools

query_cache = {}

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


def cache_query(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        query = kwargs.get("query") or (args[0] if args else None)

        if query in query_cache:
            print(f"[CACHE] Returning cached result for query: {query}")
            return query_cache[query]

        print(f"[DB] Executing and caching result for query: {query}")
        result = func(conn, *args, **kwargs)

        # 4️⃣ Store result in cache
        query_cache[query] = result
        return result
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


users = fetch_users_with_cache(query="SELECT * FROM users")

users_again = fetch_users_with_cache(query="SELECT * FROM users")

print(users_again)