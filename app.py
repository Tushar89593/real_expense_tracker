"""Flask application routes for the Smart Expense Tracker."""

from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for

from db import init_db
from models import (
    add_expense,
    delete_expense,
    get_all_expenses,
    get_expense,
    update_expense,
)
from utils import category_summary, monthly_summary, sort_by_amount_desc

app = Flask(__name__)
init_db()  # Ensure DB exists when the app boots (Gunicorn, etc.)


@app.route("/")
def index():
    """Render the dashboard with expenses and summaries."""
    expenses = get_all_expenses()

    sort_option = request.args.get("sort")
    if sort_option == "amount":
        expenses = sort_by_amount_desc(expenses)

    current_month = datetime.now().strftime("%Y-%m")

    summaries = {
        "category": category_summary(expenses),
        "monthly": monthly_summary(expenses, current_month),
    }

    return render_template(
        "index.html",
        expenses=expenses,
        summaries=summaries,
        sort_option=sort_option,
    )



def _parse_amount(raw_amount: str) -> float:
    """Parse and validate amount input."""
    amount = float(raw_amount)
    if amount <= 0:
        raise ValueError("Amount must be positive.")
    return amount


def _validate_date(date_value: str) -> str:
    """Validate date in YYYY-MM-DD format."""
    datetime.strptime(date_value, "%Y-%m-%d")
    return date_value


@app.route("/add", methods=["POST"])
def add():
    """Handle new expense submission."""
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "").strip()
    date_value = request.form.get("date", "").strip()
    amount_raw = request.form.get("amount", "").strip()

    if not title or not category or not date_value or not amount_raw:
        return redirect(url_for("index", error="Please fill in all fields."))

    try:
        amount = _parse_amount(amount_raw)
        _validate_date(date_value)
    except (ValueError, TypeError):
        return redirect(url_for("index", error="Invalid amount or date."))

    add_expense(title, amount, category, date_value)
    return redirect(url_for("index"))


@app.route("/update/<int:expense_id>", methods=["POST"])
def update(expense_id: int):
    """Update an existing expense."""
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "").strip()
    date_value = request.form.get("date", "").strip()
    amount_raw = request.form.get("amount", "").strip()

    if not title or not category or not date_value or not amount_raw:
        return redirect(url_for("index", error="Please fill in all fields."))

    try:
        amount = _parse_amount(amount_raw)
        _validate_date(date_value)
    except (ValueError, TypeError):
        return redirect(url_for("index", error="Invalid amount or date."))

    update_expense(expense_id, title, amount, category, date_value)
    return redirect(url_for("index"))


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id: int):
    """Delete an expense."""
    delete_expense(expense_id)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
