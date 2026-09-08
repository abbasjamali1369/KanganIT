import flet as ft
from database import get_all_classes, add_class, delete_class

class ClassesView(ft.Container):
    def __init__(self, page: ft.Page, on_select_class=None):
        super().__init__()
        self.app_page = page
        self.on_select_class = on_select_class
        self.expand = True
        self.padding = 16

        self.classes_column = ft.Column(
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        # فیلدهای فرم افزودن کلاس
        self.class_title_input = ft.TextField(
            label="عنوان کلاس (مثال: برنامه‌نویسی پایتون)",
            border_color=ft.Colors.CYAN_400,
            text_align=ft.TextAlign.RIGHT,
            autofocus=True,
        )
        self.class_day_time_input = ft.TextField(
            label="روز و ساعت (اختیاری)",
            border_color=ft.Colors.CYAN_400,
            text_align=ft.TextAlign.RIGHT,
        )
        self.class_teacher_input = ft.TextField(
            label="نام مدرس (اختیاری)",
            border_color=ft.Colors.CYAN_400,
            text_align=ft.TextAlign.RIGHT,
        )

        self.add_dialog = ft.AlertDialog(
            title=ft.Text("افزودن کلاس جدید", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT),
            content=ft.Column(
                [
                    self.class_title_input,
                    self.class_day_time_input,
                    self.class_teacher_input,
                ],
                tight=True,
                spacing=10,
            ),
            actions=[
                ft.TextButton("انصراف", on_click=self.close_dialog, style=ft.ButtonStyle(color=ft.Colors.GREY_400)),
                ft.ElevatedButton("ذخیره", on_click=self.save_new_class, bgcolor=ft.Colors.CYAN_700, color=ft.Colors.WHITE),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        header = ft.Row(
            controls=[
                ft.Text("مدیریت کلاس‌ها", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.ElevatedButton(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.ADD_ROUNDED, size=18, color=ft.Colors.WHITE),
                            ft.Text("کلاس جدید", color=ft.Colors.WHITE),
                        ],
                        tight=True,
                        spacing=5,
                    ),
                    bgcolor=ft.Colors.CYAN_700,
                    on_click=self.open_add_dialog,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.content = ft.Column(
            controls=[
                header,
                ft.Divider(color=ft.Colors.GREY_800, thickness=1),
                self.classes_column,
            ],
            expand=True,
            spacing=12,
        )

        self.load_classes()

    def load_classes(self):
        self.classes_column.controls.clear()
        classes = get_all_classes()

        if not classes:
            self.classes_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.CLASS_OUTLINED, size=60, color=ft.Colors.GREY_600),
                            ft.Text("هنوز هیچ کلاسی تعریف نشده است!", color=ft.Colors.GREY_400, size=16),
                            ft.Text("روی دکمه 'کلاس جدید' کلیک کنید.", color=ft.Colors.GREY_600, size=13),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=40,
                )
            )
        else:
            for cls in classes:
                self.classes_column.controls.append(self.create_class_card(cls))

        if self.app_page:
            self.app_page.update()

    def create_class_card(self, cls):
        class_id = cls["id"]
        title = cls["title"]
        day_time = cls["day_time"] if "day_time" in cls.keys() and cls["day_time"] else "زمان نامشخص"
        teacher = cls["teacher"] if "teacher" in cls.keys() and cls["teacher"] else "مدرس تعیین نشده"

        return ft.Card(
            elevation=3,
            content=ft.Container(
                bgcolor=ft.Colors.GREY_900,
                border_radius=12,
                padding=14,
                ink=True,
                on_click=lambda _, cid=class_id, t=title: self.select_class(cid, t),
                content=ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.CircleAvatar(
                                    content=ft.Icon(ft.Icons.BOOKMARK_ROUNDED, color=ft.Colors.CYAN_ACCENT, size=20),
                                    bgcolor=ft.Colors.CYAN_900,
                                    radius=22,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                        ft.Text(f"👤 مدرس: {teacher}  |  🕒 {day_time}", size=12, color=ft.Colors.GREY_400),
                                    ],
                                    spacing=4,
                                ),
                            ],
                            spacing=12,
                        ),
                        ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="حذف کلاس",
                                    on_click=lambda _, cid=class_id: self.confirm_delete(cid),
                                ),
                                ft.Icon(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, size=16, color=ft.Colors.CYAN_400),
                            ],
                            spacing=6,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
        )

    def select_class(self, class_id: int, class_title: str):
        if self.on_select_class:
            self.on_select_class(class_id, class_title)

    def open_add_dialog(self, e):
        self.class_title_input.value = ""
        self.class_day_time_input.value = ""
        self.class_teacher_input.value = ""
        self.class_title_input.error_text = None

        if self.add_dialog not in self.app_page.overlay:
            self.app_page.overlay.append(self.add_dialog)
        self.add_dialog.open = True
        self.app_page.update()

    def close_dialog(self, e):
        self.add_dialog.open = False
        self.app_page.update()

    def save_new_class(self, e):
        title = self.class_title_input.value
        day_time = self.class_day_time_input.value or ""
        teacher = self.class_teacher_input.value or ""

        if title and title.strip():
            add_class(title.strip(), day_time.strip(), teacher.strip())
            self.add_dialog.open = False
            self.load_classes()
            self.show_snack("کلاس با موفقیت ایجاد شد ✅", ft.Colors.GREEN_700)
        else:
            self.class_title_input.error_text = "عنوان کلاس الزامی است"
            self.app_page.update()

    def confirm_delete(self, class_id: int):
        delete_class(class_id)
        self.load_classes()
        self.show_snack("کلاس با موفقیت حذف شد 🗑️", ft.Colors.RED_700)

    def show_snack(self, message: str, color):
        self.app_page.snack_bar = ft.SnackBar(
            content=ft.Text(message, text_align=ft.TextAlign.RIGHT),
            bgcolor=color,
        )
        self.app_page.snack_bar.open = True
        self.app_page.update()
