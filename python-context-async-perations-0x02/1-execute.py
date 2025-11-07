import sqlite3

# implement a class based custom context manager
# ExecuteQuery that takes the query 'Select * from users
# where age > ?' and the parameter 25 returns the result
# of the query.

class ExecuteQuery:
    def __init__(self, db_name, query, params):
        self.db_name = db_name
        self.query = query
        self.params = params
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute(self.query, self.params)
        return self.cursor.fetchall()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.connection:
            self.connection.close()

# Using the context manager to perform the query
with ExecuteQuery('example.db', 'SELECT * FROM users WHERE age > ?', (25,)) as results:
    for row in results:
        print(row)