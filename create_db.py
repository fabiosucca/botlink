import sqlite3

def create_database():
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    
    # Tabella admin
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY,
            username TEXT,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabella utenti
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    db.commit()
    db.close()
    print("✅ Database creato con successo!")

if __name__ == "__main__":
    create_database()
