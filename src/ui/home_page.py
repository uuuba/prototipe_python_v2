import flet as ft
from src.core.config import (ACCENT, ACCENT2, CARD, CARD2, BORDER,
                              TEXT, MUTED, SUCCESS, ZONE_COLORS)
from src.core.session import Session
from src.services import match_service, booking_service
from src.services.booking_service import MAX_SEATS_PER_USER_PER_MATCH


def HomePage(page: ft.Page, session: Session, navigate) -> ft.Control:

    if not session.is_logged_in:
        navigate("/auth")
        return ft.Container()

    filter_sport = ["Всі"]
    all_matches  = match_service.get_all()
    sports       = ["Всі"] + list(dict.fromkeys(m.sport for m in all_matches))


    def open_match_dialog(match_id: str):
        match = match_service.get_by_id(match_id)
        if not match:
            return

        selected_seat  = [None]
        seat_info  = ft.Text("Оберіть місце на схемі", color=MUTED, size=13)
        result_txt = ft.Text("", size=13)

        booked_count = booking_service.get_user_match_booking_count(match_id, session.username)
        remaining    = MAX_SEATS_PER_USER_PER_MATCH - booked_count

        limit_row = ft.Row([
            ft.Icon(ft.Icons.CONFIRMATION_NUMBER_OUTLINED, color=ACCENT2, size=15),
            ft.Text(
                f"Ваші місця: {booked_count}/{MAX_SEATS_PER_USER_PER_MATCH}  "
                f"(залишилось: {remaining})",
                size=12, color=ACCENT2 if remaining > 0 else "#ff4d6d",
                weight=ft.FontWeight.W_500,
            ),
        ], spacing=4)

        confirm = ft.ElevatedButton(
            "Забронювати", disabled=(remaining == 0),
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: ACCENT,
                         ft.ControlState.DISABLED: "#1e2d45"},
                color={ft.ControlState.DEFAULT: "#0a0e1a",
                       ft.ControlState.DISABLED: MUTED},
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )
        grid_col = ft.Column(spacing=6)

        def build_grid():
            grid_col.controls.clear()
            rows_dict: dict[str, list] = {}
            for s in match.seats:
                rows_dict.setdefault(s.row, []).append(s)
            for row_ltr, row_seats in sorted(rows_dict.items()):
                cells = [ft.Container(
                    content=ft.Text(row_ltr, size=11, color=MUTED,
                                    weight=ft.FontWeight.BOLD),
                    width=22, height=22, alignment=ft.Alignment(0, 0),
                )]
                for seat in sorted(row_seats, key=lambda x: x.number):
                    color   = ZONE_COLORS[seat.zone]
                    booked  = seat.booked
                    is_sel  = selected_seat[0] == seat.id

                    def make_click(s=seat):
                        def on_click(_):
                            if remaining == 0:
                                result_txt.value = "❌ Ліміт досягнуто: максимум 3 місця на одну особу"
                                result_txt.color = "#ff4d6d"
                                page.update()
                                return

                            selected_seat[0] = s.id
                            price = match.price_zones[s.zone]
                            seat_info.value = (
                                f"Обране: ряд {s.row}, місце {s.number} · "
                                f"Зона {s.zone} · {price} грн"
                            )
                            seat_info.color = ZONE_COLORS[s.zone]
                            confirm.disabled = False
                            result_txt.value = ""
                            build_grid()
                            page.update()

                        return on_click

                    cells.append(ft.Container(
                        width=22, height=22, border_radius=4,
                        bgcolor=("2d3748" if booked
                                 else (color if is_sel else f"{color}33")),
                        border=ft.border.all(1, color if not booked else "#2d3748"),
                        tooltip=(f"Ряд {seat.row}, №{seat.number} — "
                                 f"{'Зайнято' if booked else f'Зона {seat.zone}'}"),
                        on_click=make_click() if not booked else None,
                        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
                    ))
                grid_col.controls.append(ft.Row(cells, spacing=4, tight=True))

        build_grid()

        def on_confirm(_):
            nonlocal booked_count, remaining
            if not selected_seat[0]:
                return
            ok, msg = booking_service.book_seat(
                match.id, selected_seat[0], session.username
            )
            result_txt.color = SUCCESS if ok else "#ff4d6d"
            result_txt.value = f"{'✅' if ok else '❌'} {msg}"
            if ok:
                booked_count = booking_service.get_user_match_booking_count(match_id, session.username)
                remaining    = MAX_SEATS_PER_USER_PER_MATCH - booked_count
                limit_row.controls[1].value = (
                    f"Ваші місця: {booked_count}/{MAX_SEATS_PER_USER_PER_MATCH}  "
                    f"(залишилось: {remaining})"
                )
                limit_row.controls[1].color = ACCENT2 if remaining > 0 else "#ff4d6d"
                confirm.disabled = (remaining == 0)
                selected_seat[0] = None
                updated = match_service.get_by_id(match.id)
                match.seats = updated.seats
                build_grid()
                seat_info.value = (
                    "Оберіть наступне місце або закрийте вікно"
                    if remaining > 0 else "Досягнуто ліміт місць для цього матчу"
                )
                seat_info.color = MUTED
            page.update()

        confirm.on_click = on_confirm

        legend = ft.Row(
            [ft.Row([
                ft.Container(width=12, height=12, bgcolor=c, border_radius=3),
                ft.Text(f"Зона {z}", size=11, color=MUTED),
                ft.Text(f"{match.price_zones[z]} грн", size=11, color=TEXT),
            ], spacing=4) for z, c in ZONE_COLORS.items()] + [
                ft.Row([
                    ft.Container(width=12, height=12, bgcolor="#2d3748", border_radius=3),
                    ft.Text("Зайнято", size=11, color=MUTED),
                ], spacing=4)
            ], spacing=16, wrap=True,
        )

        def close_dlg():
            dlg.open = False
            page.update()
            refresh_list()

        dlg = ft.AlertDialog(
            modal=True, bgcolor=CARD,
            shape=ft.RoundedRectangleBorder(radius=16),
            title=ft.Column([
                ft.Text(match.sport, size=13, color=ACCENT),
                ft.Text(f"{match.home} vs {match.away}", size=18,
                        weight=ft.FontWeight.BOLD, color=TEXT, font_family="Rajdhani"),
                ft.Text(f"📅 {match.date}  🕐 {match.time}  "
                        f"📍 {match.stadium}, {match.city}", size=12, color=MUTED),
            ], spacing=2, tight=True),
            content=ft.Container(
                content=ft.Column([
                    limit_row,
                    ft.Divider(height=4, color=BORDER),
                    ft.Text("Схема залу", size=13, color=TEXT,
                            weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([ft.Text("🎯 ПОЛЕ / АРЕНА", size=11, color=MUTED)],
                                   alignment=ft.MainAxisAlignment.CENTER),
                            ft.Divider(height=8, color=BORDER),
                            ft.Column([grid_col], scroll=ft.ScrollMode.AUTO),
                        ], spacing=6),
                        bgcolor=CARD2, border_radius=12, padding=12,
                        border=ft.border.all(1, BORDER),
                    ),
                    ft.Divider(height=4, color="transparent"),
                    legend,
                    ft.Divider(height=4, color=BORDER),
                    seat_info, result_txt,
                ], spacing=8, scroll=ft.ScrollMode.AUTO),
                width=460, height=440,
            ),
            actions=[
                ft.TextButton("Закрити",
                              style=ft.ButtonStyle(color=MUTED),
                              on_click=lambda _: close_dlg()),
                confirm,
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()


    def match_card(match) -> ft.Control:
        free  = match.free_seats
        total = len(match.seats)
        ratio = (total - free) / total if total else 0
        bar_c = SUCCESS if ratio < 0.6 else (ACCENT2 if ratio < 0.85 else "#ff4d6d")

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(match.sport, size=12, color=ACCENT,
                            weight=ft.FontWeight.W_600),
                    ft.Container(
                        content=ft.Text(match.category, size=10, color=MUTED),
                        bgcolor="#1e2d45", border_radius=20,
                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(f"{match.home} vs {match.away}", size=15,
                        weight=ft.FontWeight.BOLD, color=TEXT, font_family="Rajdhani",
                        max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Row([
                    ft.Text(f"📅 {match.date}", size=11, color=MUTED),
                    ft.Text(f"🕐 {match.time}", size=11, color=MUTED),
                ], spacing=8, wrap=True),
                ft.Text(f"📍 {match.city}", size=11, color=MUTED),
                ft.Text(f"🏟 {match.stadium}", size=11, color=MUTED,
                        max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Divider(height=6, color=BORDER),
                ft.Row([
                    ft.Column([
                        ft.Text(f"Вільних: {free}/{total}", size=11, color=MUTED),
                        ft.Container(
                            content=ft.Container(
                                bgcolor=bar_c, border_radius=4,
                                width=100 * (1 - ratio), height=5,
                            ),
                            bgcolor=BORDER, border_radius=4, width=100, height=5,
                        ),
                    ], spacing=4),
                    ft.Column([
                        ft.Text("від", size=11, color=MUTED),
                        ft.Text(f"{match.min_price} грн", size=15, color=ACCENT2,
                                weight=ft.FontWeight.BOLD, font_family="Rajdhani"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=0),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.ElevatedButton(
                    "Обрати місце →",
                    style=ft.ButtonStyle(
                        bgcolor=ACCENT if free > 0 else "#1e2d45",
                        color="#0a0e1a" if free > 0 else MUTED,
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.padding.symmetric(vertical=9),
                    ),
                    width=float("inf"), disabled=free == 0,
                    on_click=lambda _, mid=match.id: open_match_dialog(mid),
                ),
            ], spacing=7),
            bgcolor=CARD, border_radius=16, padding=16,
            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=12, color="#00000050", offset=ft.Offset(0, 4)),
            expand=True,
        )


    filter_row   = ft.Row([], spacing=8, scroll=ft.ScrollMode.AUTO)
    matches_wrap = ft.Column([], spacing=12)

    def refresh_list():
        nonlocal all_matches
        all_matches = match_service.get_all()
        sp = filter_sport[0]
        filtered = all_matches if sp == "Всі" else [m for m in all_matches if m.sport == sp]

        def chip(label: str):
            active = filter_sport[0] == label
            def click(_, lbl=label):
                filter_sport[0] = lbl
                refresh_list()
            return ft.Container(
                content=ft.Text(label, size=13,
                                color="#0a0e1a" if active else TEXT,
                                weight=ft.FontWeight.W_600 if active else ft.FontWeight.NORMAL),
                bgcolor=ACCENT if active else CARD,
                border_radius=20,
                padding=ft.padding.symmetric(horizontal=14, vertical=7),
                border=ft.border.all(1, ACCENT if active else BORDER),
                on_click=click,
                animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            )

        filter_row.controls = [chip(s) for s in sports]

        # Розбиваємо по 2 картки в рядок
        rows = []
        for i in range(0, len(filtered), 2):
            pair = filtered[i:i+2]
            if len(pair) == 2:
                row = ft.Row([
                    ft.Container(content=match_card(pair[0]), expand=1),
                    ft.Container(content=match_card(pair[1]), expand=1),
                ], spacing=12, expand=True)
            else:
                row = ft.Row([
                    ft.Container(content=match_card(pair[0]), expand=1),
                    ft.Container(expand=1),  # порожній слот
                ], spacing=12, expand=True)
            rows.append(row)

        matches_wrap.controls = rows
        page.update()

    refresh_list()

    navbar = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Text("SB", size=14, weight=ft.FontWeight.BOLD,
                                    color="#0a0e1a", font_family="Rajdhani"),
                    bgcolor=ACCENT, border_radius=8,
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                ),
                ft.Text("SportBook", size=17, weight=ft.FontWeight.BOLD,
                        color=TEXT, font_family="Rajdhani"),
            ], spacing=8),
            ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PERSON, color=ACCENT, size=16),
                        ft.Text(session.username, size=13, color=ACCENT),
                    ], spacing=6, tight=True),
                    bgcolor="#0d1520", border_radius=20,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border=ft.border.all(1, BORDER),
                    on_click=lambda _: navigate("/profile"),
                    tooltip="Профіль та мої бронювання",
                ),
                ft.IconButton(icon=ft.Icons.LOGOUT, icon_color=MUTED,
                              tooltip="Вийти",
                              on_click=lambda _: (session.logout(), navigate("/auth"))),
            ], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor=CARD, padding=ft.padding.symmetric(horizontal=24, vertical=14),
        border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
    )

    body = ft.Container(
        content=ft.Column([
            ft.Text("Матчі та події", size=28, weight=ft.FontWeight.BOLD,
                    color=TEXT, font_family="Rajdhani"),
            ft.Text("Оберіть матч і забронюйте місце", size=13, color=MUTED),
            ft.Divider(height=8, color="transparent"),
            filter_row,
            ft.Divider(height=4, color="transparent"),
            ft.Column([matches_wrap], scroll=ft.ScrollMode.AUTO, expand=True),
        ], spacing=10, expand=True),
        padding=ft.padding.symmetric(horizontal=24, vertical=20),
        expand=True,
    )

    return ft.Column([navbar, body], spacing=0, expand=True)
