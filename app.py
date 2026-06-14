from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO users (id, username, password)
    VALUES (1, 'creator', '123456')
    """)

    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            if username == "creator":
                return redirect("/creator")

            return f"Xin chào Admin {username}!"

        return "Sai tài khoản hoặc mật khẩu"

    return render_template("login.html")
@app.route("/creator", methods=["GET", "POST"])
def creator():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users(username, password)
            VALUES (?, ?)
            """,
            (username, password)
        )

        conn.commit()
        conn.close()

        return f"Đã tạo admin: {username}"

    return render_template("creator.html")

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
