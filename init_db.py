import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

# Bảng tài khoản
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# Bảng đề đã đăng
cursor.execute("""
CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    school TEXT,
    subject TEXT,
    year INTEGER,
    file_path TEXT,
    uploaded_by TEXT
)
""")

# Bảng đề chờ duyệt
cursor.execute("""
CREATE TABLE IF NOT EXISTS pending_exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    school TEXT,
    subject TEXT,
    year INTEGER,
    file_path TEXT,
    note TEXT,
    status TEXT DEFAULT 'pending'
)
""")

# Bảng feedback
cursor.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    message TEXT NOT NULL
)
""")

# Tạo creator mặc định
cursor.execute("""
INSERT OR IGNORE INTO users
(username, password, role)
VALUES
('creator', '123456', 'creator')
""")

conn.commit()
conn.close()

print("Database created successfully!")
