import asyncio
import aiosqlite

# Async function to fetch all users
async def async_fetch_users(db_name):
    async with aiosqlite.connect(db_name) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            users = await cursor.fetchall()
            print("All Users:", users)
            return users

# Async function to fetch users older than 40
async def async_fetch_older_users(db_name):
    async with aiosqlite.connect(db_name) as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            older_users = await cursor.fetchall()
            print("Users older than 40:", older_users)
            return older_users

# Function to run both queries concurrently
async def fetch_concurrently():
    db_name = "example.db"
    
    # Run both queries concurrently
    results = await asyncio.gather(
        async_fetch_users(db_name),
        async_fetch_older_users(db_name)
    )
    
    all_users, older_users = results
    print("\n=== Final Results ===")
    print("All Users:", all_users)
    print("Older Users:", older_users)

# Run the concurrent fetch
asyncio.run(fetch_concurrently())