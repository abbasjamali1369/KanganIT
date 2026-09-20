import flet as ft
from datetime import datetime, timedelta
import sqlite3
from database import Database, DB_NAME

# --- پالت رنگی مدرن ---
BG_MAIN = "#0B132B"
CARD_BG = "#1C2541"
TEXT_WHITE = "#FFFFFF"
TEXT_MUTED = "#8D99AE"
PURPLE_START = "#7B2CBF"
PURPLE_DARK = "#480CA8"
ACCENT_CYAN = "#00B4D8"
BORDER_COLOR = "#3A506B"

# رنگ‌های وضعیت حضور و غیاب
COLOR_PRESENT = "#10B981"       # سبز (حاضر)
COLOR_ABSENT = "#EF4444"        # قرمز (غیبت)
COLOR_EXCUSED = "#F59E0B"       # نارنجی (غیبت موجه)

WEEKDAYS = [
    "شنبه",
    "یکشنبه",
    "دوشنبه",
    "سه‌شنبه",
    "چهارشنبه",
    "پنج‌شنبه",
    "جمعه",
]


def gregorian_to_jalali(gy, gm, gd):
    """تبدیل تاریخ میلادی به شمسی بدون نیاز به کتابخانه جانبی"""
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gm > 2:
        gy2 = gy
    else:
        gy2 = gy - 1
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return f"{jy:04d}/{jm:02d}/{jd:02d}"


class StudentsView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        class_id=None,
        class_name=None,
        class_title=None,
        on_back=None,
        **kwargs,
    ):
        super().__init__(expand=True)
        self._current_page = page
        self.class_id = class_id
        self.class_name = class_name or class_title or "کلاس بدون نام"
        self.on_back = on_back
        self.db = Database()
        self.bgcolor = BG_MAIN

        # تاریخ روز جاری
        self.current_dt = datetime.now()
        self.selected_date_str = gregorian_to_jalali(
            self.current_dt.year, self.current_dt.month, self.current_dt.day
        )
        self.selected_day = self.get_persian_weekday(self.current_dt)

        # دیکشنری نگهداری وضعیت حضور و غیاب
        self.attendance_map = {}

        # ستون لیست هنرجویان ریسپانسیو
        self.students_column = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        # فیلدهای فرم افزودن هنرجو
        self.student_name_input = ft.TextField(
            label="نام و نام خانوادگی",
            border_color=BORDER_COLOR,
            focused_border_color=PURPLE_START,
            color=TEXT_WHITE,
            text_align=ft.TextAlign.RIGHT,
        )

        self.student_phone_input = ft.TextField(
            label="شماره تماس",
            border_color=BORDER_COLOR,
            focused_border_color=PURPLE_START,
            color=TEXT_WHITE,
            text_align=ft.TextAlign.RIGHT,
            keyboard_type=ft.KeyboardType.PHONE,
        )

        # ساخت محتوای صفحه
        self.content = self.build_page_content()

        # بارگذاری وضعیت‌ها و هنرجویان
        self.load_attendance_records()
        self.load_students(refresh=False)

    def get_active_page(self):
        return self._current_page or getattr(self, "page", None)

    def get_persian_weekday(self, dt):
        mapping = {
            5: "شنبه",
            6: "یکشنبه",
            0: "دوشنبه",
            1: "سه‌شنبه",
            2: "چهارشنبه",
            3: "پنج‌شنبه",
            4: "جمعه",
        }
        return mapping.get(dt.weekday(), "شنبه")

    def change_day_by_offset(self, days_offset):
        self.current_dt += timedelta(days=days_offset)
        self.selected_date_str = gregorian_to_jalali(
            self.current_dt.year, self.current_dt.month, self.current_dt.day
        )
        self.selected_day = self.get_persian_weekday(self.current_dt)
        self.content = self.build_page_content()
        self.load_attendance_records()
        self.load_students(refresh=True)

    def select_day(self, day_name):
        self.selected_day = day_name
        self.content = self.build_page_content()
        self.load_attendance_records()
        self.load_students(refresh=True)

    def build_header(self):
        """هدر ریسپانسیو و بهینه"""
        return ft.Container(
            padding=ft.Padding(left=12, right=12, top=10, bottom=10),
            bgcolor="#0D1B2A",
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=2,
                        tight=True,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                                icon_color=TEXT_WHITE,
                                icon_size=18,
                                tooltip="بازگشت",
                                on_click=self.handle_back,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.INSIGHTS_ROUNDED,
                                icon_color=COLOR_PRESENT,
                                icon_size=20,
                                tooltip="درصد حضور هنرجویان",
                                on_click=self.open_attendance_stats_dialog,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.HISTORY_ROUNDED,
                                icon_color=ACCENT_CYAN,
                                icon_size=20,
                                tooltip="جلسات برگزار شده",
                                on_click=self.open_sessions_history_dialog,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=8,
                        tight=True,
                        controls=[
                            ft.Column(
                                spacing=1,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                tight=True,
                                controls=[
                                    ft.Text(
                                        f"کلاس: {self.class_name}",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_WHITE,
                                    ),
                                    ft.Text(
                                        "ثبت و مدیریت حضور غیاب",
                                        size=10,
                                        color=TEXT_MUTED,
                                    ),
                                ],
                            ),
                            ft.CircleAvatar(
                                radius=16,
                                bgcolor=PURPLE_START,
                                content=ft.Icon(
                                    ft.Icons.GROUPS_ROUNDED,
                                    color=TEXT_WHITE,
                                    size=16,
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )

    def build_date_and_days_section(self):
        """بخش تاریخ و روزهای هفته بدون بیرون‌زدگی"""
        day_buttons = []
        for day in WEEKDAYS:
            is_active = (day == self.selected_day)
            day_buttons.append(
                ft.Container(
                    content=ft.Text(
                        day,
                        size=11,
                        weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                        color=TEXT_WHITE if is_active else TEXT_MUTED,
                    ),
                    padding=ft.Padding(left=10, right=10, top=5, bottom=5),
                    border_radius=16,
                    bgcolor=PURPLE_START if is_active else "#141E33",
                    border=ft.Border.all(
                        1, PURPLE_START if is_active else BORDER_COLOR
                    ),
                    on_click=lambda e, d=day: self.select_day(d),
                )
            )

        return ft.Container(
            padding=ft.Padding(left=12, right=12, top=6, bottom=4),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Container(
                        padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                        border_radius=8,
                        bgcolor="#141E33",
                        border=ft.Border.all(1, BORDER_COLOR),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.CHEVRON_LEFT_ROUNDED,
                                    icon_color=TEXT_WHITE,
                                    icon_size=20,
                                    tooltip="روز بعد",
                                    on_click=lambda e: self.change_day_by_offset(1),
                                ),
                                ft.Row(
                                    spacing=6,
                                    tight=True,
                                    controls=[
                                        ft.Text(
                                            f"تاریخ شمسی: {self.selected_date_str}",
                                            color=TEXT_WHITE,
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Icon(
                                            ft.Icons.CALENDAR_MONTH_ROUNDED,
                                            color=ACCENT_CYAN,
                                            size=16,
                                        ),
                                    ],
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CHEVRON_RIGHT_ROUNDED,
                                    icon_color=TEXT_WHITE,
                                    icon_size=20,
                                    tooltip="روز قبل",
                                    on_click=lambda e: self.change_day_by_offset(-1),
                                ),
                            ],
                        ),
                    ),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=4,
                        controls=[
                            ft.Text(
                                "انتخاب روز جلسه:",
                                size=11,
                                color=TEXT_MUTED,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Row(
                                scroll=ft.ScrollMode.AUTO,
                                spacing=6,
                                alignment=ft.MainAxisAlignment.END,
                                controls=day_buttons,
                            ),
                        ],
                    ),
                ],
            ),
        )

    def build_actions_bar(self):
        """نوار دکمه‌های عملیاتی شامل دکمه درصد حضور"""
        return ft.Container(
            padding=ft.Padding(left=12, right=12, top=4, bottom=6),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=6,
                        tight=True,
                        controls=[
                            ft.ElevatedButton(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.PERSON_ADD_ALT_1_ROUNDED,
                                            color=TEXT_WHITE,
                                            size=14,
                                        ),
                                        ft.Text(
                                            "افزودن هنرجو",
                                            color=TEXT_WHITE,
                                            weight=ft.FontWeight.BOLD,
                                            size=11,
                                        ),
                                    ],
                                    spacing=4,
                                    tight=True,
                                ),
                                bgcolor=PURPLE_DARK,
                                height=34,
                                style=ft.ButtonStyle(
                                    padding=ft.Padding(left=8, right=8, top=0, bottom=0),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=self.open_add_student_dialog,
                            ),
                            ft.OutlinedButton(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.CALENDAR_VIEW_MONTH_ROUNDED,
                                            color=ACCENT_CYAN,
                                            size=14,
                                        ),
                                        ft.Text(
                                            "جلسات",
                                            color=TEXT_WHITE,
                                            size=11,
                                        ),
                                    ],
                                    spacing=4,
                                    tight=True,
                                ),
                                height=34,
                                style=ft.ButtonStyle(
                                    padding=ft.Padding(left=8, right=8, top=0, bottom=0),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    side=ft.BorderSide(1, BORDER_COLOR),
                                ),
                                on_click=self.open_sessions_history_dialog,
                            ),
                            ft.OutlinedButton(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.PIE_CHART_ROUNDED,
                                            color=COLOR_PRESENT,
                                            size=14,
                                        ),
                                        ft.Text(
                                            "درصد حضور",
                                            color=TEXT_WHITE,
                                            size=11,
                                        ),
                                    ],
                                    spacing=4,
                                    tight=True,
                                ),
                                height=34,
                                style=ft.ButtonStyle(
                                    padding=ft.Padding(left=8, right=8, top=0, bottom=0),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    side=ft.BorderSide(1, BORDER_COLOR),
                                ),
                                on_click=self.open_attendance_stats_dialog,
                            ),
                        ],
                    ),
                    ft.Text(
                        f"وضعیت: {self.selected_day}",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ACCENT_CYAN,
                    ),
                ],
            ),
        )

    def load_attendance_records(self):
        if not self.class_id:
            return
        try:
            records = self.db.get_attendance_by_date(self.class_id, self.selected_date_str)
            for r in records:
                s_id = r["student_id"] if isinstance(r, (dict, sqlite3.Row)) else r[0]
                status = r["status"] if isinstance(r, (dict, sqlite3.Row)) else r[3]
                if status and status != 'absent':
                    self.attendance_map[(self.selected_date_str, s_id)] = status
        except Exception:
            pass

    def set_attendance(self, student_id, status_key):
        key = (self.selected_date_str, student_id)
        if self.attendance_map.get(key) == status_key:
            self.attendance_map.pop(key, None)
            new_status = 'absent'
        else:
            self.attendance_map[key] = status_key
            new_status = status_key

        try:
            self.db.set_attendance(student_id, self.selected_date_str, new_status)
        except Exception:
            try:
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO attendance (student_id, date, status)
                    VALUES (?, ?, ?)
                    ON CONFLICT(student_id, date)
                    DO UPDATE SET status = excluded.status
                    """,
                    (student_id, self.selected_date_str, new_status)
                )
                conn.commit()
                conn.close()
            except Exception:
                pass

        self.load_students(refresh=True)

    def delete_session_by_date(self, target_date):
        keys_to_del = [k for k in self.attendance_map.keys() if k[0] == target_date]
        for k in keys_to_del:
            self.attendance_map.pop(k, None)

        try:
            self.db.delete_attendance_date(self.class_id, target_date)
        except Exception:
            try:
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute(
                    """
                    DELETE FROM attendance
                    WHERE date = ? AND student_id IN (
                        SELECT id FROM students WHERE class_id = ?
                    )
                    """,
                    (target_date, self.class_id)
                )
                conn.commit()
                conn.close()
            except Exception:
                pass

        self.load_students(refresh=True)

    def open_sessions_history_dialog(self, e=None):
        pg = self.get_active_page()
        if not pg:
            return

        recorded_dates = set()
        for k in self.attendance_map.keys():
            recorded_dates.add(k[0])

        try:
            dates = self.db.get_class_held_dates(self.class_id)
            for d in dates:
                if d:
                    recorded_dates.add(str(d))
        except Exception:
            try:
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT DISTINCT a.date
                    FROM attendance AS a
                    INNER JOIN students AS s ON a.student_id = s.id
                    WHERE s.class_id = ?
                    """,
                    (self.class_id,)
                )
                for r in cur.fetchall():
                    if r and r[0]:
                        recorded_dates.add(str(r[0]))
                conn.close()
            except Exception:
                pass

        sessions_list = sorted(list(recorded_dates), reverse=True)
        history_items = []

        def close_history_dlg(ev=None):
            history_dialog.open = False
            pg.update()

        def confirm_remove_session(date_val):
            close_history_dlg()
            self.delete_session_by_date(date_val)

        if not sessions_list:
            history_items.append(
                ft.Container(
                    alignment=ft.Alignment(0, 0),
                    padding=20,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                        controls=[
                            ft.Icon(
                                ft.Icons.EVENT_BUSY_ROUNDED,
                                size=32,
                                color=TEXT_MUTED,
                            ),
                            ft.Text(
                                "تاکنون جلسه‌ای ثبت نشده است",
                                color=TEXT_MUTED,
                                size=11,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),
                )
            )
        else:
            for idx, s_date in enumerate(sessions_list, 1):
                history_items.append(
                    ft.Container(
                        bgcolor="#141E33",
                        border_radius=8,
                        padding=ft.Padding(left=8, right=8, top=6, bottom=6),
                        border=ft.Border.all(1, BORDER_COLOR),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_FOREVER_ROUNDED,
                                    icon_color=ft.Colors.RED_400,
                                    icon_size=18,
                                    tooltip="حذف جلسه",
                                    on_click=lambda ev, d=s_date: confirm_remove_session(d),
                                ),
                                ft.Row(
                                    spacing=6,
                                    tight=True,
                                    controls=[
                                        ft.Text(
                                            f"جلسه {idx}: {s_date}",
                                            color=TEXT_WHITE,
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Icon(
                                            ft.Icons.CHECK_CIRCLE_ROUNDED,
                                            color=COLOR_PRESENT,
                                            size=14,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    )
                )

        history_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        "جلسات برگزار شده",
                        weight=ft.FontWeight.BOLD,
                        size=14,
                        color=TEXT_WHITE,
                    ),
                    ft.Icon(
                        ft.Icons.HISTORY_TOGGLE_OFF_ROUNDED,
                        color=ACCENT_CYAN,
                        size=20,
                    ),
                ],
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=history_items,
                    spacing=6,
                    scroll=ft.ScrollMode.AUTO,
                    tight=True,
                ),
                width=320,
                height=240 if len(sessions_list) > 3 else None,
                padding=4,
            ),
            bgcolor=CARD_BG,
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.ElevatedButton(
                    content=ft.Text("بستن", color=TEXT_WHITE, size=12),
                    bgcolor=PURPLE_DARK,
                    on_click=close_history_dlg,
                ),
            ],
        )

import flet as ft
from datetime import datetime, timedelta
import sqlite3
from database import Database, DB_NAME

# --- پالت رنگی مدرن ---
BG_MAIN = "#0B132B"
CARD_BG = "#1C2541"
TEXT_WHITE = "#FFFFFF"
TEXT_MUTED = "#8D99AE"
PURPLE_START = "#7B2CBF"
PURPLE_DARK = "#480CA8"
ACCENT_CYAN = "#00B4D8"
BORDER_COLOR = "#3A506B"

# رنگ‌های وضعیت حضور و غیاب
COLOR_PRESENT = "#10B981"       # سبز (حاضر)
COLOR_ABSENT = "#EF4444"        # قرمز (غیبت)
COLOR_EXCUSED = "#F59E0B"       # نارنجی (غیبت موجه)

WEEKDAYS = [
    "شنبه",
    "یکشنبه",
    "دوشنبه",
    "سه‌شنبه",
    "چهارشنبه",
    "پنج‌شنبه",
    "جمعه",
]


def gregorian_to_jalali(gy, gm, gd):
    """تبدیل تاریخ میلادی به شمسی بدون نیاز به کتابخانه جانبی"""
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gm > 2:
        gy2 = gy
    else:
        gy2 = gy - 1
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return f"{jy:04d}/{jm:02d}/{jd:02d}"


class StudentsView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        class_id=None,
        class_name=None,
        class_title=None,
        on_back=None,
        **kwargs,
    ):
        super().__init__(expand=True)
        self._current_page = page
        
        # تبدیل امن class_id به مقدار عددی در صورت امکان
        try:
            self.class_id = int(class_id) if class_id is not None else None
        except Exception:
            self.class_id = class_id

        self.class_name = class_name or class_title or "کلاس بدون نام"
        self.on_back = on_back
        self.db = Database()
        self.bgcolor = BG_MAIN

        # تاریخ روز جاری
        self.current_dt = datetime.now()
        self.selected_date_str = gregorian_to_jalali(
            self.current_dt.year, self.current_dt.month, self.current_dt.day
        )
        self.selected_day = self.get_persian_weekday(self.current_dt)

        # دیکشنری نگهداری وضعیت حضور و غیاب
        self.attendance_map = {}

        # ستون لیست هنرجویان ریسپانسیو
        self.students_column = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        # فیلدهای فرم افزودن هنرجو
        self.student_name_input = ft.TextField(
            label="نام و نام خانوادگی",
            border_color=BORDER_COLOR,
            focused_border_color=PURPLE_START,
            color=TEXT_WHITE,
            text_align=ft.TextAlign.RIGHT,
        )

        self.student_phone_input = ft.TextField(
            label="شماره تماس",
            border_color=BORDER_COLOR,
            focused_border_color=PURPLE_START,
            color=TEXT_WHITE,
            text_align=ft.TextAlign.RIGHT,
            keyboard_type=ft.KeyboardType.PHONE,
        )

        # ساخت محتوای صفحه
        self.content = self.build_page_content()

        # بارگذاری وضعیت‌ها و هنرجویان
        self.load_attendance_records()
        self.load_students(refresh=False)

    def get_active_page(self):
        return self._current_page or getattr(self, "page", None)

    def get_persian_weekday(self, dt):
        mapping = {
            5: "شنبه",
            6: "یکشنبه",
            0: "دوشنبه",
            1: "سه‌شنبه",
            2: "چهارشنبه",
            3: "پنج‌شنبه",
            4: "جمعه",
        }
        return mapping.get(dt.weekday(), "شنبه")

    def change_day_by_offset(self, days_offset):
        self.current_dt += timedelta(days=days_offset)
        self.selected_date_str = gregorian_to_jalali(
            self.current_dt.year, self.current_dt.month, self.current_dt.day
        )
        self.selected_day = self.get_persian_weekday(self.current_dt)
        self.content = self.build_page_content()
        self.load_attendance_records()
        self.load_students(refresh=True)

    def select_day(self, day_name):
        self.selected_day = day_name
        self.content = self.build_page_content()
        self.load_attendance_records()
        self.load_students(refresh=True)

    def build_header(self):
        """هدر ریسپانسیو و بهینه"""
        return ft.Container(
            padding=ft.Padding(left=12, right=12, top=10, bottom=10),
            bgcolor="#0D1B2A",
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=2,
                        tight=True,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                                icon_color=TEXT_WHITE,
                                icon_size=18,
                                tooltip="بازگشت",
                                on_click=self.handle_back,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.INSIGHTS_ROUNDED,
                                icon_color=COLOR_PRESENT,
                                icon_size=20,
                                tooltip="درصد حضور هنرجویان",
                                on_click=self.open_attendance_stats_dialog,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.HISTORY_ROUNDED,
                                icon_color=ACCENT_CYAN,
                                icon_size=20,
                                tooltip="جلسات برگزار شده",
                                on_click=self.open_sessions_history_dialog,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=8,
                        tight=True,
                        controls=[
                            ft.Column(
                                spacing=1,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                tight=True,
                                controls=[
                                    ft.Text(
                                        f"کلاس: {self.class_name}",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_WHITE,
                                    ),
                                    ft.Text(
                                        "ثبت و مدیریت حضور غیاب",
                                        size=10,
                                        color=TEXT_MUTED,
                                    ),
                                ],
                            ),
                            ft.CircleAvatar(
                                radius=16,
                                bgcolor=PURPLE_START,
                                content=ft.Icon(
                                    ft.Icons.GROUPS_ROUNDED,
                                    color=TEXT_WHITE,
                                    size=16,
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )

    def build_date_and_days_section(self):
        """بخش تاریخ و روزهای هفته بدون بیرون‌زدگی"""
        day_buttons = []
        for day in WEEKDAYS:
            is_active = (day == self.selected_day)
            day_buttons.append(
                ft.Container(
                    content=ft.Text(
                        day,
                        size=11,
                        weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                        color=TEXT_WHITE if is_active else TEXT_MUTED,
                    ),
                    padding=ft.Padding(left=10, right=10, top=5, bottom=5),
                    border_radius=16,
                    bgcolor=PURPLE_START if is_active else "#141E33",
                    border=ft.Border.all(
                        1, PURPLE_START if is_active else BORDER_COLOR
                    ),
                    on_click=lambda e, d=day: self.select_day(d),
                )
            )

        return ft.Container(
            padding=ft.Padding(left=12, right=12, top=6, bottom=4),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Container(
                        padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                        border_radius=8,
                        bgcolor="#141E33",
                        border=ft.Border.all(1, BORDER_COLOR),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.CHEVRON_LEFT_ROUNDED,
                                    icon_color=TEXT_WHITE,
                                    icon_size=20,
                                    tooltip="روز بعد",
                                    on_click=lambda e: self.change_day_by_offset(1),
                                ),
                                ft.Row(
                                    spacing=6,
                                    tight=True,
                                    controls=[
                                        ft.Text(
                                            f"تاریخ شمسی: {self.selected_date_str}",
                                            color=TEXT_WHITE,
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Icon(
                                            ft.Icons.CALENDAR_MONTH_ROUNDED,
                                            color=ACCENT_CYAN,
                                            size=16,
                                        ),
                                    ],
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CHEVRON_RIGHT_ROUNDED,
                                    icon_color=TEXT_WHITE,
                                    icon_size=20,
                                    tooltip="روز قبل",
                                    on_click=lambda e: self.change_day_by_offset(-1),
                                ),
                            ],
                        ),
                    ),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=4,
                        controls=[
                            ft.Text(
                                "انتخاب روز جلسه:",
                                size=11,
                                color=TEXT_MUTED,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Row(
                                scroll=ft.ScrollMode.AUTO,
                                spacing=6,
                                alignment=ft.MainAxisAlignment.END,
                                controls=day_buttons,
                            ),
                        ],
                    ),
                ],
            ),
        )

    def build_actions_bar(self):
        """نوار دکمه‌های عملیاتی شامل دکمه درصد حضور"""
        return ft.Container(
            padding=ft.Padding(left=12, right=12, top=4, bottom=6),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=6,
                        tight=True,
                        controls=[
                            ft.ElevatedButton(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.PERSON_ADD_ALT_1_ROUNDED,
                                            color=TEXT_WHITE,
                                            size=14,
                                        ),
                                        ft.Text(
                                            "افزودن هنرجو",
                                            color=TEXT_WHITE,
                                            weight=ft.FontWeight.BOLD,
                                            size=11,
                                        ),
                                    ],
                                    spacing=4,
                                    tight=True,
                                ),
                                bgcolor=PURPLE_DARK,
                                height=34,
                                style=ft.ButtonStyle(
                                    padding=ft.Padding(left=8, right=8, top=0, bottom=0),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=self.open_add_student_dialog,
                            ),
                            ft.OutlinedButton(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.CALENDAR_VIEW_MONTH_ROUNDED,
                                            color=ACCENT_CYAN,
                                            size=14,
                                        ),
                                        ft.Text(
                                            "جلسات",
                                            color=TEXT_WHITE,
                                            size=11,
                                        ),
                                    ],
                                    spacing=4,
                                    tight=True,
                                ),
                                height=34,
                                style=ft.ButtonStyle(
                                    padding=ft.Padding(left=8, right=8, top=0, bottom=0),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    side=ft.BorderSide(1, BORDER_COLOR),
                                ),
                                on_click=self.open_sessions_history_dialog,
                            ),
                            ft.OutlinedButton(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.PIE_CHART_ROUNDED,
                                            color=COLOR_PRESENT,
                                            size=14,
                                        ),
                                        ft.Text(
                                            "درصد حضور",
                                            color=TEXT_WHITE,
                                            size=11,
                                        ),
                                    ],
                                    spacing=4,
                                    tight=True,
                                ),
                                height=34,
                                style=ft.ButtonStyle(
                                    padding=ft.Padding(left=8, right=8, top=0, bottom=0),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    side=ft.BorderSide(1, BORDER_COLOR),
                                ),
                                on_click=self.open_attendance_stats_dialog,
                            ),
                        ],
                    ),
                    ft.Text(
                        f"وضعیت: {self.selected_day}",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ACCENT_CYAN,
                    ),
                ],
            ),
        )

    def load_attendance_records(self):
        if not self.class_id:
            return
        try:
            records = self.db.get_attendance_by_date(self.class_id, self.selected_date_str)
            for r in (records or []):
                s_id = r["student_id"] if isinstance(r, (dict, sqlite3.Row)) else r[0]
                status = r["status"] if isinstance(r, (dict, sqlite3.Row)) else (r[3] if len(r) > 3 else r[1])
                if status and status != 'absent':
                    self.attendance_map[(self.selected_date_str, s_id)] = status
        except Exception:
            pass

    def set_attendance(self, student_id, status_key):
        key = (self.selected_date_str, student_id)
        if self.attendance_map.get(key) == status_key:
            self.attendance_map.pop(key, None)
            new_status = 'absent'
        else:
            self.attendance_map[key] = status_key
            new_status = status_key

        saved = False
        try:
            self.db.set_attendance(student_id, self.selected_date_str, new_status)
            saved = True
        except Exception:
            pass

        if not saved:
            try:
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO attendance (student_id, date, status)
                    VALUES (?, ?, ?)
                    ON CONFLICT(student_id, date)
                    DO UPDATE SET status = excluded.status
                    """,
                    (student_id, self.selected_date_str, new_status)
                )
                conn.commit()
                conn.close()
            except Exception:
                pass

        self.load_students(refresh=True)

    def delete_session_by_date(self, target_date):
        keys_to_del = [k for k in self.attendance_map.keys() if k[0] == target_date]
        for k in keys_to_del:
            self.attendance_map.pop(k, None)

        try:
            self.db.delete_attendance_date(self.class_id, target_date)
        except Exception:
            try:
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute(
                    """
                    DELETE FROM attendance
                    WHERE date = ? AND student_id IN (
                        SELECT id FROM students WHERE class_id = ?
                    )
                    """,
                    (target_date, self.class_id)
                )
                conn.commit()
                conn.close()
            except Exception:
                pass

        self.load_students(refresh=True)

    def open_sessions_history_dialog(self, e=None):
        pg = self.get_active_page()
        if not pg:
            return

        recorded_dates = set()
        for k in self.attendance_map.keys():
            recorded_dates.add(k[0])

        try:
            dates = self.db.get_class_held_dates(self.class_id)
            for d in (dates or []):
                if d:
                    recorded_dates.add(str(d))
        except Exception:
            try:
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT DISTINCT a.date
                    FROM attendance AS a
                    INNER JOIN students AS s ON a.student_id = s.id
                    WHERE s.class_id = ?
                    """,
                    (self.class_id,)
                )
                for r in cur.fetchall():
                    if r and r[0]:
                        recorded_dates.add(str(r[0]))
                conn.close()
            except Exception:
                pass

        sessions_list = sorted(list(recorded_dates), reverse=True)
        history_items = []

        def close_history_dlg(ev=None):
            history_dialog.open = False
            pg.update()

        def confirm_remove_session(date_val):
            close_history_dlg()
            self.delete_session_by_date(date_val)

        if not sessions_list:
            history_items.append(
                ft.Container(
                    alignment=ft.Alignment(0, 0),
                    padding=20,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                        controls=[
                            ft.Icon(
                                ft.Icons.EVENT_BUSY_ROUNDED,
                                size=32,
                                color=TEXT_MUTED,
                            ),
                            ft.Text(
                                "تاکنون جلسه‌ای ثبت نشده است",
                                color=TEXT_MUTED,
                                size=11,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),
                )
            )
        else:
            for idx, s_date in enumerate(sessions_list, 1):
                history_items.append(
                    ft.Container(
                        bgcolor="#141E33",
                        border_radius=8,
                        padding=ft.Padding(left=8, right=8, top=6, bottom=6),
                        border=ft.Border.all(1, BORDER_COLOR),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_FOREVER_ROUNDED,
                                    icon_color=ft.Colors.RED_400,
                                    icon_size=18,
                                    tooltip="حذف جلسه",
                                    on_click=lambda ev, d=s_date: confirm_remove_session(d),
                                ),
                                ft.Row(
                                    spacing=6,
                                    tight=True,
                                    controls=[
                                        ft.Text(
                                            f"جلسه {idx}: {s_date}",
                                            color=TEXT_WHITE,
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Icon(
                                            ft.Icons.CHECK_CIRCLE_ROUNDED,
                                            color=COLOR_PRESENT,
                                            size=14,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    )
                )

        history_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        "جلسات برگزار شده",
                        weight=ft.FontWeight.BOLD,
                        size=14,
                        color=TEXT_WHITE,
                    ),
                    ft.Icon(
                        ft.Icons.HISTORY_TOGGLE_OFF_ROUNDED,
                        color=ACCENT_CYAN,
                        size=20,
                    ),
                ],
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=history_items,
                    spacing=6,
                    scroll=ft.ScrollMode.AUTO,
                    tight=True,
                ),
                width=320,
                height=240 if len(sessions_list) > 3 else None,
                padding=4,
            ),
            bgcolor=CARD_BG,
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.ElevatedButton(
                    content=ft.Text("بستن", color=TEXT_WHITE, size=12),
                    bgcolor=PURPLE_DARK,
                    on_click=close_history_dlg,
                ),
            ],
        )

        pg.overlay.append(history_dialog)
        history_dialog.open = True
        pg.update()

    def open_attendance_stats_dialog(self, e=None):
        """نمایش پنجره مدرن درصد حضور و نمودار پیشرفت هنرجویان"""
        pg = self.get_active_page()
        if not pg:
            return

        def close_stats_dlg(ev=None):
            stats_dialog.open = False
            pg.update()

        total_sessions = 0
        students_stats = []

        try:
            conn = sqlite3.connect(DB_NAME)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute(
                """
                SELECT COUNT(DISTINCT a.date) as total
                FROM attendance AS a
                INNER JOIN students AS s ON a.student_id = s.id
                WHERE s.class_id = ?
                """,
                (self.class_id,)
            )
            row = cur.fetchone()
            if row and row["total"]:
                total_sessions = row["total"]

            try:
                cur.execute(
                    "SELECT id, full_name FROM students WHERE class_id = ? ORDER BY full_name ASC",
                    (self.class_id,)
                )
            except Exception:
                cur.execute(
                    "SELECT id, name AS full_name FROM students WHERE class_id = ? ORDER BY name ASC",
                    (self.class_id,)
                )
            students = cur.fetchall()

            for s in students:
                s_id = s["id"]
                s_name = s["full_name"]

                cur.execute(
                    "SELECT status, COUNT(*) as cnt FROM attendance WHERE student_id = ? GROUP BY status",
                    (s_id,)
                )
                status_counts = {"present": 0, "justified": 0, "unexcused": 0, "absent": 0}
                for sc in cur.fetchall():
                    status_counts[sc["status"]] = sc["cnt"]

                p_count = status_counts["present"]
                j_count = status_counts["justified"]
                u_count = status_counts["unexcused"] + status_counts["absent"]

                effective_total = max(total_sessions, (p_count + j_count + u_count))
                if effective_total > 0:
                    percent = round((p_count / effective_total) * 100, 1)
                else:
                    percent = 0.0

                students_stats.append({
                    "id": s_id,
                    "name": s_name,
                    "present": p_count,
                    "justified": j_count,
                    "unexcused": u_count,
                    "percent": percent
                })

            conn.close()
        except Exception:
            pass

        students_stats.sort(key=lambda x: x["percent"], reverse=True)

        stats_cards = []
        if not students_stats:
            stats_cards.append(
                ft.Container(
                    alignment=ft.Alignment(0, 0),
                    padding=25,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                        controls=[
                            ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=32, color=TEXT_MUTED),
                            ft.Text("هنرجویی برای محاسبه یافت نشد.", color=TEXT_MUTED, size=12),
                        ]
                    )
                )
            )
        else:
            for item in students_stats:
                pct = item["percent"]
                bar_color = COLOR_PRESENT if pct >= 75 else (COLOR_EXCUSED if pct >= 50 else COLOR_ABSENT)

                stats_cards.append(
                    ft.Container(
                        bgcolor="#141E33",
                        border_radius=10,
                        padding=10,
                        border=ft.Border.all(1, BORDER_COLOR),
                        content=ft.Column(
                            spacing=6,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Container(
                                            content=ft.Text(
                                                f"{pct}%",
                                                color=bar_color,
                                                weight=ft.FontWeight.BOLD,
                                                size=13,
                                            ),
                                            padding=ft.Padding(left=8, right=8, top=2, bottom=2),
                                            border_radius=10,
                                            bgcolor="rgba(255, 255, 255, 0.05)",
                                        ),
                                        ft.Text(
                                            item["name"],
                                            color=TEXT_WHITE,
                                            weight=ft.FontWeight.BOLD,
                                            size=12,
                                        ),
                                    ],
                                ),
                                ft.ProgressBar(
                                    value=pct / 100.0 if pct > 0 else 0.0,
                                    color=bar_color,
                                    bgcolor="#0B132B",
                                    height=6,
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(
                                            f"موجه: {item['justified']}",
                                            color=COLOR_EXCUSED,
                                            size=10,
                                        ),
                                        ft.Text(
                                            f"غیبت: {item['unexcused']}",
                                            color=COLOR_ABSENT,
                                            size=10,
                                        ),
                                        ft.Text(
                                            f"حاضر: {item['present']}",
                                            color=COLOR_PRESENT,
                                            size=10,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    )
                )

        stats_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        "درصد حضور هنرجویان",
                        weight=ft.FontWeight.BOLD,
                        size=14,
                        color=TEXT_WHITE,
                    ),
                    ft.Icon(
                        ft.Icons.INSIGHTS_ROUNDED,
                        color=COLOR_PRESENT,
                        size=22,
                    ),
                ],
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            padding=ft.Padding(left=10, right=10, top=6, bottom=6),
                            border_radius=8,
                            bgcolor="#0D1B2A",
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=6,
                                controls=[
                                    ft.Text(
                                        f"کل جلسات ثبت شده: {total_sessions}",
                                        color=ACCENT_CYAN,
                                        size=11,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Icon(ft.Icons.EVENT_AVAILABLE_ROUNDED, color=ACCENT_CYAN, size=15),
                                ],
                            ),
                        ),
                        ft.Divider(height=1, color=BORDER_COLOR),
                        ft.Column(
                            controls=stats_cards,
                            spacing=8,
                            scroll=ft.ScrollMode.AUTO,
                            tight=True,
                        ),
                    ],
                    spacing=8,
                    tight=True,
                ),
                width=340,
                height=320 if len(students_stats) > 2 else None,
                padding=4,
            ),
            bgcolor=CARD_BG,
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.ElevatedButton(
                    content=ft.Text("بستن", color=TEXT_WHITE, size=12),
                    bgcolor=PURPLE_DARK,
                    on_click=close_stats_dlg,
                ),
            ],
        )

        pg.overlay.append(stats_dialog)
        stats_dialog.open = True
        pg.update()

    def build_status_badge(self, student_id, title, status_key, color, icon):
        """دکمه وضعیت با طراحی ریسپانسیو و منعطف"""
        current_status = self.attendance_map.get((self.selected_date_str, student_id))
        is_selected = (current_status == status_key)

        bg = color if is_selected else "#141E33"
        txt_color = TEXT_WHITE if is_selected else TEXT_MUTED
        border = ft.Border.all(1.2, color if is_selected else BORDER_COLOR)

        return ft.Container(
            expand=True,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=3,
                tight=True,
                controls=[
                    ft.Icon(icon, size=13, color=txt_color),
                    ft.Text(
                        title,
                        size=10,
                        weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                        color=txt_color,
                    ),
                ],
            ),
            padding=ft.Padding(left=4, right=4, top=6, bottom=6),
            border_radius=16,
            bgcolor=bg,
            border=border,
            on_click=lambda e: self.set_attendance(student_id, status_key),
        )

    def parse_student_row(self, student):
        s_id = None
        s_name = None
        s_phone = None

        if isinstance(student, (dict, sqlite3.Row)):
            try:
                s_id = student["id"]
            except Exception:
                s_id = getattr(student, "id", None)

            try:
                s_name = student["full_name"]
            except Exception:
                try:
                    s_name = student["name"]
                except Exception:
                    s_name = getattr(student, "full_name", getattr(student, "name", None))

            try:
                s_phone = student["phone"]
            except Exception:
                s_phone = getattr(student, "phone", None)

        elif isinstance(student, (list, tuple)):
            s_id = student[0]
            if len(student) == 3:
                s_name = str(student[1])
                s_phone = str(student[2])
            elif len(student) >= 4:
                # اگر آیتم دوم آیدی کلاس بود (id, class_id, name, phone)
                if isinstance(student[1], (int, float)) or (isinstance(student[1], str) and str(student[1]).isdigit() and len(str(student[1])) < 6):
                    s_name = str(student[2]) if len(student) > 2 else ""
                    s_phone = str(student[3]) if len(student) > 3 else ""
                else:
                    s_name = str(student[1])
                    s_phone = str(student[2]) if len(student) > 2 else ""
        else:
            s_id = getattr(student, "id", None)
            s_name = getattr(student, "full_name", None) or getattr(student, "name", None)
            s_phone = getattr(student, "phone", None)

        if not s_name or str(s_name).strip() in ("", "None"):
            s_name = f"هنرجو کد {s_id}" if s_id else "هنرجوی بدون نام"
        if not s_phone or str(s_phone).strip() in ("", "None"):
            s_phone = "ندارد"

        return s_id, str(s_name), str(s_phone)

    def create_student_card(self, student):
        """کارت نمایش هر هنرجو"""
        s_id, s_name, s_phone = self.parse_student_row(student)

        return ft.Container(
            bgcolor=CARD_BG,
            border_radius=10,
            padding=10,
            border=ft.Border.all(1, BORDER_COLOR),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                icon_color=ft.Colors.RED_400,
                                icon_size=20,
                                tooltip="حذف هنرجو",
                                on_click=lambda e, sid=s_id, sname=s_name: self.confirm_delete_student_dialog(
                                    sid, sname
                                ),
                            ),
                            ft.Row(
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                tight=True,
                                controls=[
                                    ft.Column(
                                        spacing=1,
                                        horizontal_alignment=ft.CrossAxisAlignment.END,
                                        tight=True,
                                        controls=[
                                            ft.Text(
                                                s_name,
                                                size=13,
                                                weight=ft.FontWeight.BOLD,
                                                color=TEXT_WHITE,
                                            ),
                                            ft.Text(
                                                f"شماره: {s_phone}",
                                                size=10,
                                                color=TEXT_MUTED,
                                            ),
                                        ],
                                    ),
                                    ft.CircleAvatar(
                                        radius=16,
                                        bgcolor="rgba(0, 180, 216, 0.15)",
                                        content=ft.Icon(
                                            ft.Icons.PERSON_ROUNDED,
                                            color=ACCENT_CYAN,
                                            size=16,
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color="rgba(255, 255, 255, 0.06)"),
                    ft.Row(
                        spacing=6,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            self.build_status_badge(
                                s_id, "غیبت موجه", "justified", COLOR_EXCUSED, ft.Icons.ACCESS_TIME_ROUNDED
                            ),
                            self.build_status_badge(
                                s_id, "غیبت", "unexcused", COLOR_ABSENT, ft.Icons.CANCEL_OUTLINED
                            ),
                            self.build_status_badge(
                                s_id, "حاضر", "present", COLOR_PRESENT, ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED
                            ),
                        ],
                    ),
                ],
            ),
        )

    def build_page_content(self):
        """چیدمان ریسپانسیو کلی صفحه"""
        return ft.Column(
            spacing=0,
            expand=True,
            controls=[
                self.build_header(),
                self.build_date_and_days_section(),
                self.build_actions_bar(),
                ft.Container(
                    expand=True,
                    padding=ft.Padding(left=12, right=12, top=2, bottom=12),
                    content=self.students_column,
                ),
            ],
        )

    def load_students(self, refresh=True):
        self.students_column.controls.clear()

        students = []
        try:
            students = self.db.get_students_by_class(self.class_id) or []
        except Exception:
            pass

        if not students:
            try:
                conn = sqlite3.connect(DB_NAME)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                try:
                    cur.execute(
                        "SELECT id, class_id, full_name, phone FROM students WHERE class_id = ? ORDER BY id ASC",
                        (self.class_id,)
                    )
                except Exception:
                    cur.execute(
                        "SELECT id, class_id, name AS full_name, phone FROM students WHERE class_id = ? ORDER BY id ASC",
                        (self.class_id,)
                    )
                students = cur.fetchall()
                conn.close()
            except Exception:
                pass

        if not students:
            self.students_column.controls.append(
                ft.Container(
                    alignment=ft.Alignment(0, 0),
                    padding=30,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(
                                ft.Icons.PERSON_OFF_OUTLINED,
                                size=36,
                                color=TEXT_MUTED,
                            ),
                            ft.Text(
                                "هنوز هنرجویی برای این کلاس ثبت نشده است",
                                color=TEXT_MUTED,
                                size=12,
                            ),
                        ],
                    ),
                )
            )
        else:
            for s in students:
                self.students_column.controls.append(self.create_student_card(s))

        if refresh:
            pg = self.get_active_page()
            if pg:
                pg.update()

    def open_add_student_dialog(self, e=None):
        pg = self.get_active_page()
        if not pg:
            return

        self.student_name_input.value = ""
        self.student_phone_input.value = ""

        def close_dlg(ev=None):
            dialog.open = False
            pg.update()

        def do_save(ev=None):
            name = (self.student_name_input.value or "").strip()
            phone = (self.student_phone_input.value or "").strip()

            if not name:
                return

            saved = False
            try:
                self.db.add_student(self.class_id, name, phone)
                saved = True
            except Exception:
                pass

            if not saved:
                try:
                    conn = sqlite3.connect(DB_NAME)
                    cur = conn.cursor()
                    try:
                        cur.execute(
                            "INSERT INTO students (class_id, full_name, phone) VALUES (?, ?, ?)",
                            (self.class_id, name, phone),
                        )
                    except Exception:
                        cur.execute(
                            "INSERT INTO students (class_id, name, phone) VALUES (?, ?, ?)",
                            (self.class_id, name, phone),
                        )
                    conn.commit()
                    conn.close()
                except Exception:
                    pass

            close_dlg()
            self.load_students(refresh=True)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "افزودن هنرجوی جدید",
                weight=ft.FontWeight.BOLD,
                color=TEXT_WHITE,
                size=14,
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        self.student_name_input,
                        self.student_phone_input,
                    ],
                    spacing=10,
                    tight=True,
                ),
                width=300,
                padding=4,
            ),
            bgcolor=CARD_BG,
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton(
                    content=ft.Text("انصراف", color=TEXT_MUTED, size=12),
                    on_click=close_dlg,
                ),
                ft.ElevatedButton(
                    content=ft.Text(
                        "ثبت هنرجو",
                        color=TEXT_WHITE,
                        weight=ft.FontWeight.BOLD,
                        size=12,
                    ),
                    bgcolor=PURPLE_DARK,
                    on_click=do_save,
                ),
            ],
        )

        pg.overlay.append(dialog)
        dialog.open = True
        pg.update()

    def confirm_delete_student_dialog(self, student_id, student_name):
        pg = self.get_active_page()
        if not pg:
            return

        def do_close(e=None):
            delete_dialog.open = False
            pg.update()

        def do_delete(e=None):
            deleted = False
            try:
                self.db.delete_student(student_id)
                deleted = True
            except Exception:
                pass

            if not deleted:
                try:
                    conn = sqlite3.connect(DB_NAME)
                    cur = conn.cursor()
                    cur.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
                    cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
                    conn.commit()
                    conn.close()
                except Exception:
                    pass

            do_close()
            self.load_students(refresh=True)

        delete_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "تأیید حذف هنرجو",
                weight=ft.FontWeight.BOLD,
                color=TEXT_WHITE,
                size=14,
            ),
            content=ft.Text(
                f"آیا از حذف هنرجو «{student_name}» مطمئن هستید؟",
                color=TEXT_WHITE,
                size=13,
            ),
            bgcolor=CARD_BG,
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton(
                    content=ft.Text("انصراف", color=TEXT_MUTED, size=12),
                    on_click=do_close,
                ),
                ft.ElevatedButton(
                    content=ft.Text(
                        "حذف قطعی",
                        color=TEXT_WHITE,
                        weight=ft.FontWeight.BOLD,
                        size=12,
                    ),
                    bgcolor=ft.Colors.RED_600,
                    on_click=do_delete,
                ),
            ],
        )

        pg.overlay.append(delete_dialog)
        delete_dialog.open = True
        pg.update()

    def handle_back(self, e=None):
        pg = self.get_active_page()
        if callable(self.on_back):
            self.on_back()
            if pg:
                pg.update()
        elif pg:
            pg.go("/classes")
            pg.update()
