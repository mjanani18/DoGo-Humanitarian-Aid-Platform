import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# ---------------- NGO TABLE ----------------
c.execute("""
CREATE TABLE IF NOT EXISTS ngo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_name TEXT,
    ngo_name TEXT,
    password TEXT,
    ngo_id TEXT UNIQUE,
    email TEXT,
    phone TEXT,
    address TEXT,
    verification_type TEXT,
    verification_number TEXT
)
""")

# ---------------- DONATIONS TABLE ----------------
c.execute("""
CREATE TABLE IF NOT EXISTS donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    item TEXT,
    status TEXT,
    proof_link TEXT,

    ngo_person_name TEXT,
    ngo_name TEXT,
    ngo_id TEXT,
    ngo_email TEXT,
    ngo_phone TEXT,
    ngo_address TEXT
)
""")
 
conn.commit()
conn.close()

print("Database and tables created successfully ✅")



