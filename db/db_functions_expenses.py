# db/db_functions_expenses.py

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

DB_EXPENSES = "db/expenses.db"


def connect():
    return sqlite3.connect(DB_EXPENSES)


def create_expenses_table():
    """
    Create the expenses table if it does not exist.
    One row = one receipt for one trip.
    """
    conn = connect()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_ID INTEGER NOT NULL,
            user_ID INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            amount REAL,
            currency TEXT,
            category TEXT,
            note TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS ix_expenses_trip ON expenses(trip_ID);")
    c.execute("CREATE INDEX IF NOT EXISTS ix_expenses_user ON expenses(user_ID);")
    conn.commit()
    conn.close()


def add_expense(trip_ID: int,
                user_ID: int,
                file_path: str,
                amount: float | None,
                currency: str | None,
                category: str | None,
                note: str | None):
    """
    Insert a new expense row.
    Status starts as 'pending' for future manager approval.
    """
    conn = connect()
    c = conn.cursor()
    c.execute("""
        INSERT INTO expenses (
            trip_ID, user_ID, file_path,
            amount, currency, category, note,
            status, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)
    """, (
        trip_ID,
        user_ID,
        file_path,
        amount,
        currency,
        category,
        note,
        datetime.utcnow().isoformat(timespec="seconds"),
    ))
    conn.commit()
    conn.close()


def get_expenses_for_trip(trip_ID: int, user_ID: int | None = None) -> pd.DataFrame:
    """
    Return all expenses for a trip.
    If user_ID is given, filter down to that user.
    """
    conn = connect()
    if user_ID is None:
        query = """
            SELECT id, trip_ID, user_ID, file_path,
                   amount, currency, category, note,
                   status, created_at
            FROM expenses
            WHERE trip_ID = ?
            ORDER BY created_at DESC
        """
        df = pd.read_sql_query(query, conn, params=(trip_ID,))
    else:
        query = """
            SELECT id, trip_ID, user_ID, file_path,
                   amount, currency, category, note,
                   status, created_at
            FROM expenses
            WHERE trip_ID = ? AND user_ID = ?
            ORDER BY created_at DESC
        """
        df = pd.read_sql_query(query, conn, params=(trip_ID, user_ID))
    conn.close()
    return df


def update_expense_status(expense_id: int, new_status: str):
    """
    For future manager approval dashboard.
    new_status could be 'approved', 'rejected', 'pending'.
    """
    conn = connect()
    c = conn.cursor()
    c.execute("""
        UPDATE expenses
        SET status = ?
        WHERE id = ?
    """, (new_status, expense_id))
    conn.commit()
    conn.close()


def get_total_expenses_for_trip(trip_ID: int) -> float:
    """
    Sum of approved + pending expenses for a given trip.
    (You can later filter to only 'approved' if you like.)
    """
    conn = connect()
    c = conn.cursor()
    c.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE trip_ID = ?
    """, (trip_ID,))
    total = c.fetchone()[0] or 0.0
    conn.close()
    return float(total)
