import sqlite3

conn = sqlite3.connect('court_queries.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM case_queries")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
