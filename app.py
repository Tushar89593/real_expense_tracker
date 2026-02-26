"""Flask application routes for the Smart Expense Tracker."""

import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from db import init_db
from models import (
    add_expense,
    create_google_user,
    create_user,
    delete_expense,
    get_all_expenses,
    get_expense,
    get_user_by_id,
    update_expense,
    verify_user,
)
from utils import category_summary, monthly_summary, sort_by_amount_desc

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24).hex()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

init_db()  # Ensure DB exists when the app boots (Gunicorn, etc.)


class User(UserMixin):
    """Wrapper for Flask-Login compatibility."""

    def __init__(self, user_dict):
        self.id = user_dict["id"]
        self.email = user_dict["email"]
        self.name = user_dict["name"]


@login_manager.user_loader
def load_user(user_id):
    """Load a user from the database for Flask-Login."""
    user_dict = get_user_by_id(int(user_id))
    if user_dict:
        return User(user_dict)
    return None


@app.route("/")
def index():
    """Render the dashboard with expenses and summaries."""
    expenses = []
    edit_expense = None

    if current_user.is_authenticated:
        expenses = get_all_expenses(current_user.id)

        sort_option = request.args.get("sort")
        if sort_option == "amount":
            expenses = sort_by_amount_desc(expenses)

        edit_id = request.args.get("edit")
        if edit_id:
            edit_expense = get_expense(int(edit_id))
            if edit_expense and edit_expense.get("user_id") != current_user.id:
                edit_expense = None
    else:
        sort_option = None

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
        edit_expense=edit_expense,
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
@login_required
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

    add_expense(title, amount, category, date_value, current_user.id)
    return redirect(url_for("index"))


@app.route("/update/<int:expense_id>", methods=["POST"])
@login_required
def update(expense_id: int):
    """Update an existing expense."""
    expense = get_expense(expense_id)
    if not expense or expense.get("user_id") != current_user.id:
        return redirect(url_for("index", error="Expense not found."))

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
@login_required
def delete(expense_id: int):
    """Delete an expense."""
    expense = get_expense(expense_id)
    if not expense or expense.get("user_id") != current_user.id:
        return redirect(url_for("index", error="Expense not found."))

    delete_expense(expense_id)
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle login page and form submission."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            return render_template("login.html", error="Please fill in all fields.")

        user_dict = verify_user(email, password)
        if user_dict:
            login_user(User(user_dict))
            return redirect(url_for("index"))
        return render_template("login.html", error="Invalid email or password.")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handle registration page and form submission."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not name or not email or not password:
            return render_template("register.html", error="Please fill in all fields.")

        if len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters.")

        user_id = create_user(email, password, name)
        if user_id is None:
            return render_template("register.html", error="An account with this email already exists.")

        user_dict = get_user_by_id(user_id)
        login_user(User(user_dict))
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/auth/google/callback", methods=["POST"])
def google_callback():
    """Handle Google sign-in callback with ID token from frontend."""
    # This endpoint receives the Google ID token from the frontend
    # JavaScript Google Sign-In and verifies it server-side.
    # Requires GOOGLE_CLIENT_ID environment variable to be set.
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        token = request.form.get("credential", "")
        client_id = os.environ.get("GOOGLE_CLIENT_ID", "")

        if not token or not client_id:
            return redirect(url_for("login", error="Google sign-in is not configured."))

        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), client_id)
        google_id = idinfo["sub"]
        email = idinfo["email"]
        name = idinfo.get("name", email.split("@")[0])

        user_id = create_google_user(email, name, google_id)
        user_dict = get_user_by_id(user_id)
        login_user(User(user_dict))
        return redirect(url_for("index"))
    except Exception as exc:
        app.logger.warning("Google sign-in failed: %s", exc)
        return redirect(url_for("login", error="Google sign-in failed. Please try again."))


@app.route("/logout")
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
