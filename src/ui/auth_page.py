import re
import flet as ft
from src.core.config import ACCENT, CARD, BORDER, TEXT, MUTED, BG
from src.core.session import Session
from src.services import auth_service

_DANGER = "#ff4d6d"
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def AuthPage(page: ft.Page, session: Session, navigate) -> ft.Control:
    is_login_mode = [True]

    username_field = ft.TextField(
        hint_text="Ім'я користувача", prefix_icon=ft.Icons.PERSON_OUTLINE,
        border_color=BORDER, focused_border_color=ACCENT,
        color=TEXT, hint_style=ft.TextStyle(color=MUTED),
        bgcolor="#0d1520", border_radius=12, height=52,
    )
    email_field = ft.TextField(
        hint_text="Email", prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_color=BORDER, focused_border_color=ACCENT,
        color=TEXT, hint_style=ft.TextStyle(color=MUTED),
        bgcolor="#0d1520", border_radius=12, height=52, visible=False,
    )
    password_field = ft.TextField(
        hint_text="Пароль", prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True, can_reveal_password=True,
        border_color=BORDER, focused_border_color=ACCENT,
        color=TEXT, hint_style=ft.TextStyle(color=MUTED),
        bgcolor="#0d1520", border_radius=12, height=52,
    )
    error_text    = ft.Text("", color=_DANGER, size=13, visible=False)
    title_text    = ft.Text("Вхід до системи", size=26, weight=ft.FontWeight.BOLD,
                            color=TEXT, font_family="Rajdhani")
    subtitle_text = ft.Text("Увійдіть, щоб бронювати місця", size=13, color=MUTED)
    submit_label  = ft.Text("Увійти", size=15, weight=ft.FontWeight.BOLD, color="#0a0e1a")
    toggle_label  = ft.Text("Немає акаунту? Зареєструватись",
                            size=13, color=ACCENT, weight=ft.FontWeight.W_500)

    def show_error(msg: str):
        error_text.value = msg
        error_text.visible = True
        page.update()

    def submit(_):
        error_text.visible = False
        username = username_field.value.strip()
        password = password_field.value.strip()

        if not username or not password:
            show_error("Заповніть усі поля")
            return

        if len(username) < 3:
            show_error("Ім'я користувача має бути не менше 3 символів")
            return

        if len(password) < 6:
            show_error("Пароль має бути не менше 6 символів")
            return

        if is_login_mode[0]:
            ok, result = auth_service.login(username, password)
            if ok:
                session.login(result)
                navigate("/home")
            else:
                show_error(result)
        else:
            email = email_field.value.strip()
            if not email:
                show_error("Введіть email")
                return
            if not _EMAIL_RE.match(email):
                show_error("Невірний формат email")
                return
            ok, msg = auth_service.register(username, password, email)
            if ok:
                _, user = auth_service.login(username, password)
                session.login(user)
                navigate("/home")
            else:
                show_error(msg)

    def toggle_mode(_):
        is_login_mode[0] = not is_login_mode[0]
        login = is_login_mode[0]
        title_text.value    = "Вхід до системи" if login else "Реєстрація"
        subtitle_text.value = ("Увійдіть, щоб бронювати місця" if login
                               else "Створіть акаунт безкоштовно")
        submit_label.value  = "Увійти" if login else "Зареєструватись"
        toggle_label.value  = ("Немає акаунту? Зареєструватись" if login
                               else "Вже маєте акаунт? Увійти")
        email_field.visible = not login
        username_field.value = email_field.value = password_field.value = ""
        error_text.visible = False
        page.update()

    submit_btn = ft.ElevatedButton(
        content=submit_label,
        style=ft.ButtonStyle(
            bgcolor=ACCENT, shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(vertical=14),
        ),
        width=340, on_click=submit,
    )

    bg_icons = ft.Stack([
        ft.Text("⚽", size=80,  opacity=0.04, top=40,    left=20),
        ft.Text("🏀", size=100, opacity=0.04, top=200,   right=10),
        ft.Text("🥊", size=90,  opacity=0.04, bottom=150, left=50),
        ft.Text("🎾", size=70,  opacity=0.04, bottom=80,  right=30),
        ft.Text("🏐", size=85,  opacity=0.04, top=350,   left=140),
    ], expand=True)

    card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Text("SB", size=18, weight=ft.FontWeight.BOLD,
                                    color="#0a0e1a", font_family="Rajdhani"),
                    bgcolor=ACCENT, border_radius=10,
                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                ),
                ft.Text("SportBook", size=20, weight=ft.FontWeight.BOLD,
                        color=TEXT, font_family="Rajdhani"),
            ], spacing=10),
            ft.Divider(height=20, color="transparent"),
            title_text, subtitle_text,
            ft.Divider(height=16, color="transparent"),
            username_field, email_field, password_field,
            ft.Divider(height=4, color="transparent"),
            error_text,
            ft.Divider(height=4, color="transparent"),
            submit_btn,
            ft.Divider(height=4, color="transparent"),
            ft.Row([ft.TextButton(content=toggle_label, on_click=toggle_mode)],
                   alignment=ft.MainAxisAlignment.CENTER),
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.START),
        width=380, bgcolor=CARD, border_radius=20, padding=36,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=40, color="#00000080", offset=ft.Offset(0, 10)),
    )

    return ft.Stack([
        ft.Container(bgcolor=BG, expand=True),
        bg_icons,
        ft.Container(content=card, alignment=ft.Alignment(0, 0), expand=True),
    ], expand=True)