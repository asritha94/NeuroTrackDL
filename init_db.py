import sqlite3

con = sqlite3.connect("users.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

con.commit()
con.close()

print("✅ users.db created")
