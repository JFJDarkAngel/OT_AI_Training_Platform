import sqlite3
from pathlib import Path

# Database location
DATABASE_PATH = Path("data/platform.db")


def get_connection():
    """
    Create and return a connection to the SQLite database.
    """

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    return connection

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "platform.db"


def get_connection() -> sqlite3.Connection:
    """
    Create and return a SQLite database connection.
    """

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection