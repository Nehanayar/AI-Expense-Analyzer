import sqlite3

# ---------------- CONNECT ---------------- #
def connect_db():
    return sqlite3.connect("expense.db", check_same_thread=False)


# ---------------- CREATE TABLES ---------------- #
def create_tables():
    conn = connect_db()
    c = conn.cursor()

    # USERS (EMAIL INCLUDED)
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT UNIQUE
    )
    """)

    # CATEGORY
    c.execute("""
    CREATE TABLE IF NOT EXISTS category(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)

    # EXPENSES
    c.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        category TEXT,
        date TEXT
    )
    """)

    # BUDGET
    c.execute("""
    CREATE TABLE IF NOT EXISTS budget(
        user_id INTEGER PRIMARY KEY,
        amount REAL
    )
    """)

    conn.commit()
    conn.close()


# ---------------- DEFAULT CATEGORIES ---------------- #
def insert_default_categories():
    defaults = ["Food", "Travel", "Shopping", "Bills", "Health"]

    conn = connect_db()
    c = conn.cursor()

    for cat in defaults:
        try:
            c.execute("INSERT INTO category (name) VALUES (?)", (cat,))
        except:
            pass

    conn.commit()
    conn.close()


def view_categories():
    conn = connect_db()
    c = conn.cursor()

    c.execute("SELECT name FROM category")
    data = c.fetchall()

    conn.close()
    return [i[0] for i in data]


def add_category(name):
    conn = connect_db()
    c = conn.cursor()

    try:
        c.execute("INSERT INTO category (name) VALUES (?)", (name,))
        conn.commit()
        return "Added"
    except:
        return "Exists"
    finally:
        conn.close()


# ---------------- EXPENSES ---------------- #
def add_expense(user_id, amount, category, date):
    conn = connect_db()
    c = conn.cursor()

    c.execute("""
    INSERT INTO expenses (user_id, amount, category, date)
    VALUES (?, ?, ?, ?)
    """, (user_id, amount, category, date))

    conn.commit()
    conn.close()


def get_expenses(user_id):
    conn = connect_db()
    c = conn.cursor()

    c.execute("""
    SELECT id, user_id, amount, category, date
    FROM expenses
    WHERE user_id=?
    """, (user_id,))

    data = c.fetchall()
    conn.close()
    return data


def view_expense(user_id):
    conn = connect_db()
    c = conn.cursor()

    c.execute("""
    SELECT amount, category, date
    FROM expenses
    WHERE user_id=?
    """, (user_id,))

    data = c.fetchall()
    conn.close()
    return data


def delete_expense(expense_id):
    conn = connect_db()
    c = conn.cursor()

    c.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()


# ---------------- BUDGET SYSTEM ---------------- #
def get_budget(user_id):
    conn = connect_db()
    c = conn.cursor()

    c.execute("SELECT amount FROM budget WHERE user_id=?", (user_id,))
    data = c.fetchone()

    conn.close()
    return data[0] if data else 0


def set_budget(user_id, amount):
    conn = connect_db()
    c = conn.cursor()

    c.execute("""
    INSERT INTO budget (user_id, amount)
    VALUES (?, ?)
    ON CONFLICT(user_id) DO UPDATE SET amount=excluded.amount
    """, (user_id, amount))

    conn.commit()
    conn.close()









