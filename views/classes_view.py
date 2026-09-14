import inspect
import flet as ft
from database import Database

# --- پالت رنگی ---
NAVY_HEADER = "#0D1B2A"
BG_MAIN = "#0B132B"
CARD_BG = "#1C2541"
TEXT_WHITE = "#FFFFFF"
TEXT_MUTED = "#8D99AE"
PURPLE_START = "#7B2CBF"
PURPLE_END = "#5A189A"
PURPLE_DARK = "#480CA8"
ACCENT_GREEN = "#2EC4B6"
ACCENT_CYAN = "#00B4D8"
BORDER_COLOR = "#3A506B"
DANGER_RED = "#EF476F"


class ClassesView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        on_select_class=None,
        on_logout=None,
    ):
        super().__init__(expand=True)

        self._current_page = page
        self.on_select_class = on_select_class
        self.on_logout = on_logout
        self.db = Database()
        self.bgcolor = BG_MAIN

        # لیست نگه‌دارنده کارت‌ها
        self.classes_column = ft.Column(
            spacing=14,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        # فیلدهای دیالوگ افزودن کلاس
        self.class_name_input = ft.TextField(
            label="نام دوره / کلاس",
            border_color=BORDER_COLOR,
            focused_border_color=PURPLE_START,
            color=TEXT_WHITE,
            text_align=ft.TextAlign.RIGHT,
        )

        self.teacher_name_input = ft.TextField(
            label="نام مدرس",
            border_color=BORDER_COLOR,
            focused_border_color=PURPLE_START,
            color=TEXT_WHITE,
            text_align=ft.TextAlign.RIGHT,
        )

        # ساخت رابط کاربری
        self.content = self.build_ui()

        # بارگذاری دوره‌ها
        self.load_classes(refresh=False)

    def get_active_page(self):
        """یافتن صفحه فعال برای باز کردن پاپ‌آپ‌ها و آپدیت"""
        return self._current_page or getattr(self, "page", None)

    def safe_delete_class(self, class_id):
        """حذف ایمن کلاس با سازگاری کامل با متدهای مختلف database.py"""
        if not hasattr(self.db, "delete_class"):
            return False

        method = getattr(self.db, "delete_class")
        try:
            sig = inspect.signature(method)
            params_count = len(sig.parameters)
            if params_count >= 1:
                method(class_id)
            else:
                method()
            return True
        except Exception:
            try:
                method(class_id)
                return True
            except Exception as err:
                print(f"Error deleting class: {err}")
                return False

    def build_top_navy_bar(self):
        """نوار اطلاعات بالای صفحه (اطلاعات تماس و اینستاگرام تمیز و مرتب)"""
        return ft.Container(
            bgcolor=NAVY_HEADER,
            padding=ft.Padding(
                left=16,
                right=16,
                top=8,
                bottom=8,
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=6,
                        controls=[
                            ft.Icon(
                                ft.Icons.CAMERA_ALT_OUTLINED,
                                size=14,
                                color="#E1306C",
                            ),
                            ft.Text(
                                "kanganit_academy",
                                size=11,
                                color=TEXT_WHITE,
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=6,
                        controls=[
                            ft.Icon(
                                ft.Icons.CALL,
                                size=14,
                                color=ACCENT_GREEN,
                            ),
                            ft.Text(
                                "09914621788",
                                size=11,
                                color=TEXT_WHITE,
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                    ),
                ],
            ),
        )

    def build_profile_header(self):
        """هدر مشخصات آموزشگاه همراه با دکمه خروج دقیقا زیر لوگو"""
        return ft.Container(
            padding=ft.Padding(
                left=16,
                right=16,
                top=12,
                bottom=6,
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # دکمه کلاس جدید
                    ft.ElevatedButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.ADD_CIRCLE_OUTLINE,
                                    color=TEXT_WHITE,
                                    size=18,
                                ),
                                ft.Text(
                                    "کلاس جدید",
                                    color=TEXT_WHITE,
                                    weight=ft.FontWeight.BOLD,
                                    size=13,
                                ),
                            ],
                            spacing=6,
                            tight=True,
                        ),
                        bgcolor=PURPLE_DARK,
                        height=42,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        on_click=self.open_add_dialog,
                    ),
                    # مشخصات آموزشگاه + لوگو و دکمه خروج دقیقا زیر لوگو
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=3,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                controls=[
                                    ft.Text(
                                        "آموزشگاه ارتباطات هوشمند",
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_WHITE,
                                    ),
                                    ft.Text(
                                        "مدیریت دوره‌ها و حضور غیاب",
                                        size=12,
                                        color=TEXT_MUTED,
                                    ),
                                ],
                            ),
                            # ستون شامل لوگو و دکمه خروج قرمز زیر آن
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                                controls=[
                                    ft.CircleAvatar(
                                        radius=22,
                                        bgcolor=PURPLE_START,
                                        content=ft.Icon(
                                            ft.Icons.SCHOOL,
                                            color=TEXT_WHITE,
                                            size=22,
                                        ),
                                    ),
                                    # دکمه خروج دقیقاً زیر لوگو
                                    ft.Container(
                                        content=ft.Row(
                                            spacing=3,
                                            tight=True,
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.LOGOUT_ROUNDED,
                                                    size=12,
                                                    color=ft.Colors.WHITE,
                                                ),
                                                ft.Text(
                                                    "خروج",
                                                    size=10,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=ft.Colors.WHITE,
                                                ),
                                            ],
                                        ),
                                        bgcolor=DANGER_RED,
                                        padding=ft.Padding(left=7, right=7, top=3, bottom=3),
                                        border_radius=7,
                                        ink=True,
                                        tooltip="خروج از حساب کاربری",
                                        on_click=self.confirm_logout_dialog,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        )

    def get_classes_count(self):
        try:
            return len(self.db.get_all_classes() or [])
        except Exception:
            return 0

    def get_students_count(self):
        if not hasattr(self.db, "get_all_students"):
            return 0
        try:
            return len(self.db.get_all_students() or [])
        except Exception:
            return 0

    def build_stats_cards(self):
        """کارت‌های آمار و کارت درباره ما"""
        classes_count = self.get_classes_count()
        students_count = self.get_students_count()

        classes_card = ft.Container(
            expand=True,
            height=90,
            padding=12,
            border_radius=14,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[
                    PURPLE_START,
                    PURPLE_END,
                ],
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.MENU_BOOK_ROUNDED,
                            size=26,
                            color=TEXT_WHITE,
                        ),
                        bgcolor="rgba(255, 255, 255, 0.15)",
                        padding=8,
                        border_radius=10,
                    ),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=2,
                        controls=[
                            ft.Text(
                                str(classes_count),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT_WHITE,
                            ),
                            ft.Text(
                                "دوره‌های فعال",
                                size=11,
                                color=TEXT_WHITE,
                            ),
                        ],
                    ),
                ],
            ),
        )

        students_card = ft.Container(
            expand=True,
            height=90,
            padding=12,
            border_radius=14,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[
                    PURPLE_END,
                    PURPLE_DARK,
                ],
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.PEOPLE_ALT_ROUNDED,
                            size=26,
                            color=TEXT_WHITE,
                        ),
                        bgcolor="rgba(255, 255, 255, 0.15)",
                        padding=8,
                        border_radius=10,
                    ),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=2,
                        controls=[
                            ft.Text(
                                str(students_count),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT_WHITE,
                            ),
                            ft.Text(
                                "هنرجویان ثبت‌شده",
                                size=11,
                                color=TEXT_WHITE,
                            ),
                        ],
                    ),
                ],
            ),
        )

        about_card = ft.Container(
            height=60,
            padding=ft.Padding(left=14, right=14, top=6, bottom=6),
            border_radius=12,
            bgcolor=CARD_BG,
            border=ft.Border.all(1, BORDER_COLOR),
            url="https://kanganit.ir",
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(
                                ft.Icons.OPEN_IN_NEW_ROUNDED,
                                size=16,
                                color=ACCENT_CYAN,
                            ),
                            ft.Text(
                                "kanganit.ir",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=ACCENT_CYAN,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Text(
                                "درباره ما و وب‌سایت رسمی",
                                size=12,
                                weight=ft.FontWeight.W_500,
                                color=TEXT_WHITE,
                            ),
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.LANGUAGE_ROUNDED,
                                    size=18,
                                    color=TEXT_WHITE,
                                ),
                                bgcolor="rgba(0, 180, 216, 0.2)",
                                padding=6,
                                border_radius=8,
                            ),
                        ],
                    ),
                ],
            ),
        )

        return ft.Container(
            padding=ft.Padding(
                left=16,
                right=16,
                top=10,
                bottom=10,
            ),
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        spacing=12,
                        controls=[
                            students_card,
                            classes_card,
                        ],
                    ),
                    about_card,
                ],
            ),
        )

    def show_attendance_stats_dialog(self, class_id, class_name):
        """نمایش پنجره آمار و درصد حضور و غیاب دوره"""
        pg = self.get_active_page()
        if not pg:
            return

        present_count = 0
        absent_count = 0
        excused_count = 0

        try:
            if hasattr(self.db, "get_class_attendance_summary"):
                stats = self.db.get_class_attendance_summary(class_id)
                present_count = stats.get("present", 0)
                absent_count = stats.get("absent", 0)
                excused_count = stats.get("excused", 0)
            elif hasattr(self.db, "get_attendance_by_class"):
                records = self.db.get_attendance_by_class(class_id) or []
                for r in records:
                    status = str(r[3] if len(r) > 3 else "").lower()
                    if "present" in status or "حاضر" in status:
                        present_count += 1
                    elif "excused" in status or "موجه" in status:
                        excused_count += 1
                    elif "absent" in status or "غائب" in status or "غایب" in status:
                        absent_count += 1
        except Exception:
            pass

        total_sessions = present_count + absent_count + excused_count
        attendance_percent = (
            round((present_count / total_sessions) * 100) if total_sessions > 0 else 0
        )

        def close_stats(e=None):
            stats_dialog.open = False
            pg.update()

        stats_dialog = ft.AlertDialog(
            open=True,
            title=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Icon(ft.Icons.INSIGHTS_ROUNDED, color=ACCENT_CYAN, size=22),
                    ft.Text(
                        f"آمار حضور و غیاب: {class_name}",
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_WHITE,
                    ),
                ],
            ),
            content=ft.Container(
                width=340,
                padding=10,
                content=ft.Column(
                    tight=True,
                    spacing=14,
                    controls=[
                        ft.Container(
                            padding=12,
                            border_radius=10,
                            bgcolor="rgba(0, 180, 216, 0.1)",
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(
                                        f"{attendance_percent}%",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=ACCENT_CYAN,
                                    ),
                                    ft.Text(
                                        "میانگین درصد حضور:",
                                        color=TEXT_WHITE,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                            ),
                        ),
                        ft.ProgressBar(
                            value=attendance_percent / 100 if total_sessions > 0 else 0,
                            color=ACCENT_CYAN,
                            bgcolor=BORDER_COLOR,
                            height=8,
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            controls=[
                                ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2,
                                    controls=[
                                        ft.Text(str(present_count), color=ACCENT_GREEN, size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text("حاضر", color=TEXT_MUTED, size=11),
                                    ],
                                ),
                                ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2,
                                    controls=[
                                        ft.Text(str(excused_count), color="#FFB703", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text("موجه", color=TEXT_MUTED, size=11),
                                    ],
                                ),
                                ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2,
                                    controls=[
                                        ft.Text(str(absent_count), color=DANGER_RED, size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text("غایب", color=TEXT_MUTED, size=11),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ),
            bgcolor=CARD_BG,
            actions=[
                ft.TextButton(
                    content=ft.Text("بستن", color=ACCENT_CYAN),
                    on_click=close_stats,
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        pg.overlay.append(stats_dialog)
        pg.update()

    def create_class_card(self, class_record):
        """کارت هر دوره با قابلیت مدیریت، آمار و حذف"""
        class_id = class_record[0]
        class_name = class_record[1]
        teacher_name = (
            class_record[2]
            if len(class_record) > 2 and class_record[2]
            else "تعیین‌نشده"
        )

        return ft.Container(
            bgcolor=CARD_BG,
            border_radius=12,
            padding=14,
            border=ft.Border.all(1, BORDER_COLOR),
            ink=True,
            on_click=lambda e, cid=class_id, cname=class_name: self.go_to_students(
                cid, cname
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=2,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=ft.Colors.RED_400,
                                tooltip="حذف کلاس",
                                on_click=lambda e, cid=class_id, cname=class_name: self.confirm_delete_dialog(
                                    cid, cname
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.BAR_CHART_ROUNDED,
                                icon_color=ACCENT_CYAN,
                                tooltip="درصد و آمار حضور و غیاب",
                                on_click=lambda e, cid=class_id, cname=class_name: self.show_attendance_stats_dialog(
                                    cid, cname
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ARROW_FORWARD_IOS_ROUNDED,
                                icon_color=ACCENT_GREEN,
                                icon_size=18,
                                tooltip="مدیریت هنرجویان و حضور غیاب",
                                on_click=lambda e, cid=class_id, cname=class_name: self.go_to_students(
                                    cid, cname
                                ),
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=3,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                controls=[
                                    ft.Text(
                                        class_name,
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_WHITE,
                                    ),
                                    ft.Row(
                                        spacing=4,
                                        controls=[
                                            ft.Text(
                                                f"مدرس: {teacher_name}",
                                                size=12,
                                                color=TEXT_MUTED,
                                            ),
                                            ft.Icon(
                                                ft.Icons.PERSON_OUTLINE,
                                                size=14,
                                                color=TEXT_MUTED,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Container(
                                width=44,
                                height=44,
                                border_radius=10,
                                bgcolor="rgba(123, 44, 191, 0.2)",
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(
                                    ft.Icons.BOOK_ROUNDED,
                                    color=PURPLE_START,
                                    size=22,
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )

    def build_ui(self):
        """چیدمان کل صفحه"""
        return ft.Column(
            spacing=0,
            expand=True,
            controls=[
                self.build_top_navy_bar(),
                self.build_profile_header(),
                self.build_stats_cards(),
                ft.Container(
                    padding=ft.Padding(
                        left=18,
                        right=18,
                        top=6,
                        bottom=6,
                    ),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        controls=[
                            ft.Text(
                                "لیست دوره‌های آموزشی",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT_WHITE,
                            ),
                            ft.Icon(
                                ft.Icons.LIST_ALT_ROUNDED,
                                size=18,
                                color=PURPLE_START,
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    expand=True,
                    padding=ft.Padding(
                        left=16,
                        right=16,
                        top=0,
                        bottom=10,
                    ),
                    content=self.classes_column,
                ),
            ],
        )

    def load_classes(self, refresh=True):
        """بارگذاری کلاس‌ها و بروزرسانی کل UI"""
        self.classes_column.controls.clear()

        try:
            classes = self.db.get_all_classes() or []
        except Exception:
            classes = []

        if not classes:
            self.classes_column.controls.append(
                ft.Container(
                    alignment=ft.Alignment(0, 0),
                    padding=40,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            ft.Icon(
                                ft.Icons.INVENTORY_2_OUTLINED,
                                size=48,
                                color=TEXT_MUTED,
                            ),
                            ft.Text(
                                "هنوز کلاسی ثبت نشده است",
                                color=TEXT_MUTED,
                                size=14,
                            ),
                        ],
                    ),
                )
            )
        else:
            for class_record in classes:
                self.classes_column.controls.append(
                    self.create_class_card(class_record)
                )

        # بازسازی کامل UI برای بروزشدن کارت‌های آمار بالای صفحه
        self.content = self.build_ui()

        if refresh:
            pg = self.get_active_page()
            if pg:
                pg.update()

    def open_add_dialog(self, e=None):
        """باز کردن دیالوگ افزودن کلاس"""
        pg = self.get_active_page()
        if not pg:
            return

        self.class_name_input.value = ""
        self.teacher_name_input.value = ""

        def close_dialog(ev=None):
            dialog.open = False
            pg.update()

        def do_save(ev=None):
            name = (self.class_name_input.value or "").strip()
            teacher = (self.teacher_name_input.value or "").strip()
            if name:
                self.db.add_class(name, teacher)
                close_dialog()
                self.load_classes(refresh=True)

        dialog = ft.AlertDialog(
            open=True,
            title=ft.Text(
                "افزودن کلاس جدید",
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.RIGHT,
                color=TEXT_WHITE,
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        self.class_name_input,
                        self.teacher_name_input,
                    ],
                    tight=True,
                    spacing=12,
                ),
                width=340,
                padding=10,
            ),
            bgcolor=CARD_BG,
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton(
                    content=ft.Text("انصراف", color=TEXT_MUTED),
                    on_click=close_dialog,
                ),
                ft.ElevatedButton(
                    content=ft.Text(
                        "ذخیره کلاس",
                        color=TEXT_WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                    bgcolor=PURPLE_DARK,
                    on_click=do_save,
                ),
            ],
        )

        pg.overlay.append(dialog)
        pg.update()

    def confirm_logout_dialog(self, e=None):
        """دیالوگ خروج امن و حرفه‌ای"""
        pg = self.get_active_page()
        if not pg:
            return

        def do_close(ev=None):
            logout_dialog.open = False
            pg.update()

        def do_logout(ev=None):
            do_close()
            # پاک کردن سشن
            if pg and hasattr(pg, "session") and pg.session is not None:
                try:
                    if hasattr(pg.session, "clear"):
                        pg.session.clear()
                except Exception:
                    pass

            # در صورتی که تابع خروج اختصاصی ست شده باشد
            if callable(self.on_logout):
                try:
                    self.on_logout()
                    return
                except Exception:
                    pass

            # رفتن به صفحه ورود
            if pg:
                try:
                    pg.go("/login")
                except Exception:
                    try:
                        pg.go("/")
                    except Exception:
                        pass
                pg.update()

        logout_dialog = ft.AlertDialog(
            open=True,
            title=ft.Row(
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=DANGER_RED, size=22),
                    ft.Text("خروج از برنامه", weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                ],
            ),
            content=ft.Text(
                "آیا مطمئن هستید که می‌خواهید از حساب کاربری خود خارج شوید؟",
                color=TEXT_WHITE,
                size=13,
            ),
            bgcolor=CARD_BG,
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton(
                    content=ft.Text("انصراف", color=TEXT_MUTED),
                    on_click=do_close,
                ),
                ft.ElevatedButton(
                    content=ft.Text(
                        "بله، خارج شو",
                        color=TEXT_WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                    bgcolor=DANGER_RED,
                    on_click=do_logout,
                ),
            ],
        )

        pg.overlay.append(logout_dialog)
        pg.update()

    def confirm_delete_dialog(self, class_id, class_name):
        """دیالوگ تأیید حذف کلاس"""
        pg = self.get_active_page()
        if not pg:
            return

        def do_close(e=None):
            delete_dialog.open = False
            pg.update()

        def do_delete(e=None):
            # حذف ایمن با فراخوانی تابع اختصاصی
            self.safe_delete_class(class_id)
            do_close()
            # آپدیت کامل صفحه و کارت‌های آمار
            self.load_classes(refresh=True)

        delete_dialog = ft.AlertDialog(
            open=True,
            title=ft.Text(
                "تأیید حذف",
                weight=ft.FontWeight.BOLD,
                color=TEXT_WHITE,
            ),
            content=ft.Text(
                f"آیا از حذف دوره «{class_name}» و اطلاعات آن مطمئن هستید؟",
                color=TEXT_WHITE,
            ),
            bgcolor=CARD_BG,
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton(
                    content=ft.Text(
                        "انصراف",
                        color=TEXT_MUTED,
                    ),
                    on_click=do_close,
                ),
                ft.ElevatedButton(
                    content=ft.Text(
                        "حذف کلاس",
                        color=TEXT_WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                    bgcolor=ft.Colors.RED_600,
                    on_click=do_delete,
                ),
            ],
        )

        pg.overlay.append(delete_dialog)
        pg.update()

    def go_to_students(self, class_id, class_name):
        """انتقال به صفحه هنرجویان و ذخیره مقادیر سشن"""
        pg = self.get_active_page()

        if pg and hasattr(pg, "session") and pg.session is not None:
            try:
                if hasattr(pg.session, "set"):
                    pg.session.set("selected_class_id", class_id)
                    pg.session.set("selected_class_name", class_name)
                else:
                    pg.session["selected_class_id"] = class_id
                    pg.session["selected_class_name"] = class_name
            except Exception:
                pass

        if callable(self.on_select_class):
            self._call_select_class_callback(class_id, class_name)
            if pg:
                pg.update()
            return

        if pg:
            pg.go("/students")
            pg.update()

    def _call_select_class_callback(self, class_id, class_name):
        """فراخوانی سازگار متد جابجایی صفحه"""
        callback = self.on_select_class
        try:
            signature = inspect.signature(callback)
            params = [
                p
                for p in signature.parameters.values()
                if p.kind
                in (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            ]
            has_var_args = any(
                p.kind == inspect.Parameter.VAR_POSITIONAL
                for p in signature.parameters.values()
            )

            if has_var_args or len(params) >= 2:
                callback(class_id, class_name)
            elif len(params) == 1:
                callback(class_id)
            else:
                callback()
        except (TypeError, ValueError):
            callback(class_id, class_name)
