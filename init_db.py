import sqlite3

conn = sqlite3.connect('court_queries.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS case_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_type TEXT,
    case_number TEXT,
    case_year TEXT,
    response_summary TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()
print("Table created...")