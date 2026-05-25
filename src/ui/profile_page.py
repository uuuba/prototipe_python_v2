import flet as ft
from src.core.config import (ACCENT, ACCENT2, CARD, CARD2, BORDER,
                              TEXT, MUTED, SUCCESS, DANGER, ZONE_COLORS)
from src.core.session import Session
from src.services import booking_service

_DANGER = "#ff4d6d"


def ProfilePage(page: ft.Page, session: Session, navigate) -> ft.Control:
    # ── Guard ─────────────────────────────────────────────────────────────────
    if not session.is_logged_in:
        navigate("/auth")
        return ft.Container()

    user = session.current_user

    # ── Стан вкладок ──────────────────────────────────────────────────────────
    active_tab = [0]  # 0 = Профіль, 1 = Мої бронювання

    # ── Контент вкладки "Профіль" ─────────────────────────────────────────────
    def profile_tab() -> ft.Control:
        created = user.created_at[:10] if user and user.created_at else "—"
        bookings = booking_service.get_user_bookings(session.username)
        total_spent = sum(b.price for b in bookings)

        avatar = ft.Container(
            content=ft.Text(
                session.username[0].upper(),
                size=36, weight=ft.FontWeight.BOLD,
                color="#0a0e1a", font_family="Rajdhani",
            ),
            width=80, height=80,
            bgcolor=ACCENT, border_radius=40,
            alignment=ft.Alignment(0, 0),
        )

        return ft.Column([
            ft.Row([avatar], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=12, color="transparent"),
            ft.Text(session.username, size=24, weight=ft.FontWeight.BOLD,
                    color=TEXT, font_family="Rajdhani",
                    text_align=ft.TextAlign.CENTER),
            ft.Text(user.email if user else "", size=13, color=MUTED,
                    text_align=ft.TextAlign.CENTER),
            ft.Divider(height=16, color=BORDER),

            # Статистика
            ft.Row([
                _stat_box("🎟", "Бронювань", str(len(bookings))),
                _stat_box("💰", "Витрачено", f"{total_spent} грн"),
                _stat_box("📅", "Акаунт з", created),
            ], spacing=10),

            ft.Divider(height=20, color=BORDER),

            # Інфо
            _info_row(ft.Icons.PERSON_OUTLINE, "Ім'я користувача", session.username),
            _info_row(ft.Icons.EMAIL_OUTLINED, "Email", user.email if user else "—"),
            _info_row(ft.Icons.CALENDAR_TODAY, "Дата реєстрації", created),

            ft.Divider(height=20, color="transparent"),

            # Вихід
            ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.LOGOUT, color="#0a0e1a", size=18),
                    ft.Text("Вийти з акаунту", color="#0a0e1a",
                            weight=ft.FontWeight.BOLD),
                ], tight=True, spacing=8),
                style=ft.ButtonStyle(
                    bgcolor=_DANGER,
                    shape=ft.RoundedRectangleBorder(radius=12),
                    padding=ft.padding.symmetric(vertical=14),
                ),
                width=float("inf"),
                on_click=lambda _: (session.logout(), navigate("/auth")),
            ),
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # ── Контент вкладки "Мої бронювання" ──────────────────────────────────────
    bookings_col = ft.Column([], spacing=14)
    total_text   = ft.Text("", size=13, color=MUTED)
    sum_text     = ft.Text("", size=20, weight=ft.FontWeight.BOLD,
                           color=ACCENT2, font_family="Rajdhani")

    def load_bookings():
        bookings = booking_service.get_user_bookings(session.username)
        bookings_col.controls.clear()

        if not bookings:
            bookings_col.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text("🎟", size=60),
                    ft.Text("Бронювань поки немає", size=18,
                            weight=ft.FontWeight.BOLD, color=TEXT,
                            font_family="Rajdhani"),
                    ft.Text("Перейдіть на головну та оберіть матч",
                            size=13, color=MUTED),
                    ft.ElevatedButton(
                        "Переглянути матчі →",
                        style=ft.ButtonStyle(
                            bgcolor=ACCENT, color="#0a0e1a",
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.padding.symmetric(vertical=12, horizontal=24),
                        ),
                        on_click=lambda _: navigate("/home"),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                alignment=ft.Alignment(0, 0), expand=True, padding=60,
            ))
            total_text.value = "Немає активних бронювань"
            sum_text.value   = ""
        else:
            total_text.value = f"Активних бронювань: {len(bookings)}"
            sum_text.value   = f"Загалом: {sum(b.price for b in bookings)} грн"
            for b in reversed(bookings):
                bookings_col.controls.append(_booking_card(b, page, load_bookings))

        page.update()

    def bookings_tab() -> ft.Control:
        load_bookings()
        stats_bar = ft.Container(
            content=ft.Row([
                ft.Column([total_text, sum_text], spacing=2),
                ft.ElevatedButton(
                    "＋ Нове бронювання",
                    style=ft.ButtonStyle(
                        bgcolor=ACCENT, color="#0a0e1a",
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.padding.symmetric(vertical=10, horizontal=16),
                    ),
                    on_click=lambda _: navigate("/home"),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=CARD2, border_radius=12, padding=14,
            border=ft.border.all(1, BORDER),
        )
        return ft.Column([
            stats_bar,
            ft.Divider(height=8, color="transparent"),
            bookings_col,
        ], spacing=0)

    # ── Вкладки ───────────────────────────────────────────────────────────────
    tab_content = ft.Container(expand=True)

    def switch_tab(index: int):
        active_tab[0] = index
        tab_content.content = ft.Column(
            [profile_tab() if index == 0 else bookings_tab()],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        tab_row.controls = build_tabs()
        page.update()

    def build_tabs():
        tabs = [("👤 Профіль", 0), ("🎟 Мої бронювання", 1)]
        result = []
        for label, idx in tabs:
            active = active_tab[0] == idx
            result.append(ft.Container(
                content=ft.Text(
                    label, size=13, color="#0a0e1a" if active else TEXT,
                    weight=ft.FontWeight.W_600 if active else ft.FontWeight.NORMAL,
                ),
                bgcolor=ACCENT if active else "transparent",
                border_radius=10,
                padding=ft.padding.symmetric(horizontal=18, vertical=9),
                on_click=lambda _, i=idx: switch_tab(i),
                animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            ))
        return result

    tab_row = ft.Row(build_tabs(), spacing=4)
    tab_bar = ft.Container(
        content=tab_row,
        bgcolor=CARD2, border_radius=12, padding=4,
        border=ft.border.all(1, BORDER),
    )

    # Ініціалізація першої вкладки
    tab_content.content = ft.Column(
        [profile_tab()],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    # ── Navbar ────────────────────────────────────────────────────────────────
    navbar = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=MUTED,
                              tooltip="Назад до матчів",
                              on_click=lambda _: navigate("/home")),
                ft.Container(
                    content=ft.Text("SB", size=14, weight=ft.FontWeight.BOLD,
                                    color="#0a0e1a", font_family="Rajdhani"),
                    bgcolor=ACCENT, border_radius=8,
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                ),
                ft.Text("Профіль", size=17, weight=ft.FontWeight.BOLD,
                        color=TEXT, font_family="Rajdhani"),
            ], spacing=8),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.PERSON, color=ACCENT, size=16),
                    ft.Text(session.username, size=13, color=ACCENT),
                ], spacing=6, tight=True),
                bgcolor="#0d1520", border_radius=20,
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                border=ft.border.all(1, BORDER),
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor=CARD, padding=ft.padding.symmetric(horizontal=24, vertical=14),
        border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
    )

    body = ft.Container(
        content=ft.Column([
            tab_bar,
            ft.Divider(height=16, color="transparent"),
            tab_content,
        ], spacing=0, expand=True),
        padding=ft.padding.symmetric(horizontal=24, vertical=20),
        expand=True,
    )

    return ft.Column([navbar, body], spacing=0, expand=True)


# ── Допоміжні віджети ─────────────────────────────────────────────────────────

def _stat_box(icon: str, label: str, value: str) -> ft.Control:
    return ft.Container(
        content=ft.Column([
            ft.Text(icon, size=24),
            ft.Text(value, size=18, weight=ft.FontWeight.BOLD,
                    color="#e8eaf0", font_family="Rajdhani"),
            ft.Text(label, size=11, color="#6b7a99"),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
        bgcolor="#0d1520", border_radius=12, padding=16,
        border=ft.border.all(1, "#1e2d45"), expand=True,
        alignment=ft.Alignment(0, 0),
    )


def _info_row(icon, label: str, value: str) -> ft.Control:
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, color="#6b7a99", size=18),
            ft.Column([
                ft.Text(label, size=11, color="#6b7a99"),
                ft.Text(value, size=14, color="#e8eaf0", weight=ft.FontWeight.W_500),
            ], spacing=1, tight=True),
        ], spacing=12),
        bgcolor="#0d1520", border_radius=12, padding=14,
        border=ft.border.all(1, "#1e2d45"),
    )


def _booking_card(b, page, reload_fn) -> ft.Control:
    mi         = b.match_info
    zone_color = ZONE_COLORS.get(b.zone, "#00d4ff")
    date_str   = b.booked_at[:10] if b.booked_at else ""

    def confirm_cancel(booking_id: str):
        def do_cancel(_):
            dlg.open = False
            page.update()
            ok, msg = booking_service.cancel_booking(booking_id, b.username)
            page.snack_bar = ft.SnackBar(
                content=ft.Text(msg, color="#0a0e1a"),
                bgcolor=SUCCESS if ok else "#ff4d6d", duration=3000,
            )
            page.snack_bar.open = True
            reload_fn()

        dlg = ft.AlertDialog(
            modal=True, bgcolor="#111827",
            shape=ft.RoundedRectangleBorder(radius=14),
            title=ft.Text("Скасувати бронювання?", color="#e8eaf0",
                          weight=ft.FontWeight.BOLD),
            content=ft.Text("Це скасує бронювання і звільнить місце.",
                            color="#6b7a99", size=13),
            actions=[
                ft.TextButton("Ні, залишити",
                              style=ft.ButtonStyle(color="#6b7a99"),
                              on_click=lambda _: _close(dlg, page)),
                ft.ElevatedButton(
                    "Так, скасувати",
                    style=ft.ButtonStyle(bgcolor="#ff4d6d", color="#e8eaf0",
                                         shape=ft.RoundedRectangleBorder(radius=10)),
                    on_click=do_cancel,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text(mi.get("sport", ""), size=13, color="#00d4ff",
                        weight=ft.FontWeight.W_600),
                ft.Container(
                    content=ft.Text(f"Зона {b.zone}", size=11,
                                    color="#0a0e1a", weight=ft.FontWeight.BOLD),
                    bgcolor=zone_color, border_radius=20,
                    padding=ft.padding.symmetric(horizontal=10, vertical=3),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text(f"{mi.get('home','')} vs {mi.get('away','')}", size=18,
                    weight=ft.FontWeight.BOLD, color="#e8eaf0", font_family="Rajdhani"),
            ft.Row([
                _mini_info("📅 Дата матчу",
                           f"{mi.get('date','')}  {mi.get('time','')}"),
                _mini_info("🎟 Місце",
                           f"Ряд {b.seat_id[0]}, №{b.seat_id[1:]}"),
                _mini_info("💰 Ціна", f"{b.price} грн", value_color="#ff6b35"),
            ], spacing=8),
            ft.Row([
                ft.Text(f"📍 {mi.get('stadium','')}, {mi.get('city','')}",
                        size=12, color="#6b7a99"),
                ft.Text(f"Заброньовано: {date_str}", size=11, color="#6b7a99"),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=4, color="#1e2d45"),
            ft.TextButton(
                "Скасувати бронювання",
                style=ft.ButtonStyle(color="#ff4d6d"),
                icon=ft.Icons.CANCEL_OUTLINED, icon_color="#ff4d6d",
                on_click=lambda _, bid=b.id: confirm_cancel(bid),
            ),
        ], spacing=8),
        bgcolor="#111827", border_radius=16, padding=20,
        border=ft.border.all(1, "#1e2d45"),
        shadow=ft.BoxShadow(blur_radius=12, color="#00000050", offset=ft.Offset(0, 4)),
    )


def _mini_info(label: str, value: str, value_color: str = "#e8eaf0") -> ft.Control:
    return ft.Container(
        content=ft.Column([
            ft.Text(label, size=11, color="#6b7a99"),
            ft.Text(value, size=13, color=value_color, weight=ft.FontWeight.W_600),
        ], spacing=2),
        bgcolor="#0d1520", border_radius=10,
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border=ft.border.all(1, "#1e2d45"), expand=True,
    )


def _close(dlg, page):
    dlg.open = False
    page.update()