"""CRUD operations for expenses and users."""

from typing import Iterable, Optional

from werkzeug.security import check_password_hash, generate_password_hash

from db import get_connection


# ── User operations ──────────────────────────────────────────────────────────


def create_user(email: str, password: str, name: str) -> Optional[int]:
    """Create a new user with email/password. Returns user id or None if email exists."""
    password_hash = generate_password_hash(password)
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
                (email, password_hash, name),
            )
            connection.commit()
            return cursor.lastrowid
    except Exception:
        return None


def get_user_by_email(email: str) -> Optional[dict]:
    """Fetch a user by email."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, email, password_hash, name, google_id FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Fetch a user by ID."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, email, password_hash, name, google_id FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def get_user_by_google_id(google_id: str) -> Optional[dict]:
    """Fetch a user by Google ID."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, email, password_hash, name, google_id FROM users WHERE google_id = ?",
            (google_id,),
        ).fetchone()
    return dict(row) if row else None


def create_google_user(email: str, name: str, google_id: str) -> int:
    """Create or get a user who signs in via Google."""
    existing = get_user_by_google_id(google_id)
    if existing:
        return existing["id"]
    existing_email = get_user_by_email(email)
    if existing_email:
        # Link Google ID to existing account
        with get_connection() as connection:
            connection.execute(
                "UPDATE users SET google_id = ? WHERE id = ?",
                (google_id, existing_email["id"]),
            )
            connection.commit()
        return existing_email["id"]
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO users (email, name, google_id) VALUES (?, ?, ?)",
            (email, name, google_id),
        )
        connection.commit()
        return cursor.lastrowid


def verify_user(email: str, password: str) -> Optional[dict]:
    """Verify email/password and return user dict or None."""
    user = get_user_by_email(email)
    if user and user["password_hash"] and check_password_hash(user["password_hash"], password):
        return user
    return None


# ── Expense operations ───────────────────────────────────────────────────────


def add_expense(title: str, amount: float, category: str, date: str, user_id: int) -> None:
    """Insert a new expense row."""
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO expenses (title, amount, category, date, user_id) VALUES (?, ?, ?, ?, ?)",
            (title, amount, category, date, user_id),
        )
        connection.commit()


def get_all_expenses(user_id: int) -> Iterable[dict]:
    """Fetch all expenses for a user ordered by date descending."""
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, title, amount, category, date FROM expenses WHERE user_id = ? ORDER BY date DESC",
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_expense(expense_id: int) -> Optional[dict]:
    """Fetch a single expense by ID."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, title, amount, category, date, user_id FROM expenses WHERE id = ?",
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
