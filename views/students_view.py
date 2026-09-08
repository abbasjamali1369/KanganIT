import os
import json
from datetime import datetime, timedelta
import flet as ft
import jdatetime

from database import (
    add_student,
    delete_student,
    get_attendance_by_date,
    get_class_attendance_report,
    get_class_held_dates,
    set_attendance,
)


class StudentsView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        class_id: int,
        class_title: str,
        on_back=None,
    ):
        super().__init__()

        self.app_page = page
        self.class_id = class_id
        self.class_title = class_title
        self.on_back = on_back

        self.expand = True
        self.padding = ft.Padding(8, 8, 8, 8)

        # تاریخ انتخابی (پیش‌فرض: امروز)
        self.selected_date = datetime.now()
        self.current_date = self.selected_date.strftime("%Y-%m-%d")

        # لیبل تاریخ شمسی
        self.date_label = ft.Text(
            self.get_shamsi_text(),
            size=13,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.CYAN_200,
            text_align=ft.TextAlign.CENTER,
        )

        self.students_column = ft.Column(
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        self.report_list_column = ft.Column(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )

        self.held_dates_column = ft.Column(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )

        self.name_input = ft.TextField(
            label="نام و نام خانوادگی هنرجو",
            border_color=ft.Colors.CYAN_400,
            text_align=ft.TextAlign.RIGHT,
            autofocus=True,
            rtl=True,
        )

        self.phone_input = ft.TextField(
            label="شماره تماس اختیاری",
            border_color=ft.Colors.CYAN_400,
            text_align=ft.TextAlign.RIGHT,
            keyboard_type=ft.KeyboardType.PHONE,
            rtl=True,
        )

        # دیالوگ افزودن هنرجو
        self.add_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "افزودن هنرجوی جدید",
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.RIGHT,
            ),
            content=ft.Column(
                controls=[
                    self.name_input,
                    self.phone_input,
                ],
                tight=True,
                spacing=10,
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("انصراف"),
                    on_click=self.close_dialog,
                ),
                ft.ElevatedButton(
                    content=ft.Text("ذخیره"),
                    on_click=self.save_new_student,
                    bgcolor=ft.Colors.CYAN_700,
                    color=ft.Colors.WHITE,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # دیالوگ گزارش آماری (فقط نمایش آمار در اپلیکیشن)
        self.report_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                controls=[
                    ft.Text(
                        "📊 گزارش آماری کلاس",
                        weight=ft.FontWeight.BOLD,
                        size=16,
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
            ),
            content=ft.Container(
                content=self.report_list_column,
                width=340,
                height=380,
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("بستن"),
                    on_click=self.close_report_dialog,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # دیالوگ جلسات برگزار شده
        self.dates_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "📅 تاریخچه جلسات کلاس",
                weight=ft.FontWeight.BOLD,
                size=16,
                text_align=ft.TextAlign.RIGHT,
            ),
            content=ft.Container(
                content=self.held_dates_column,
                width=320,
                height=350,
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("بستن"),
                    on_click=self.close_dates_dialog,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.content = self.build_page_content()
        self.load_students()

    def get_shamsi_text(self):
        try:
            shamsi_date = jdatetime.date.fromgregorian(
                date=self.selected_date.date()
            )
            weekdays = {
                0: "دوشنبه",
                1: "سه‌شنبه",
                2: "چهارشنبه",
                3: "پنج‌شنبه",
                4: "جمعه",
                5: "شنبه",
                6: "یکشنبه",
            }
            day_name = weekdays.get(self.selected_date.weekday(), "")
            return f"{day_name} {shamsi_date.strftime('%Y/%m/%d')}"
        except Exception:
            return self.current_date

    def prev_day(self, e):
        self.selected_date -= timedelta(days=1)
        self.current_date = self.selected_date.strftime("%Y-%m-%d")
        self.date_label.value = self.get_shamsi_text()
        self.load_students()

    def next_day(self, e):
        self.selected_date += timedelta(days=1)
        self.current_date = self.selected_date.strftime("%Y-%m-%d")
        self.date_label.value = self.get_shamsi_text()
        self.load_students()

    def go_today(self, e):
        self.selected_date = datetime.now()
        self.current_date = self.selected_date.strftime("%Y-%m-%d")
        self.date_label.value = self.get_shamsi_text()
        self.load_students()

    def build_page_content(self):
        options_menu = ft.PopupMenuButton(
            icon=ft.Icons.MORE_VERT_ROUNDED,
            icon_color=ft.Colors.WHITE,
            tooltip="عملیات کلاس",
            items=[
                ft.PopupMenuItem(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.PERSON_ADD_ROUNDED, color=ft.Colors.CYAN_300, size=20),
                            ft.Text("افزودن هنرجو", size=13),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    on_click=self.open_add_dialog,
                ),
                ft.PopupMenuItem(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, color=ft.Colors.PURPLE_300, size=20),
                            ft.Text("تاریخچه جلسات برگزار شده", size=13),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    on_click=self.open_dates_dialog,
                ),
                ft.PopupMenuItem(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ANALYTICS_ROUNDED, color=ft.Colors.AMBER_300, size=20),
                            ft.Text("گزارش و درصد حضور", size=13),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    on_click=self.open_report_dialog,
                ),
            ],
        )

        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.ARROW_FORWARD_IOS_ROUNDED,
                                icon_color=ft.Colors.GREY_300,
                                tooltip="بازگشت",
                                on_click=self.handle_back,
                            ),
                            options_menu,
                        ],
                        spacing=4,
                    ),
                    ft.Text(
                        self.class_title,
                        size=17,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                        text_align=ft.TextAlign.RIGHT,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(4, 4, 4, 4),
        )

        date_bar = ft.Container(
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_LEFT_ROUNDED,
                        icon_color=ft.Colors.CYAN_300,
                        tooltip="روز بعد",
                        on_click=self.next_day,
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.CALENDAR_TODAY_ROUNDED,
                                    size=15,
                                    color=ft.Colors.CYAN_200,
                                ),
                                self.date_label,
                            ],
                            spacing=6,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        on_click=self.go_today,
                        tooltip="کلیک برای برگشت به امروز",
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_RIGHT_ROUNDED,
                        icon_color=ft.Colors.CYAN_300,
                        tooltip="روز قبل",
                        on_click=self.prev_day,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.GREY_900,
            border_radius=8,
            padding=ft.Padding(4, 2, 4, 2),
        )

        legend = ft.Container(
            content=ft.Row(
                controls=[
                    self.build_legend_badge("حاضر", ft.Colors.GREEN_400),
                    self.build_legend_badge("موجه", ft.Colors.AMBER_400),
                    self.build_legend_badge("غیرموجه", ft.Colors.RED_400),
                ],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            ),
            bgcolor=ft.Colors.GREY_900,
            border_radius=8,
            padding=ft.Padding(8, 6, 8, 6),
        )

        return ft.Column(
            controls=[
                header,
                date_bar,
                legend,
                ft.Divider(
                    color=ft.Colors.GREY_800,
                    thickness=1,
                    height=1,
                ),
                self.students_column,
            ],
            expand=True,
            spacing=8,
        )

    def build_legend_badge(self, title: str, color: str):
        return ft.Row(
            controls=[
                ft.Container(
                    width=8,
                    height=8,
                    bgcolor=color,
                    border_radius=4,
                ),
                ft.Text(
                    title,
                    size=11,
                    color=ft.Colors.GREY_300,
                ),
            ],
            spacing=5,
        )

    def load_students(self):
        self.students_column.controls.clear()

        records = get_attendance_by_date(
            self.class_id,
            self.current_date,
        )

        if not records:
            self.students_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.PEOPLE_OUTLINE_ROUNDED,
                                size=48,
                                color=ft.Colors.GREY_600,
                            ),
                            ft.Text(
                                "هنوز هیچ هنرجویی در این کلاس ثبت نشده است.",
                                size=13,
                                color=ft.Colors.GREY_400,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "از منوی سه‌نقطه بالای صفحه هنرجو اضافه کنید.",
                                size=11,
                                color=ft.Colors.GREY_600,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.Padding(20, 30, 20, 30),
                )
            )
        else:
            for row in records:
                self.students_column.controls.append(
                    self.create_student_card(row)
                )

        self.update_page()

    def create_student_card(self, row):
        student_id = row["student_id"]
        full_name = row["full_name"]
        phone = row["phone"] or "بدون شماره"
        current_status = row["status"]

        allowed_statuses = [
            "present",
            "justified",
            "unexcused",
        ]

        if current_status not in allowed_statuses:
            current_status = "unexcused"

        def make_status_btn(
            title: str,
            status_key: str,
            active_color,
            active_icon,
        ):
            is_active = current_status == status_key

            return ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            active_icon
                            if is_active
                            else ft.Icons.RADIO_BUTTON_UNCHECKED,
                            size=15,
                            color=(
                                ft.Colors.WHITE
                                if is_active
                                else ft.Colors.GREY_500
                            ),
                        ),
                        ft.Text(
                            title,
                            size=12,
                            weight=(
                                ft.FontWeight.BOLD
                                if is_active
                                else ft.FontWeight.NORMAL
                            ),
                            color=(
                                ft.Colors.WHITE
                                if is_active
                                else ft.Colors.GREY_400
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=4,
                ),
                bgcolor=(
                    active_color
                    if is_active
                    else ft.Colors.GREY_800
                ),
                border=ft.Border.all(
                    1.5 if is_active else 0.5,
                    active_color
                    if is_active
                    else ft.Colors.GREY_700,
                ),
                border_radius=8,
                padding=ft.Padding(6, 6, 6, 6),
                expand=True,
                on_click=lambda _: self.change_attendance(
                    student_id,
                    status_key,
                ),
            )

        status_buttons = ft.Row(
            controls=[
                make_status_btn(
                    "حاضر",
                    "present",
                    ft.Colors.GREEN_700,
                    ft.Icons.CHECK_CIRCLE_ROUNDED,
                ),
                make_status_btn(
                    "موجه",
                    "justified",
                    ft.Colors.AMBER_800,
                    ft.Icons.WARNING_ROUNDED,
                ),
                make_status_btn(
                    "غیرموجه",
                    "unexcused",
                    ft.Colors.RED_800,
                    ft.Icons.CANCEL_ROUNDED,
                ),
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        top_info = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                            icon_color=ft.Colors.RED_400,
                            icon_size=18,
                            tooltip="حذف هنرجو",
                            on_click=lambda _: self.remove_student(student_id),
                        ),
                        ft.Text(
                            phone,
                            size=11,
                            color=ft.Colors.GREY_400,
                        ),
                    ],
                    spacing=2,
                ),
                ft.Text(
                    full_name,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.RIGHT,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.Container(
            bgcolor=ft.Colors.GREY_900,
            border_radius=10,
            padding=ft.Padding(10, 8, 10, 8),
            border=ft.Border.all(0.8, ft.Colors.GREY_800),
            content=ft.Column(
                controls=[
                    top_info,
                    ft.Divider(
                        color=ft.Colors.GREY_800,
                        height=1,
                        thickness=0.8,
                    ),
                    status_buttons,
                ],
                spacing=6,
            ),
        )

    def open_dates_dialog(self, event=None):
        self.held_dates_column.controls.clear()

        try:
            dates = get_class_held_dates(self.class_id)
        except Exception as error:
            self.show_snack(
                f"خطا در دریافت تاریخ‌ها: {error}",
                ft.Colors.RED_700,
            )
            return

        if not dates:
            self.held_dates_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.EVENT_BUSY_ROUNDED,
                                size=36,
                                color=ft.Colors.GREY_600,
                            ),
                            ft.Text(
                                "هنوز جلسه‌ای برای این کلاس ثبت نشده است.",
                                color=ft.Colors.GREY_400,
                                size=12,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.Padding(10, 20, 10, 20),
                )
            )
        else:
            weekdays = {
                0: "دوشنبه",
                1: "سه‌شنبه",
                2: "چهارشنبه",
                3: "پنج‌شنبه",
                4: "جمعه",
                5: "شنبه",
                6: "یکشنبه",
            }

            total = len(dates)
            for index, d_str in enumerate(dates):
                session_num = total - index
                is_current = (d_str == self.current_date)

                try:
                    dt = datetime.strptime(d_str, "%Y-%m-%d")
                    shamsi_obj = jdatetime.date.fromgregorian(date=dt.date())
                    shamsi_formatted = shamsi_obj.strftime("%Y/%m/%d")
                    day_name = weekdays.get(dt.weekday(), "")
                except Exception:
                    shamsi_formatted = d_str
                    day_name = ""

                self.held_dates_column.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.CHECK_CIRCLE_ROUNDED if is_current else ft.Icons.CALENDAR_TODAY_ROUNDED,
                                            size=16,
                                            color=ft.Colors.CYAN_300 if is_current else ft.Colors.PURPLE_300,
                                        ),
                                        ft.Text(
                                            f"جلسه {session_num}",
                                            size=13,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.WHITE,
                                        ),
                                    ],
                                    spacing=6,
                                ),
                                ft.Text(
                                    f"{day_name} {shamsi_formatted}",
                                    size=12,
                                    color=ft.Colors.CYAN_200 if is_current else ft.Colors.GREY_300,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        bgcolor=ft.Colors.CYAN_900 if is_current else ft.Colors.GREY_900,
                        border=ft.Border.all(1, ft.Colors.CYAN_500 if is_current else ft.Colors.GREY_800),
                        border_radius=8,
                        padding=ft.Padding(12, 10, 12, 10),
                        on_click=lambda _, target=d_str: self.set_specific_date(target),
                        tooltip="رفتن به این جلسه",
                    )
                )

        if self.dates_dialog not in self.app_page.overlay:
            self.app_page.overlay.append(self.dates_dialog)

        self.dates_dialog.open = True
        self.update_page()

    def close_dates_dialog(self, event=None):
        self.dates_dialog.open = False
        self.update_page()

    def set_specific_date(self, date_str: str):
        try:
            self.selected_date = datetime.strptime(date_str, "%Y-%m-%d")
            self.current_date = date_str
            self.date_label.value = self.get_shamsi_text()
            self.dates_dialog.open = False
            self.load_students()
        except Exception as error:
            self.show_snack(f"خطا در تغییر تاریخ: {error}", ft.Colors.RED_700)

    def open_report_dialog(self, event=None):
        self.report_list_column.controls.clear()

        try:
            report = get_class_attendance_report(self.class_id)
        except Exception as error:
            self.show_snack(
                f"خطا در دریافت آمار: {error}",
                ft.Colors.RED_700,
            )
            return

        total_sessions = report["total_sessions"]

        self.report_list_column.controls.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(
                            f"مجموع جلسات: {total_sessions}",
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.CYAN_300,
                        ),
                        ft.Icon(
                            ft.Icons.EVENT_NOTE_ROUNDED,
                            color=ft.Colors.CYAN_300,
                            size=18,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor=ft.Colors.BLUE_GREY_900,
                padding=ft.Padding(10, 8, 10, 8),
                border_radius=8,
            )
        )

        if not report["students"]:
            self.report_list_column.controls.append(
                ft.Text(
                    "هنوز هنرجویی وجود ندارد.",
                    color=ft.Colors.GREY_400,
                    size=12,
                    text_align=ft.TextAlign.CENTER,
                )
            )
        else:
            for st in report["students"]:
                percent = st["percent"]

                if percent >= 75:
                    progress_color = ft.Colors.GREEN_400
                elif percent >= 50:
                    progress_color = ft.Colors.AMBER_400
                else:
                    progress_color = ft.Colors.RED_400

                self.report_list_column.controls.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            f"{percent}%",
                                            size=13,
                                            weight=ft.FontWeight.BOLD,
                                            color=progress_color,
                                        ),
                                        ft.Text(
                                            st["full_name"],
                                            size=13,
                                            weight=ft.FontWeight.W_600,
                                            color=ft.Colors.WHITE,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.ProgressBar(
                                    value=(
                                        percent / 100
                                        if percent > 0
                                        else 0
                                    ),
                                    color=progress_color,
                                    bgcolor=ft.Colors.GREY_800,
                                    height=6,
                                    border_radius=3,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            f"غیرموجه: {st['unexcused']}",
                                            size=11,
                                            color=ft.Colors.RED_300,
                                        ),
                                        ft.Text(
                                            f"موجه: {st['justified']}",
                                            size=11,
                                            color=ft.Colors.AMBER_300,
                                        ),
                                        ft.Text(
                                            f"حاضر: {st['present']}",
                                            size=11,
                                            color=ft.Colors.GREEN_300,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                            ],
                            spacing=5,
                        ),
                        bgcolor=ft.Colors.GREY_900,
                        border_radius=8,
                        padding=ft.Padding(8, 8, 8, 8),
                    )
                )

        if self.report_dialog not in self.app_page.overlay:
            self.app_page.overlay.append(self.report_dialog)

        self.report_dialog.open = True
        self.update_page()

    def close_report_dialog(self, event=None):
        self.report_dialog.open = False
        self.update_page()

    def change_attendance(self, student_id: int, status: str):
        if status not in [
            "present",
            "justified",
            "unexcused",
        ]:
            return

        try:
            set_attendance(
                student_id,
                self.current_date,
                status,
            )

            label_map = {
                "present": "حاضر",
                "justified": "موجه",
                "unexcused": "غیرموجه",
            }

            self.load_students()

            self.show_snack(
                f"وضعیت به «{label_map.get(status, status)}» ثبت شد",
                ft.Colors.GREEN_700,
            )
        except Exception as error:
            self.show_snack(
                f"خطا در ثبت: {error}",
                ft.Colors.RED_700,
            )

    def open_add_dialog(self, event=None):
        self.name_input.value = ""
        self.phone_input.value = ""
        self.name_input.error_text = None
        self.phone_input.error_text = None

        if self.add_dialog not in self.app_page.overlay:
            self.app_page.overlay.append(self.add_dialog)

        self.add_dialog.open = True
        self.update_page()

    def close_dialog(self, event=None):
        self.add_dialog.open = False
        self.update_page()

    def save_new_student(self, event=None):
        name = self.name_input.value.strip()
        phone = self.phone_input.value.strip()

        if not name:
            self.name_input.error_text = "نام هنرجو الزامی است"
            self.update_page()
            return

        try:
            add_student(
                class_id=self.class_id,
                full_name=name,
                phone=phone,
            )
            self.close_dialog()
            self.load_students()
            self.show_snack(
                f"هنرجو «{name}» با موفقیت افزوده شد.",
                ft.Colors.GREEN_700,
            )
        except Exception as error:
            self.show_snack(
                f"خطا در افزودن: {error}",
                ft.Colors.RED_700,
            )

    def remove_student(self, student_id: int):
        try:
            delete_student(student_id)
            self.load_students()
            self.show_snack(
                "هنرجو با موفقیت حذف شد.",
                ft.Colors.RED_700,
            )
        except Exception as error:
            self.show_snack(
                f"خطا در حذف: {error}",
                ft.Colors.RED_700,
            )

    def handle_back(self, event=None):
        if self.on_back:
            self.on_back()

    def show_snack(self, message: str, color):
        self.app_page.snack_bar = ft.SnackBar(
            content=ft.Text(
                message,
                text_align=ft.TextAlign.RIGHT,
            ),
            bgcolor=color,
            duration=1200,
        )

        self.app_page.snack_bar.open = True
        self.update_page()

    def update_page(self):
        if self.app_page:
            self.app_page.update()
