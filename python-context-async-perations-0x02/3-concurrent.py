# Run multiple database queries concurrently using asyncio.gather

# use the aiosqlite library to interact with SQLite 
# asynchronously. To learn more about it.

# Write two asynchronous functions: async_fetch_users()
# and async_fetch_orders()_users() that fetches all users 
# and users older than 40 respectively.

# use the asyncio.gather() to execute both queries
# concurrently.

# use the asyncio.run(fetch_concurrently()) to run
# the concurrent fetch. 

import aiosqlite
import asyncio      

async def async_fetch_users(db_name):
    async with aiosqlite.connect(db_name) as db:
        cursor = await db.execute('SELECT * FROM users;')
        results = await cursor.fetchall()
        await cursor.close()
        return results  
    