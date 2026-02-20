# Smart Expense Tracker (Flask + SQLite)

A clean, beginner-friendly expense tracker designed for interview readiness. It demonstrates full CRUD, summary analytics, and clear usage of data structures and algorithms in a practical backend project.

## ✨ Features
- Add, edit, and delete expenses
- View all expenses with simple UI
- Category-wise summary (hash map aggregation)
- Monthly summary (hash map aggregation)
- Sort expenses by amount (descending)

## 🧰 Tech Stack (and why)
- **Python + Flask**: Lightweight, fast to learn, and perfect for explaining routing, templates, and REST-style flows in interviews.
- **SQLite**: Zero-config, file-based database that keeps the project simple and portable while still representing real DB usage.
- **HTML/CSS/JS**: Minimal UI for clarity and focus on backend logic.

## 📁 Project Structure
```
expense_tracker/
├── app.py              # Flask app & routes
├── db.py               # Database connection & table creation
├── models.py           # CRUD operations
├── utils.py            # DSA logic: summaries, sorting
└── templates/
    └── index.html      # Simple UI
```

## 🚀 How to Run Locally
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Start the app**
   ```bash
   python app.py
   ```
3. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

> The SQLite database file (`expenses.db`) is created automatically on first run.

## ☁️ Deploying to Render.com

Use the provided `render.yaml`, `Procfile`, and `requirements.txt` to deploy the project as a managed Python Web Service:

1. **Push the project to GitHub.** Render connects directly to Git repositories.
2. **Create a Blueprint** on [Render](https://render.com):
   - Dashboard → *New +* → *Blueprint* → pick your repo.
   - Render will detect `render.yaml` and prefill the service (`smart-expense-tracker`).
3. **Review the service settings** (populated from `render.yaml`):
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
   - Environment variable `EXPENSE_DB_PATH=/var/lib/expense-tracker/expenses.db`
   - Persistent disk mounted at `/var/lib/expense-tracker` (keeps the SQLite file safe across deploys).
4. **Click “Deploy”.** Render installs dependencies, runs migrations (handled automatically via `init_db()`), and starts Gunicorn.

> Want to deploy manually instead of the Blueprint? Create a new “Web Service (Python)” on Render, point it at the repo, then copy the same build/start commands, env var, and disk settings.

## 🧠 DSA Usage (Interview-friendly)
- **Hash maps for aggregation**: Category and monthly summaries are built using dictionaries to achieve **O(n)** time.
- **Sorting**: Expenses are sorted by amount using Python’s built-in sort, which runs in **O(n log n)** time.
- These are explicitly implemented in `utils.py` with time-complexity comments.

## ✅ Edge Cases Handled
- Empty list (no expenses yet)
- Invalid input (missing fields, negative amount, invalid date)

## 🧩 How This Scales in the Future
- Replace SQLite with PostgreSQL/MySQL for multi-user support.
- Add authentication (optional) and role-based views.
- Move summaries to SQL aggregation for large datasets.
- Add API endpoints and a modern frontend (React/Vue).

## 🗣️ How to Explain in Interviews
- **Why Flask?** It’s lightweight and shows understanding of HTTP routing, templates, and backend flow without overhead.
- **Why SQLite?** Perfect for quick demos; illustrates DB design without setup complexity.
- **Where is DSA used?** In summary aggregations (hash maps) and sorting (O(n log n)).
- **Why this project?** It is realistic, shows CRUD + analytics, and maps directly to backend fundamentals.

---

If you’re prepping for SDE internships, this project gives you a strong, practical story to tell during interviews.
