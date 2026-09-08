import flet as ft

def LoginView(page: ft.Page, on_login_success):
    username_field = ft.TextField(
        label="نام کاربری",
        prefix_icon=ft.Icons.PERSON_ROUNDED,
        border_radius=14,
        color=ft.Colors.WHITE,
        border_color=ft.Colors.BLUE_GREY_400,
        focused_border_color=ft.Colors.CYAN_ACCENT,
        text_align=ft.TextAlign.RIGHT,
    )
    
    password_field = ft.TextField(
        label="رمز عبور",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_ROUNDED,
        border_radius=14,
        color=ft.Colors.WHITE,
        border_color=ft.Colors.BLUE_GREY_400,
        focused_border_color=ft.Colors.CYAN_ACCENT,
        text_align=ft.TextAlign.RIGHT,
    )
    
    error_text = ft.Text(
        value="",
        color=ft.Colors.RED_ACCENT_100,
        size=13,
        weight=ft.FontWeight.W_500,
        visible=False,
    )

    def handle_login(e):
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

    # کارت لاگین با استایل شیک و سایه نرم
    card = ft.Container(
        width=340,
        padding=28,
        border_radius=24,
        bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.WHITE),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=25,
            color=ft.Colors.BLACK54,
            offset=ft.Offset(0, 10),
        ),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            controls=[
                ft.Container(
                    width=70,
                    height=70,
                    border_radius=35,
                    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.CYAN_ACCENT),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(
                        ft.Icons.SCHOOL_ROUNDED,
                        size=40,
                        color=ft.Colors.CYAN_ACCENT,
                    ),
                ),
                ft.Text(
                    "مدیریت آموزشگاه",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(
                    "لطفاً وارد حساب خود شوید",
                    size=13,
                    color=ft.Colors.WHITE70,
                ),
                username_field,
                password_field,
                error_text,
                ft.Container(height=6),
                ft.ElevatedButton(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text("ورود به سیستم", size=16, weight=ft.FontWeight.BOLD),
                            ft.Icon(ft.Icons.LOGIN_ROUNDED),
                        ]
                    ),
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: ft.Colors.CYAN_ACCENT_400},
                        color={ft.ControlState.DEFAULT: ft.Colors.BLACK87},
                        shape=ft.RoundedRectangleBorder(radius=14),
                        padding=16,
                    ),
                    width=300,
                    on_click=handle_login,
                )
            ],
        ),
    )

    # پس‌زمینه گرادیانت شیک کل صفحه
    return ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=["#0f172a", "#1e1b4b", "#0f172a"],
        ),
        alignment=ft.Alignment.CENTER,
        content=card,
    )
