import sqlite3

conn = sqlite3.connect('reminders.db')
c = conn.cursor()

# Run only if column doesn't exist
try:
    c.execute('ALTER TABLE reminders ADD COLUMN repeat TEXT DEFAULT "none"')
    print("repeat column added.")
except:
    print("repeat column already exists, skipping.")

# OTP table
c.execute('''
    CREATE TABLE IF NOT EXISTS otp_store (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        otp TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        used INTEGER DEFAULT 0
    )
''')

conn.commit()
conn.close()

print("Migration done.")