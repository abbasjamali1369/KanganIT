import flet as ft


def LoginView(page: ft.Page, on_login_success):
    username_field = ft.TextField(
        label="نام کاربری",
        prefix_icon=ft.Icons.PERSON_ROUNDED,
        border_radius=14,
        color=ft.Colors.WHITE,
        border_color=ft.Colors.GREY_700,
        focused_border_color=ft.Colors.CYAN_400,
        label_style=ft.TextStyle(color=ft.Colors.GREY_400),
        text_align=ft.TextAlign.RIGHT,
        autofocus=True,
    )

    password_field = ft.TextField(
        label="رمز عبور",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_ROUNDED,
        border_radius=14,
        color=ft.Colors.WHITE,
        border_color=ft.Colors.GREY_700,
        focused_border_color=ft.Colors.CYAN_400,
        label_style=ft.TextStyle(color=ft.Colors.GREY_400),
        text_align=ft.TextAlign.RIGHT,
    )

    error_text = ft.Text(
        value="",
        color=ft.Colors.RED_300,
        size=12,
        weight=ft.FontWeight.W_500,
        visible=False,
        text_align=ft.TextAlign.CENTER,
    )

    def handle_login(e=None):
        # بررسی ورود (پیش‌فرض: admin / 1234)
        user = username_field.value.strip() if username_field.value else ""
        pwd = password_field.value.strip() if password_field.value else ""

        if user == "admin" and pwd == "1234":
            error_text.visible = False
            page.update()
            on_login_success()
        else:
            error_text.value = "نام کاربری یا رمز عبور اشتباه است (admin / 1234)"
            error_text.visible = True
            page.update()

    # اتصال کلید Enter روی فیلد رمز عبور برای ورود سریع
    password_field.on_submit = handle_login

    # کارت لاگین با استایل شیک و سایه نرم
    card = ft.Container(
        width=350,
        padding=28,
        border_radius=22,
        bgcolor=ft.Colors.GREY_900,
        border=ft.Border.all(1, ft.Colors.GREY_800),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=30,
            color=ft.Colors.BLACK54,
            offset=ft.Offset(0, 10),
        ),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            controls=[
                ft.Container(
                    width=72,
                    height=72,
                    border_radius=36,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(-1, -1),
                        end=ft.Alignment(1, 1),
                        colors=[ft.Colors.CYAN_700, ft.Colors.CYAN_900],
                    ),
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(
                        ft.Icons.SCHOOL_ROUNDED,
                        size=38,
                        color=ft.Colors.CYAN_200,
                    ),
                ),
                ft.Column(
                    spacing=4,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "مدیریت آموزشگاه",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        ft.Text(
                            "لطفاً وارد حساب کاربری خود شوید",
                            size=12,
                            color=ft.Colors.GREY_400,
                        ),
                    ],
                ),
                ft.Column(
                    spacing=12,
                    controls=[
                        username_field,
                        password_field,
                    ],
                ),
                error_text,
                ft.ElevatedButton(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                "ورود به سیستم",
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLACK,
                            ),
                            ft.Icon(
                                ft.Icons.LOGIN_ROUNDED,
                                size=18,
                                color=ft.Colors.BLACK,
                            ),
                        ],
                        spacing=8,
                    ),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=12),
                        padding=14,
                    ),
                    bgcolor=ft.Colors.CYAN_400,
                    width=300,
                    on_click=handle_login,
                ),
                ft.Text(
                    "سامانه مدیریت حضور و غیاب دانش‌آموزان",
                    size=10,
                    color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )

    # پس‌زمینه تیره و مدرن کل صفحه
    return ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=[ft.Colors.GREY_900, ft.Colors.BLUE_GREY_900, ft.Colors.GREY_900],
        ),
        alignment=ft.Alignment(0, 0),
        content=card,
    )
