from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "hoctotnhe_secret"
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS users")

    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    cursor.execute("""
    INSERT INTO users (username, password, role)
    VALUES ('creator', '123456', 'creator')
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

            session["role"] = "admin"
            return redirect("/admin")

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
            INSERT INTO users(username, password, role)
            VALUES (?, ?, ?)
            """,
            (username, password, "admin")
        )

        conn.commit()
        conn.close()

        return f"Đã tạo admin: {username}"

    return render_template("creator.html")

@app.route("/pending")
def pending():

    if session.get("role") != "creator":
        return "Không có quyền truy cập!"

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, year, subject
        FROM pending_exams
        ORDER BY id DESC
        """
    )

    exams = cursor.fetchall()

    conn.close()

    return render_template(
        "pending.html",
        exams=exams
    )

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

    q = request.args.get("q", "").lower()

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, year, subject
        FROM exams
        ORDER BY id DESC
        """
    )

    all_exams = cursor.fetchall()

    conn.close()

    if q:

        exams = []

        for exam in all_exams:

            title = str(exam[1]).lower()
            year = str(exam[2]).lower()
            subject = str(exam[3]).lower()

            if (
                q in title
                or q in year
                or q in subject
            ):
                exams.append(exam)

    else:
        exams = all_exams

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

@app.route("/submit_exam", methods=["GET", "POST"])
def submit_exam():

    if request.method == "POST":

        title = request.form["title"]
        year = request.form["year"]
        subject = request.form["subject"]
        content = request.form["content"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO pending_exams(title, year, subject, content)
            VALUES (?, ?, ?, ?)
            """,
            (title, year, subject, content)
        )

        conn.commit()
        conn.close()

        return "Đã gửi đề thành công! Chờ duyệt."

    return render_template("submit_exam.html")

@app.route("/approve_exam/<int:exam_id>")
def approve_exam(exam_id):

    if session.get("role") != "creator":
        return "Không có quyền truy cập!"

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM pending_exams WHERE id=?",
        (exam_id,)
    )

    exam = cursor.fetchone()

    if exam:

        cursor.execute(
            """
            INSERT INTO exams(title, year, subject, content)
            VALUES (?, ?, ?, ?)
            """,
            (
                exam[1],
                exam[2],
                exam[3],
                exam[4]
            )
        )

        cursor.execute(
            "DELETE FROM pending_exams WHERE id=?",
            (exam_id,)
        )

    conn.commit()
    conn.close()

    return redirect("/pending")

@app.route("/reject_exam/<int:exam_id>")
def reject_exam(exam_id):

    if session.get("role") != "creator":
        return "Không có quyền truy cập!"

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM pending_exams WHERE id=?",
        (exam_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/pending")

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
