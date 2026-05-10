from database import connect_db
import sqlite3
import bcrypt

# ---------------- REGISTER ---------------- #
def register(user, pwd, email):
    conn = connect_db()
    c = conn.cursor()

    username = user.strip()
    email = email.strip().lower()
    password = pwd.strip()

    if username == "" or password == "" or email == "":
        conn.close()
        return "Empty"

    try:
        # check username
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        if c.fetchone():
            conn.close()
            return "Username Exists"

        # check email
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        if c.fetchone():
            conn.close()
            return "Email Exists"

        # 🔥 HASH PASSWORD (bcrypt)
        hashed_pwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        c.execute("""
        INSERT INTO users (username, password, email)
        VALUES (?, ?, ?)
        """, (username, hashed_pwd, email))

        conn.commit()
        return "Success"

    except sqlite3.Error as e:
        return f"Error: {e}"

    finally:
        conn.close()


# ---------------- LOGIN ---------------- #
def login(email, password):
    conn = connect_db()
    c = conn.cursor()

    email = email.strip().lower()
    password = password.strip()

    if email == "" or password == "":
        conn.close()
        return None

    # 🔥 GET USER
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()

    if user:
        stored_pwd = user[2]  # password column

        # 🔥 FIX: ensure bytes
        if isinstance(stored_pwd, str):
            stored_pwd = stored_pwd.encode()

        # 🔥 PASSWORD CHECK
        if bcrypt.checkpw(password.encode(), stored_pwd):
            conn.close()
            return user

    conn.close()
    return None









# from database import connect_db
# import hashlib
# import sqlite3
#
# # ---------------- PASSWORD HASH ---------------- #
# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()
#
#
# # ---------------- REGISTER ---------------- #
# def register(user, pwd, email):
#     conn = connect_db()
#     c = conn.cursor()
#
#     # clean input
#     username = user.strip()
#     email = email.strip().lower()
#     password = pwd.strip()
#
#     # empty check
#     if username == "" or password == "" or email == "":
#         conn.close()
#         return "Empty"
#
#     try:
#         # check username
#         c.execute("SELECT * FROM users WHERE username=?", (username,))
#         if c.fetchone():
#             conn.close()
#             return "Username Exists"
#
#         # check email
#         c.execute("SELECT * FROM users WHERE email=?", (email,))
#         if c.fetchone():
#             conn.close()
#             return "Email Exists"
#
#         # insert user
#         hashed_pwd = hash_password(password)
#
#         c.execute("""
#         INSERT INTO users (username, password, email)
#         VALUES (?, ?, ?)
#         """, (username, hashed_pwd, email))
#
#         conn.commit()
#         return "Success"
#
#     except sqlite3.Error as e:
#         return f"Error: {e}"
#
#     finally:
#         conn.close()
#
#
# # ---------------- LOGIN (EMAIL BASED) ---------------- #
# def login(email, password):
#     conn = connect_db()
#     c = conn.cursor()
#
#     email = email.strip().lower()
#     password = password.strip()
#
#     if email == "" or password == "":
#         conn.close()
#         return None
#
#     hashed_pwd = hash_password(password)
#
#     c.execute("""
#     SELECT * FROM users
#     WHERE email=? AND password=?
#     """, (email, hashed_pwd))
#
#     user = c.fetchone()
#     conn.close()
#
#     return user
#
