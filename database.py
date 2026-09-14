import sqlite3
from pathlib import Path

# مسیر پایگاه داده
BASE_DIR = Path(__file__).resolve().parent
DB_NAME = str(BASE_DIR / "academy.db")


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
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

    # افزودن کاربر پیش‌فرض ادمین
    cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", "admin123")
        )

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


# =========================================================
# توابع مربوط به احراز هویت
# =========================================================

def verify_user(username, password):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        return cursor.fetchone() is not None
    finally:
        conn.close()


# =========================================================
# توابع مربوط به کلاس‌ها
# =========================================================

def get_all_classes():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, day_time, teacher FROM classes ORDER BY id DESC")
        return cursor.fetchall()
    finally:
        conn.close()


def get_class_by_id(class_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, day_time, teacher FROM classes WHERE id = ?", (class_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def add_class(title, day_time="", teacher=""):
    title = (title or "").strip()
    day_time = (day_time or "").strip()
    teacher = (teacher or "").strip()

    if not title:
        raise ValueError("نام کلاس نمی‌تواند خالی باشد.")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO classes (title, day_time, teacher) VALUES (?, ?, ?)",
            (title, day_time, teacher)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def delete_class(class_id):
    """حذف کامل یک کلاس همراه با دانش‌آموزان و سوابق حضور و غیاب مربوطه"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # ۱. حذف تمامی سوابق حضور و غیاب هنرجویان این کلاس
        cursor.execute(
            """
            DELETE FROM attendance
            WHERE student_id IN (SELECT id FROM students WHERE class_id = ?)
            """,
            (class_id,)
        )

        # ۲. حذف تمامی هنرجویان این کلاس
        cursor.execute("DELETE FROM students WHERE class_id = ?", (class_id,))

        # ۳. حذف خود رکورد کلاس
        cursor.execute("DELETE FROM classes WHERE id = ?", (class_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# =========================================================
# توابع مربوط به هنرجویان
# =========================================================

def get_all_students():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, class_id, full_name, phone FROM students ORDER BY id ASC")
        return cursor.fetchall()
    finally:
        conn.close()


def get_students_by_class(class_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, class_id, full_name, phone FROM students WHERE class_id = ? ORDER BY id ASC",
            (class_id,)
        )
        return cursor.fetchall()
    finally:
        conn.close()


def add_student(class_id, full_name, phone=""):
    # پشتیبانی دوگانه از جابجایی آرگومان‌ها
    if isinstance(full_name, int) and not isinstance(class_id, int):
        class_id, full_name = full_name, class_id

    full_name = str(full_name or "").strip()
    phone = str(phone or "").strip()

    if not full_name:
        raise ValueError("نام هنرجو نمی‌تواند خالی باشد.")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (class_id, full_name, phone) VALUES (?, ?, ?)",
            (class_id, full_name, phone)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def delete_student(student_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# =========================================================
# توابع حضور و غیاب و گزارش‌گیری
# =========================================================

def get_attendance_by_date(class_id, date_str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                s.id AS student_id,
                s.full_name,
                s.phone,
                COALESCE(a.status, 'absent') AS status
            FROM students AS s
            LEFT JOIN attendance AS a
                ON s.id = a.student_id
                AND a.date = ?
            WHERE s.class_id = ?
            ORDER BY s.id ASC
            """,
            (date_str, class_id)
        )
        return cursor.fetchall()
    finally:
        conn.close()


def set_attendance(student_id, date_str, status):
    status = (status or "").strip()
    if not status:
        raise ValueError("وضعیت حضور و غیاب نمی‌تواند خالی باشد.")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO attendance (student_id, date, status)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, date)
            DO UPDATE SET status = excluded.status
            """,
            (student_id, date_str, status)
        )
        conn.commit()
    finally:
        conn.close()


def delete_attendance_date(class_id, date_str):
    """حذف سوابق حضور و غیاب یک تاریخ مشخص برای یک کلاس"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM attendance
            WHERE date = ? AND student_id IN (
                SELECT id FROM students WHERE class_id = ?
            )
            """,
            (date_str, class_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_class_attendance_report(class_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(DISTINCT a.date) AS total_sessions
            FROM attendance AS a
            INNER JOIN students AS s ON a.student_id = s.id
            WHERE s.class_id = ?
            """,
            (class_id,)
        )
        row = cursor.fetchone()
        total_sessions = row["total_sessions"] if (row and row["total_sessions"]) else 0

        cursor.execute(
            """
            SELECT
                s.id AS student_id,
                s.full_name,
                s.phone,
                SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS present_count,
                SUM(CASE WHEN a.status = 'justified' THEN 1 ELSE 0 END) AS justified_count,
                SUM(CASE WHEN a.status = 'unexcused' THEN 1 ELSE 0 END) AS unexcused_count,
                COUNT(a.id) AS recorded_sessions
            FROM students AS s
            LEFT JOIN attendance AS a ON s.id = a.student_id
            WHERE s.class_id = ?
            GROUP BY s.id, s.full_name, s.phone
            ORDER BY s.full_name ASC
            """,
            (class_id,)
        )

        students_stats = []
        for student in cursor.fetchall():
            present = student["present_count"] or 0
            justified = student["justified_count"] or 0
            unexcused = student["unexcused_count"] or 0
            recorded = student["recorded_sessions"] or 0
            percent = (present / total_sessions * 100) if total_sessions > 0 else 0

            students_stats.append({
                "student_id": student["student_id"],
                "full_name": student["full_name"],
                "phone": student["phone"] or "بدون شماره",
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


def get_class_held_dates(class_id):
    """دریافت لیست تمامی تاریخ‌هایی که برای این کلاس حضور و غیاب ثبت شده است"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT DISTINCT a.date
            FROM attendance AS a
            INNER JOIN students AS s ON a.student_id = s.id
            WHERE s.class_id = ?
            ORDER BY a.date DESC
            """,
            (class_id,)
        )
        return [row["date"] for row in cursor.fetchall()]
    finally:
        conn.close()


# =========================================================
# کلاس دیتابیس جهت سازگاری با شیوه فراخوانی شیءگرا Database()
# =========================================================

class Database:
    def __init__(self):
        init_db()

    def verify_user(self, username, password):
        return verify_user(username, password)

    def get_all_classes(self):
        return get_all_classes()

    def get_class_by_id(self, class_id):
        return get_class_by_id(class_id)

    def add_class(self, title, day_time="", teacher=""):
        return add_class(title, day_time, teacher)

    def delete_class(self, class_id):
        return delete_class(class_id)

    def get_all_students(self):
        return get_all_students()

    def get_students_by_class(self, class_id):
        return get_students_by_class(class_id)

    def add_student(self, arg1, arg2, arg3=""):
        """
        پشتیبانی دوگانه:
        ۱. add_student(class_id, full_name, phone)
        ۲. add_student(full_name, phone, class_id)
        """
        if isinstance(arg1, int) or (isinstance(arg1, str) and arg1.isdigit() and not isinstance(arg3, int)):
            return add_student(class_id=int(arg1), full_name=arg2, phone=arg3)
        else:
            class_id = int(arg3) if str(arg3).isdigit() else 0
            return add_student(class_id=class_id, full_name=arg1, phone=arg2)

    def delete_student(self, student_id):
        return delete_student(student_id)

    def get_attendance_by_date(self, class_id, date_str):
        return get_attendance_by_date(class_id, date_str)

    def set_attendance(self, student_id, date_str, status):
        return set_attendance(student_id, date_str, status)

    def delete_attendance_date(self, class_id, date_str):
        return delete_attendance_date(class_id, date_str)

    def get_class_attendance_report(self, class_id):
        return get_class_attendance_report(class_id)

    def get_class_held_dates(self, class_id):
        return get_class_held_dates(class_id)


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
