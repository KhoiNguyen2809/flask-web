from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "hoctotnhe_secret"
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
    CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        year INTEGER,
        subject TEXT,
        content TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pending_exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        year INTEGER,
        subject TEXT,
        content TEXT
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
                session["role"] = "creator"
                return redirect("/creator")

            return f"Xin chào Admin {username}!"

        return "Sai tài khoản hoặc mật khẩu"

    return render_template("login.html")
@app.route("/creator", methods=["GET", "POST"])
def creator():
    if session.get("role") != "creator":
        return "Không có quyền truy cập!"

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

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")
@app.route("/routes")
def routes():
    return str(app.url_map)

@app.route("/add_exam", methods=["GET", "POST"])
def add_exam():

    if session.get("role") != "creator":
        return "Không có quyền truy cập!"

    if request.method == "POST":

        title = request.form["title"]
        year = request.form["year"]
        subject = request.form["subject"]
        content = request.form["content"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO exams(title, year, subject, content)
            VALUES (?, ?, ?, ?)
            """,
            (title, year, subject, content)
        )

        conn.commit()
        conn.close()

        return "Đăng đề thành công!"

    return render_template("add_exam.html")

@app.route("/exams")
def exams():

    q = request.args.get("q", "")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, year, subject
        FROM exams
        WHERE title LIKE ?
        OR subject LIKE ?
        OR CAST(year AS TEXT) LIKE ?
        ORDER BY id DESC
        """,
        (
            f"%{q}%",
            f"%{q}%",
            f"%{q}%"
        )
    )

    exams = cursor.fetchall()

    conn.close()

    return render_template(
        "exams.html",
        exams=exams
    )

@app.route("/exam/<int:exam_id>")
def exam_detail(exam_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM exams WHERE id=?",
        (exam_id,)
    )

    exam = cursor.fetchone()

    conn.close()

    if not exam:
        return "Không tìm thấy đề"

    return render_template(
        "exam_detail.html",
        exam=exam
    )

@app.route("/delete_exam/<int:exam_id>")
def delete_exam(exam_id):

    if session.get("role") != "creator":
        return "Không có quyền truy cập!"

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM exams WHERE id=?",
        (exam_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/exams")

@app.route("/edit_exam/<int:exam_id>", methods=["GET", "POST"])
def edit_exam(exam_id):

    if session.get("role") != "creator":
        return "Không có quyền truy cập!"

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":

        title = request.form["title"]
        year = request.form["year"]
        subject = request.form["subject"]
        content = request.form["content"]

        cursor.execute(
            """
            UPDATE exams
            SET title=?, year=?, subject=?, content=?
            WHERE id=?
            """,
            (title, year, subject, content, exam_id)
        )

        conn.commit()
        conn.close()

        return redirect(f"/exam/{exam_id}")

    cursor.execute(
        "SELECT * FROM exams WHERE id=?",
        (exam_id,)
    )

    exam = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_exam.html",
        exam=exam
    )

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
