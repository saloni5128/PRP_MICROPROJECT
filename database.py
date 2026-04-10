import sqlite3

DB_NAME = "blood_donor_system.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS donors (
                donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                blood_group TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                city TEXT NOT NULL,
                area TEXT NOT NULL,
                address TEXT,
                is_available INTEGER DEFAULT 1,
                last_donation_date TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blood_requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                blood_group TEXT NOT NULL,
                units_required INTEGER NOT NULL,
                hospital_name TEXT NOT NULL,
                city TEXT NOT NULL,
                area TEXT NOT NULL,
                contact_name TEXT NOT NULL,
                contact_phone TEXT NOT NULL,
                required_date TEXT NOT NULL,
                priority TEXT DEFAULT 'Normal',
                status TEXT DEFAULT 'Pending'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS donations (
                donation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                donor_id INTEGER NOT NULL,
                donation_date TEXT NOT NULL,
                hospital_name TEXT NOT NULL,
                remarks TEXT,
                FOREIGN KEY (donor_id) REFERENCES donors(donor_id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    except Exception as e:
        print("Database Error:", e)

