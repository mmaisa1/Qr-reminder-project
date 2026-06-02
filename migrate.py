import sqlite3

conn = sqlite3.connect('reminders.db')
c = conn.cursor()

c.execute('ALTER TABLE reminders ADD COLUMN repeat TEXT DEFAULT "none"')

conn.commit()
conn.close()

print("Migration done — repeat column added.")