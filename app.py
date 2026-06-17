from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from werkzeug.utils import secure_filename
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
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        message TEXT
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
        content TEXT,
        views INTEGER DEFAULT 0
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

    try:
        cursor.execute(
            "ALTER TABLE feedback ADD COLUMN status TEXT DEFAULT 'pending'"
        )
        conn.commit()
    except:
        pass

    try:
        cursor.execute(
            "ALTER TABLE exams ADD COLUMN views INTEGER DEFAULT 0"
        )    
        conn.commit()
    except:
        pass

    try:
        cursor.execute(
            "ALTER TABLE exams ADD COLUMN file_path TEXT"
        )
        conn.commit()
    except:
        pass

    try:
        cursor.execute(
            "ALTER TABLE pending_exams ADD COLUMN file_path TEXT"
        )
        conn.commit()
    except:
        pass

    try:
        cursor.execute(
            "ALTER TABLE exams ADD COLUMN file_path TEXT"
        )
        conn.commit()
    except:
        pass

    try:
        cursor.execute(
            "ALTER TABLE pending_exams ADD COLUMN file_path TEXT"
        )
        conn.commit()
    except:
        pass

    conn.commit()
    conn.close()



@app.route("/")
def home():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM exams
        ORDER BY views DESC
        LIMIT 5
    """)

    top_exams = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        top_exams=top_exams
    )

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

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM exams")
    total_exams = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM pending_exams")
    pending_exams = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM feedback
        WHERE status='pending'
    """)
    pending_feedbacks = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE role='admin'
    """)
    total_admins = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "creator.html",
        total_exams=total_exams,
        pending_exams=pending_exams,
        pending_feedbacks=pending_feedbacks,
        total_admins=total_admins
    )

@app.route("/pending")
def pending():

    if session.get("role") not in ["creator", "admin"]:
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

    if session.get("role") not in ["creator", "admin"]:
        return "Không có quyền truy cập!"

    if request.method == "POST":

        title = request.form["title"]
        year = request.form["year"]
        subject = request.form["subject"]
        content = request.form["content"]
        pdf = request.files["pdf"]
        
        filename = None

        if pdf and pdf.filename:

            filename = secure_filename(pdf.filename)

            pdf.save(
                os.path.join(
                    "static/uploads",
                    filename
                )
            )

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO exams(
                title,
                year,
                subject,
                content,
                file_path
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                title,
                year,
                subject,
                content,
                filename
            )
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

    view_key = f"viewed_{exam_id}"

    if not session.get(view_key):

        cursor.execute(
            "UPDATE exams SET views = views + 1 WHERE id=?",
            (exam_id,)
        )

        conn.commit()

        session[view_key] = True

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

    if session.get("role") not in ["creator", "admin"]:
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

    if session.get("role") not in ["creator", "admin"]:
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

    if session.get("role") not in ["creator", "admin"]:
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

    if session.get("role") not in ["creator", "admin"]:
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

@app.route("/admin")
def admin():

    if session.get("role") not in ["creator", "admin"]:
        return "Không có quyền truy cập!"

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM exams")
    total_exams = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pending_exams")
    pending_exams = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM feedback
        WHERE status='pending'
    """)
    pending_feedbacks = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE role='admin'
    """)
    total_admins = cursor.fetchone()[0]

    cursor.execute("""
        SELECT title, views
        FROM exams
        ORDER BY views DESC
        LIMIT 1
    """)

    top_exam = cursor.fetchone()

    conn.close()
    
    return render_template(
        "admin.html",
        total_exams=total_exams,
        pending_exams=pending_exams,
        pending_feedbacks=pending_feedbacks,
        total_admins=total_admins,
        top_exam=top_exam
    )

@app.route("/admins")
def admins():

    if session.get("role") != "creator":
        return "Không có quyền truy cập!"

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username FROM users WHERE role='admin'"
    )

    admins = cursor.fetchall()

    conn.close()

    return render_template(
        "admins.html",
        admins=admins
    )

@app.route("/delete_admin/<int:id>")
def delete_admin(id):

    if session.get("role") != "creator":
        return "Không có quyền truy cập!"

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Lấy username trước
    cursor.execute(
        "SELECT username FROM users WHERE id=?",
        (id,)
    )

    user = cursor.fetchone()

    if user and user[0] == "creator":
        conn.close()
        return "Không thể xóa Creator!"

    cursor.execute(
        "DELETE FROM users WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admins")

@app.route("/feedback", methods=["GET", "POST"])
def feedback():

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        if not name:
            name = "Ẩn danh"
        message = request.form["message"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO feedback(name, message)
            VALUES (?, ?)
            """,
            (name, message)
        )

        conn.commit()
        conn.close()

        return "Cảm ơn bạn đã góp ý!"

    return render_template("feedback.html")

@app.route("/feedbacks")
def feedbacks():

    if session.get("role") not in ["creator", "admin"]:
        return "Không có quyền truy cập!"

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
         SELECT * FROM feedback
         WHERE status='pending'
         ORDER BY id DESC
    """)

    feedbacks = cursor.fetchall()

    conn.close()

    return render_template(
        "feedbacks.html",
        feedbacks=feedbacks
    )

@app.route("/resolve_feedback/<int:id>")
def resolve_feedback(id):

    if session.get("role") not in ["creator", "admin"]:
        return "Không có quyền truy cập!"

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE feedback
        SET status='resolved'
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/feedbacks")



if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
