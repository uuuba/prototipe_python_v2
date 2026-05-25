import flet as ft
from src.core.config import (ACCENT, ACCENT2, CARD, CARD2, BORDER,
                              TEXT, MUTED, SUCCESS, ZONE_COLORS)
from src.core.session import Session
from src.services import booking_service

_DANGER = "#ff4d6d"


def MyBookingsPage(page: ft.Page, session: Session, navigate) -> ft.Control:
    bookings_col = ft.Column([], spacing=14)
    total_text   = ft.Text("", size=13, color=MUTED)
    sum_text     = ft.Text("", size=20, weight=ft.FontWeight.BOLD,
                            color=ACCENT2, font_family="Rajdhani")

    def load():
        bookings = booking_service.get_user_bookings(session.username)
        bookings_col.controls.clear()

        if not bookings:
            bookings_col.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text("🎟", size=60),
                    ft.Text("Бронювань поки немає", size=18,
                            weight=ft.FontWeight.BOLD, color=TEXT, font_family="Rajdhani"),
                    ft.Text("Перейдіть на головну та оберіть матч", size=13, color=MUTED),
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
                bookings_col.controls.append(_booking_card(b, page, load))

        page.update()

    load()

    navbar = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=MUTED,
                              on_click=lambda _: navigate("/home")),
                ft.Container(
                    content=ft.Text("SB", size=14, weight=ft.FontWeight.BOLD,
                                    color="#0a0e1a", font_family="Rajdhani"),
                    bgcolor=ACCENT, border_radius=8,
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                ),
                ft.Text("Мої бронювання", size=17, weight=ft.FontWeight.BOLD,
                        color=TEXT, font_family="Rajdhani"),
            ], spacing=8),
            ft.Container(
                content=ft.Text(f"👤 {session.username}", size=13, color=ACCENT),
                bgcolor="#0d1520", border_radius=20,
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                border=ft.border.all(1, BORDER),
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor=CARD, padding=ft.padding.symmetric(horizontal=24, vertical=14),
        border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
    )

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
        bgcolor=CARD, padding=ft.padding.symmetric(horizontal=24, vertical=14),
        border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
    )

    body = ft.Container(
        content=ft.Column([bookings_col], scroll=ft.ScrollMode.AUTO, expand=True),
        padding=ft.padding.symmetric(horizontal=24, vertical=20),
        expand=True,
    )

    return ft.Column([navbar, stats_bar, body], spacing=0, expand=True)


def _booking_card(b, page, reload_fn) -> ft.Control:
    mi         = b.match_info
    zone_color = ZONE_COLORS.get(b.zone, ACCENT)
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
                ft.Text(mi.get("sport", ""), size=13, color=ACCENT,
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
                _info_box("📅 Дата матчу",
                          f"{mi.get('date','')}  {mi.get('time','')}"),
                _info_box("🎟 Місце",
                          f"Ряд {b.seat_id[0]}, №{b.seat_id[1:]}"),
                _info_box("💰 Ціна", f"{b.price} грн", value_color=ACCENT2),
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
        bgcolor=CARD, border_radius=16, padding=20,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=12, color="#00000050", offset=ft.Offset(0, 4)),
    )


def _info_box(label: str, value: str, value_color: str = "#e8eaf0") -> ft.Control:
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
