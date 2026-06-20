import sqlite3

from config import DATABASE_FILE


def initialise_database():
    conn = sqlite3.connect(DATABASE_FILE, timeout=30)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transfers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            club_id TEXT,
            city TEXT,
            country TEXT,
            manager TEXT,
            wallet TEXT,
            club_name TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def insert_transfer(
    timestamp,
    club_id,
    city,
    country,
    manager,
    wallet,
    club_name,
):
    conn = sqlite3.connect(DATABASE_FILE, timeout=30)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO transfers(
            timestamp,
            club_id,
            city,
            country,
            manager,
            wallet,
            club_name
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            club_id,
            city,
            country,
            manager,
            wallet,
            club_name,
        ),
    )
    conn.commit()
    conn.close()
