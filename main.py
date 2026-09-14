import flet as ft

from database import init_db
from views.login_view import LoginView
from views.classes_view import ClassesView
from views.students_view import StudentsView


def main(page: ft.Page):
    # تنظیمات عمومی و پیکربندی صفحه
    page.title = "آموزشگاه من | کنگان آی‌تی"
    page.window.icon = "assets/icon.png"
    page.theme_mode = ft.ThemeMode.DARK
    page.rtl = True
    page.padding = 0
    page.margin = 0
    page.adaptive = True
    page.scroll = ft.ScrollMode.AUTO

    # تنظیم فونت و تم اختصاصی مدرن
    page.fonts = {
        "Vazirmatn": "fonts/Vazirmatn-Regular.ttf",
        "Vazirmatn-Bold": "fonts/Vazirmatn-Bold.ttf",
    }
    page.theme = ft.Theme(
        font_family="Vazirmatn",
        color_scheme_seed=ft.Colors.CYAN_400,
        visual_density=ft.VisualDensity.COMPACT,
    )

    # مقداردهی اولیه دیتابیس
    init_db()

    def open_kanganit(e=None):
        """باز کردن وب‌سایت در وب، دسکتاپ و موبایل"""
        try:
            page.launch_url("https://kanganit.ir")
        except Exception:
            pass

    def close_about_developer_dialog(dialog):
        dialog.open = False
        page.update()

    def show_about_developer_dialog(e=None):
        """نمایش پنجره مدرن اطلاعات توسعه‌دهنده"""

        about_dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=20),
            bgcolor=ft.Colors.GREY_900,
            content_padding=20,
            title=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.VERIFIED_ROUNDED,
                        color=ft.Colors.CYAN_400,
                        size=24,
                    ),
                    ft.Text(
                        "درباره توسعه‌دهنده",
                        size=17,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
                spacing=8,
            ),
            content=ft.Container(
                width=340,
                content=ft.Column(
                    tight=True,
                    spacing=14,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            padding=4,
                            shape=ft.BoxShape.CIRCLE,
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.top_left,
                                end=ft.alignment.bottom_right,
                                colors=[ft.Colors.CYAN_400, ft.Colors.BLUE_600],
                            ),
                            content=ft.CircleAvatar(
                                radius=36,
                                bgcolor=ft.Colors.GREY_900,
                                content=ft.Icon(
                                    ft.Icons.CODE_ROUNDED,
                                    size=34,
                                    color=ft.Colors.CYAN_300,
                                ),
                            ),
                        ),
                        ft.Column(
                            spacing=4,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    "عباس جمالی نژاد",
                                    size=17,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    "توسعه‌دهنده نرم‌افزار و سامانه‌های هوشمند",
                                    size=12,
                                    color=ft.Colors.CYAN_200,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                        ),
                        ft.Divider(
                            color=ft.Colors.GREY_800,
                            height=1,
                            thickness=1,
                        ),
                        ft.Container(
                            padding=ft.Padding(left=12, top=8, right=12, bottom=8),
                            bgcolor=ft.Colors.GREY_850,
                            border_radius=ft.BorderRadius.all(10),
                            content=ft.Text(
                                "طراحی و پیاده‌سازی شده در مجموعه آموزشی و نرم‌افزاری کنگان آی‌تی",
                                size=11,
                                color=ft.Colors.GREY_300,
                                text_align=ft.TextAlign.CENTER,
                            ),
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
                                spacing=8,
                            ),
                            bgcolor=ft.Colors.CYAN_400,
                            url="https://kanganit.ir",
                            on_click=open_kanganit,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=ft.Padding(left=16, top=12, right=16, bottom=12),
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
                        size=13,
                    ),
                    on_click=lambda e: close_about_developer_dialog(about_dialog),
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
        """نمایش صفحه مدیریت کلاس‌ها همراه با نوار برندینگ مدرن"""
        page.clean()

        classes_screen = ClassesView(
            page,
            on_select_class=show_students_view,
        )

        branding_bar = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.TextButton(
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
                                spacing=6,
                            ),
                            url="https://kanganit.ir",
                            on_click=open_kanganit,
                            tooltip="ورود به وب‌سایت کنگان آی‌تی",
                        ),
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
            padding=ft.Padding(left=14, top=6, right=14, bottom=6),
            bgcolor=ft.Colors.GREY_900,
            border=ft.Border(
                bottom=ft.BorderSide(
                    width=1,
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
