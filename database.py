import sqlite3

DB_NAME = "academy.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # جدول کاربران
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    # کاربر پیش‌فرض ادمین در صورت عدم وجود
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")

    # جدول کلاس‌ها
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            day_time TEXT DEFAULT '',
            teacher TEXT DEFAULT ''
        )
    """)

    # جدول هنرجویان
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT DEFAULT '',
            FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE
        )
    """)

    # جدول حضور و غیاب
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
            UNIQUE(student_id, date)
        )
    """)

    conn.commit()
    conn.close()

# --- توابع احراز هویت ---
def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# --- توابع کلاس‌ها ---
def get_all_classes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM classes ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_class_by_id(class_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM classes WHERE id = ?", (class_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def add_class(title, day_time="", teacher=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO classes (title, day_time, teacher) VALUES (?, ?, ?)",
        (title.strip(), day_time.strip() if day_time else "", teacher.strip() if teacher else "")
    )
    conn.commit()
    conn.close()

def delete_class(class_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM classes WHERE id = ?", (class_id,))
    conn.commit()
    conn.close()

# --- توابع هنرجویان ---
def get_students_by_class(class_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE class_id = ? ORDER BY id ASC", (class_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_student(class_id, full_name, phone=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (class_id, full_name, phone) VALUES (?, ?, ?)",
        (class_id, full_name.strip(), phone.strip() if phone else "")
    )
    conn.commit()
    conn.close()

def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()

# --- توابع حضور و غیاب ---
def get_attendance_by_date(class_id, date_str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s.id as student_id, 
            s.full_name, 
            s.phone, 
            COALESCE(a.status, 'absent') as status
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id AND a.date = ?
        WHERE s.class_id = ?
        ORDER BY s.id ASC
    """, (date_str, class_id))
    rows = cursor.fetchall()
    conn.close()
    return rows

def set_attendance(student_id: int, date_str: str, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO attendance (student_id, date, status)
        VALUES (?, ?, ?)
        ON CONFLICT(student_id, date) DO UPDATE SET status=excluded.status
    """, (student_id, date_str, status))
    conn.commit()
    conn.close()

def get_class_attendance_report(class_id: int):
    """دریافت گزارش تفکیکی و آماری حضور و غیاب هنرجویان یک کلاس"""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # ۱. تعداد کل جلسات ثبت شده برای این کلاس (با JOIN چون class_id در جدول attendance نیست)
        cursor.execute("""
            SELECT COUNT(DISTINCT a.date) as total_sessions
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE s.class_id = ?
        """, (class_id,))
        row = cursor.fetchone()
        total_sessions = row["total_sessions"] if row and row["total_sessions"] else 0

        # ۲. محاسبه آمار هر هنرجو
        cursor.execute("""
            SELECT 
                s.id as student_id,
                s.full_name,
                s.phone,
                SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as present_count,
                SUM(CASE WHEN a.status = 'justified' THEN 1 ELSE 0 END) as justified_count,
                SUM(CASE WHEN a.status = 'unexcused' THEN 1 ELSE 0 END) as unexcused_count,
                COUNT(a.id) as recorded_sessions
            FROM students s
            LEFT JOIN attendance a ON s.id = a.student_id
            WHERE s.class_id = ?
            GROUP BY s.id
            ORDER BY s.full_name ASC
        """, (class_id,))

        students_stats = []
        for r in cursor.fetchall():
            recorded = r["recorded_sessions"]
            present = r["present_count"] or 0
            justified = r["justified_count"] or 0
            unexcused = r["unexcused_count"] or 0

            # محاسبه درصد حضور بر اساس کل جلسات کلاس
            percent = (present / total_sessions * 100) if total_sessions > 0 else 0

            students_stats.append({
                "student_id": r["student_id"],
                "full_name": r["full_name"],
                "phone": r["phone"] or "بدون شماره",
                "present": present,
                "justified": justified,
                "unexcused": unexcused,
                "recorded": recorded,
                "percent": round(percent, 1),
            })

        return {
            "total_sessions": total_sessions,
            "students": students_stats,
        }
    finally:
        conn.close()

def get_class_held_dates(class_id: int):
    """لیست تاریخ‌های منحصر‌به‌فردی که برای این کلاس حضور و غیاب ثبت شده را برمی‌گرداند"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT a.date 
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE s.class_id = ?
            ORDER BY a.date DESC
        """, (class_id,))
        rows = cursor.fetchall()
        return [r["date"] for r in rows]
    finally:
        conn.close()
