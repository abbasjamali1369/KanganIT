import flet as ft

from database import init_db
from views.login_view import LoginView
from views.classes_view import ClassesView
from views.students_view import StudentsView


def main(page: ft.Page):
    page.title = "آموزشگاه من"
    page.window.icon = "assets/icon.png"
    page.theme_mode = ft.ThemeMode.DARK
    page.rtl = True
    page.padding = 0
    page.margin = 0
    page.adaptive = True
    page.scroll = ft.ScrollMode.AUTO

    # مقداردهی اولیه دیتابیس
    init_db()

    def open_kanganit(e=None):
        """باز کردن وب‌سایت در وب و دسکتاپ"""
        try:
            page.launch_url("https://kanganit.ir")
        except Exception:
            pass

    def close_about_developer_dialog(dialog):
        dialog.open = False
        page.update()

    def show_about_developer_dialog(e=None):
        """نمایش اطلاعات توسعه‌دهنده"""

        about_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.VERIFIED_ROUNDED,
                        color=ft.Colors.CYAN_400,
                        size=22,
                    ),
                    ft.Text(
                        "درباره توسعه‌دهنده",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
                spacing=8,
            ),
            content=ft.Container(
                width=330,
                padding=ft.Padding(10, 5, 10, 5),
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.CircleAvatar(
                            radius=32,
                            bgcolor=ft.Colors.CYAN_800,
                            content=ft.Icon(
                                ft.Icons.TERMINAL_ROUNDED,
                                size=32,
                                color=ft.Colors.CYAN_200,
                            ),
                        ),
                        ft.Text(
                            "عباس جمالی نژاد",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "توسعه‌دهنده نرم‌افزار و سامانه‌های تحت وب",
                            size=12,
                            color=ft.Colors.CYAN_200,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Divider(
                            color=ft.Colors.GREY_800,
                            height=1,
                        ),
                        ft.Text(
                            "طراحی و پیاده‌سازی شده در مجموعه آموزشی و نرم‌افزاری کنگان آی‌تی",
                            size=11,
                            color=ft.Colors.GREY_300,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.ElevatedButton(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(
                                        ft.Icons.OPEN_IN_NEW_ROUNDED,
                                        size=16,
                                        color=ft.Colors.BLACK,
                                    ),
                                    ft.Text(
                                        "مشاهده وب‌سایت kanganit.ir",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLACK,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=6,
                            ),
                            bgcolor=ft.Colors.CYAN_400,
                            url="https://kanganit.ir",
                            on_click=open_kanganit,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.Padding(12, 10, 12, 10),
                            ),
                        ),
                    ],
                ),
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text(
                        "بستن",
                        color=ft.Colors.GREY_400,
                    ),
                    on_click=lambda e: close_about_developer_dialog(
                        about_dialog
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.START,
        )

        page.overlay.append(about_dialog)
        about_dialog.open = True
        page.update()

    def show_students_view(class_id: int, class_title: str):
        """نمایش صفحه فهرست دانش‌آموزان یک کلاس"""

        page.clean()

        students_screen = StudentsView(
            page,
            class_id=class_id,
            class_title=class_title,
            on_back=show_classes_view,
        )

        page.add(students_screen)
        page.update()

    def show_classes_view():
        """نمایش صفحه مدیریت کلاس‌ها"""

        page.clean()

        classes_screen = ClassesView(
            page,
            on_select_class=show_students_view,
        )

        branding_bar = ft.Container(
            content=ft.Row(
                controls=[
                    ft.TextButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.LANGUAGE_ROUNDED,
                                    size=16,
                                    color=ft.Colors.CYAN_300,
                                ),
                                ft.Text(
                                    "kanganit.ir",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.CYAN_300,
                                ),
                            ],
                            spacing=4,
                        ),
                        url="https://kanganit.ir",
                        on_click=open_kanganit,
                        tooltip="ورود به وب‌سایت کنگان آی‌تی",
                    ),
                    ft.IconButton(
                        icon=ft.Icons.INFO_OUTLINE_ROUNDED,
                        icon_color=ft.Colors.CYAN_300,
                        icon_size=20,
                        tooltip="درباره توسعه‌دهنده",
                        on_click=show_about_developer_dialog,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(12, 4, 12, 4),
            bgcolor=ft.Colors.GREY_900,
            border=ft.Border(
                bottom=ft.BorderSide(
                    width=0.8,
                    color=ft.Colors.GREY_800,
                ),
            ),
        )

        main_classes_container = ft.Column(
            controls=[
                branding_bar,
                ft.Container(
                    content=classes_screen,
                    expand=True,
                ),
            ],
            expand=True,
            spacing=0,
        )

        page.add(main_classes_container)
        page.update()

    def show_login_view():
        """نمایش صفحه ورود"""

        page.clean()

        login_screen = LoginView(
            page,
            on_login_success=show_classes_view,
        )

        page.add(login_screen)
        page.update()

    # شروع برنامه با صفحه ورود
    show_login_view()


if __name__ == "__main__":
    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",
        port=8550,
        assets_dir="assets",
    )
