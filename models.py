"""CRUD operations for expenses."""

from typing import Iterable, Optional

from db import get_connection


def add_expense(title: str, amount: float, category: str, date: str) -> None:
    """Insert a new expense row."""
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO expenses (title, amount, category, date) VALUES (?, ?, ?, ?)",
            (title, amount, category, date),
        )
        connection.commit()


def get_all_expenses() -> Iterable[dict]:
    """Fetch all expenses ordered by date descending."""
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, title, amount, category, date FROM expenses ORDER BY date DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_expense(expense_id: int) -> Optional[dict]:
    """Fetch a single expense by ID."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, title, amount, category, date FROM expenses WHERE id = ?",
            (expense_id,),
        ).fetchone()
    return dict(row) if row else None


def update_expense(expense_id: int, title: str, amount: float, category: str, date: str) -> None:
    """Update an expense row."""
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE expenses
            SET title = ?, amount = ?, category = ?, date = ?
            WHERE id = ?
            """,
            (title, amount, category, date, expense_id),
        )
        connection.commit()


def delete_expense(expense_id: int) -> None:
    """Remove an expense by ID."""
    with get_connection() as connection:
        connection.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        connection.commit()
