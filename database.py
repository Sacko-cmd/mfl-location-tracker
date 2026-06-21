import sqlite3
from datetime import datetime

from config import DATABASE_FILE


def _connect():
    return sqlite3.connect(DATABASE_FILE, timeout=30)


def initialise_database():
    conn = _connect()
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
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS subscribers(
            discord_user_id TEXT PRIMARY KEY,
            webhook_url TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_watchlists(
            discord_user_id TEXT PRIMARY KEY,
            cities TEXT NOT NULL,
            countries TEXT NOT NULL,
            club_ids TEXT NOT NULL,
            paused INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (discord_user_id) REFERENCES subscribers(discord_user_id)
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
    conn = _connect()
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


def register_subscriber(discord_user_id, webhook_url):
    conn = _connect()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute(
        """
        INSERT INTO subscribers(discord_user_id, webhook_url, created_at)
        VALUES (?, ?, ?)
        ON CONFLICT(discord_user_id) DO UPDATE SET
            webhook_url=excluded.webhook_url
        """,
        (str(discord_user_id), webhook_url, now),
    )
    conn.commit()
    conn.close()


def unregister_subscriber(discord_user_id):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM user_watchlists WHERE discord_user_id=?",
        (str(discord_user_id),),
    )
    cursor.execute(
        "DELETE FROM subscribers WHERE discord_user_id=?",
        (str(discord_user_id),),
    )
    conn.commit()
    conn.close()


def get_subscriber(discord_user_id):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT discord_user_id, webhook_url, created_at
        FROM subscribers
        WHERE discord_user_id=?
        """,
        (str(discord_user_id),),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "discord_user_id": row[0],
        "webhook_url": row[1],
        "created_at": row[2],
    }


def list_subscribers():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT discord_user_id, webhook_url, created_at
        FROM subscribers
        ORDER BY created_at ASC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "discord_user_id": row[0],
            "webhook_url": row[1],
            "created_at": row[2],
        }
        for row in rows
    ]


def is_registered(discord_user_id):
    return get_subscriber(discord_user_id) is not None
