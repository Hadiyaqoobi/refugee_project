import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            country TEXT,
            phone TEXT,
            address TEXT,
            preferences TEXT,
            frequency TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_user(data):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (
            first_name, last_name, email, country, phone, address, preferences, frequency
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data["first_name"],
        data["last_name"],
        data["email"],
        data["country"],
        data["phone"],
        data["address"],
        ",".join(data["preferences"]),
        data["frequency"]
    ))
    conn.commit()
    conn.close()
