import flet as ft


def LoginView(page: ft.Page, on_login_success):
    current_ramz = ["1234"]

    username_field = ft.TextField(
        label="نام کاربری",
        value="teacher",
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
        user = username_field.value.strip() if username_field.value else ""
        pwd = password_field.value if password_field.value else ""

        if user == "teacher" and pwd == current_ramz[0]:
            error_text.visible = False
            page.update()
            on_login_success()
        else:
            error_text.value = "نام کاربری یا رمز عبور اشتباه است"
            error_text.color = ft.Colors.RED_300
            error_text.visible = True
            page.update()

    # اتصال کلید Enter روی فیلد رمز عبور برای ورود سریع
    password_field.on_submit = handle_login

    # --- دیالوگ تغییر رمز عبور ---
    old_ramz_field = ft.TextField(
        label="رمز عبور فعلی",
        password=True,
        can_reveal_password=True,
        border_radius=12,
        text_align=ft.TextAlign.RIGHT,
    )
    new_ramz_field = ft.TextField(
        label="رمز عبور جدید",
        password=True,
        can_reveal_password=True,
        border_radius=12,
        text_align=ft.TextAlign.RIGHT,
    )
    confirm_ramz_field = ft.TextField(
        label="تکرار رمز عبور جدید",
        password=True,
        can_reveal_password=True,
        border_radius=12,
        text_align=ft.TextAlign.RIGHT,
    )
    dialog_error = ft.Text(
        value="",
        color=ft.Colors.RED_300,
        size=12,
        visible=False,
        text_align=ft.TextAlign.RIGHT,
    )

    def close_dialog(e=None):
        change_dialog.open = False
        page.update()

    def save_new_password(e=None):
        old_val = old_ramz_field.value or ""
        new_val = new_ramz_field.value or ""
        confirm_val = confirm_ramz_field.value or ""

        if old_val != current_ramz[0]:
            dialog_error.value = "رمز عبور فعلی اشتباه است"
            dialog_error.visible = True
        elif new_val != confirm_val:
            dialog_error.value = "رمز عبور جدید با تکرار آن یکسان نیست"
            dialog_error.visible = True
        elif len(new_val) < 4:
            dialog_error.value = "رمز عبور باید حداقل ۴ کاراکتر باشد"
            dialog_error.visible = True
        else:
            current_ramz[0] = new_val
            change_dialog.open = False
            error_text.value = "رمز عبور با موفقیت تغییر کرد"
            error_text.color = ft.Colors.GREEN_400
            error_text.visible = True
        page.update()

    change_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("تغییر رمز عبور", text_align=ft.TextAlign.RIGHT),
        content=ft.Column(
            [old_ramz_field, new_ramz_field, confirm_ramz_field, dialog_error],
            tight=True,
            spacing=10,
        ),
        actions=[
            ft.TextButton(content=ft.Text("انصراف"), on_click=close_dialog),
            ft.ElevatedButton(
                content=ft.Text("ذخیره", color=ft.Colors.BLACK),
                bgcolor=ft.Colors.CYAN_400,
                on_click=save_new_password,
            ),
        ],
    )

    def open_dialog(e=None):
        old_ramz_field.value = ""
        new_ramz_field.value = ""
        confirm_ramz_field.value = ""
        dialog_error.visible = False
        if change_dialog not in page.overlay:
            page.overlay.append(change_dialog)
        change_dialog.open = True
        page.update()

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
                            "نرم افزار مدیریت حضور غیاب آموزشی",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER,
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
                ft.TextButton(
                    content=ft.Text("تغییر رمز عبور", color=ft.Colors.CYAN_200, size=13),
                    on_click=open_dialog,
                ),
                ft.Column(
                    spacing=4,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "تهیه شده توسط شرکت نرم افزاری ارتباطات هوشمند نوین جنوب",
                            size=10,
                            color=ft.Colors.GREY_500,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "با همکاری و حمایت پژوهش‌سرای شهید احمدی‌ تنها شهرستان کنگان",
                            size=10,
                            color=ft.Colors.CYAN_300,
                            weight=ft.FontWeight.W_500,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
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
