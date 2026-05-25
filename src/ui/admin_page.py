import flet as ft
from src.core.config import (ACCENT, ACCENT2, CARD, CARD2, BORDER,
                              TEXT, MUTED, SUCCESS, ZONE_COLORS, DANGER)
from src.core.session import Session
from src.services import match_service, booking_service

_PAID_COLOR   = "#00c896"
_BOOK_COLOR   = ACCENT
_CANCEL_COLOR = DANGER


def AdminPage(page: ft.Page, session: Session, navigate) -> ft.Control:
    # Simple admin check — username "admin"
    if not session.is_logged_in or session.username.lower() != "admin":
        navigate("/home")
        return ft.Container()

    # ── State ──────────────────────────────────────────────────────────────
    tab_index = [0]
    content_col = ft.Column([], expand=True, scroll=ft.ScrollMode.AUTO)

    # ── Helpers ─────────────────────────────────────────────────────────────
    def _stat_card(icon: str, label: str, value: str,
                   color: str = ACCENT) -> ft.Control:
        return ft.Container(
            content=ft.Column([
                ft.Text(icon, size=28),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD,
                        color=color, font_family="Rajdhani"),
                ft.Text(label, size=12, color=MUTED),
            ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=CARD2, border_radius=14, padding=20,
            border=ft.border.all(1, BORDER),
            expand=True,
            alignment=ft.Alignment(0, 0),
        )

    def _badge(text: str, bg: str) -> ft.Control:
        return ft.Container(
            content=ft.Text(text, size=11, color="#0a0e1a",
                            weight=ft.FontWeight.BOLD),
            bgcolor=bg, border_radius=20,
            padding=ft.padding.symmetric(horizontal=10, vertical=3),
        )

    # ── Tab: Загальна статистика ─────────────────────────────────────────────
    def build_overview():
        bookings = booking_service.get_all_bookings()
        matches  = match_service.get_all()

        total_b   = len(bookings)
        paid_b    = sum(1 for b in bookings if b.status == "paid")
        booked_b  = total_b - paid_b
        revenue   = sum(b.price for b in bookings if b.status == "paid")
        reserved  = sum(b.price for b in bookings if b.status == "booked")

        # seats taken per match
        seats_taken = {m.id: sum(1 for s in m.seats if s.booked) for m in matches}
        seats_total = {m.id: len(m.seats) for m in matches}

        # unique users
        users_set = {b.username for b in bookings}

        stats_row = ft.Row([
            _stat_card("🎟", "Всього транзакцій", str(total_b)),
            _stat_card("💳", "Куплено",   str(paid_b),   _PAID_COLOR),
            _stat_card("🔖", "Заброньовано", str(booked_b), _BOOK_COLOR),
            _stat_card("👥", "Покупців",  str(len(users_set)), ACCENT2),
        ], spacing=12)

        money_row = ft.Row([
            _stat_card("💰", "Дохід (куплено)", f"{revenue:,} грн", _PAID_COLOR),
            _stat_card("⏳", "В очікуванні (брон.)", f"{reserved:,} грн", ACCENT2),
            _stat_card("📊", "Разом потенційно",
                       f"{revenue + reserved:,} грн", SUCCESS),
        ], spacing=12)

        # Per-match occupancy table
        rows = []
        for m in matches:
            taken = seats_taken.get(m.id, 0)
            total = seats_total.get(m.id, 1)
            pct   = int(taken / total * 100)
            bar_c = (SUCCESS if pct < 60 else (ACCENT2 if pct < 85 else _CANCEL_COLOR))
            rows.append(ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(f"{m.home} vs {m.away}", size=14, color=TEXT,
                                weight=ft.FontWeight.W_600, font_family="Rajdhani"),
                        ft.Text(f"{m.sport}  ·  {m.date}  ·  {m.city}",
                                size=11, color=MUTED),
                    ], spacing=2, expand=True),
                    ft.Column([
                        ft.Text(f"{taken}/{total} місць ({pct}%)",
                                size=12, color=MUTED),
                        ft.Container(
                            content=ft.Container(
                                bgcolor=bar_c, border_radius=4,
                                width=140 * pct / 100, height=6,
                            ),
                            bgcolor=BORDER, border_radius=4, width=140, height=6,
                        ),
                    ], spacing=4),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=CARD2, border_radius=12, padding=14,
                border=ft.border.all(1, BORDER),
            ))

        match_table = ft.Column(rows, spacing=8)

        content_col.controls = [
            ft.Text("Загальна статистика", size=22, weight=ft.FontWeight.BOLD,
                    color=TEXT, font_family="Rajdhani"),
            ft.Divider(height=6, color="transparent"),
            stats_row,
            ft.Divider(height=6, color="transparent"),
            money_row,
            ft.Divider(height=10, color=BORDER),
            ft.Text("Заповненість по матчах", size=16, color=TEXT,
                    weight=ft.FontWeight.W_600),
            ft.Divider(height=4, color="transparent"),
            match_table,
        ]
        page.update()

    # ── Tab: Всі бронювання ──────────────────────────────────────────────────
    def build_bookings():
        bookings = booking_service.get_all_bookings()
        bookings = list(reversed(bookings))

        if not bookings:
            content_col.controls = [
                ft.Container(
                    content=ft.Text("Бронювань ще немає", size=18, color=MUTED),
                    alignment=ft.Alignment(0, 0), expand=True, padding=60,
                )
            ]
            page.update()
            return

        cards = []
        for b in bookings:
            mi   = b.match_info
            z_c  = ZONE_COLORS.get(b.zone, ACCENT)
            s_c  = _PAID_COLOR if b.status == "paid" else _BOOK_COLOR
            s_lbl = "Куплено" if b.status == "paid" else "Заброньовано"
            date_str = b.booked_at[:16].replace("T", " ") if b.booked_at else ""
            cards.append(ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"{mi.get('sport','')} — "
                                f"{mi.get('home','')} vs {mi.get('away','')}",
                                size=14, color=TEXT, weight=ft.FontWeight.W_600,
                                font_family="Rajdhani", expand=True),
                        _badge(s_lbl, s_c),
                        _badge(f"Зона {b.zone}", z_c),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([
                        ft.Text(f"👤 {b.username}", size=12, color=MUTED),
                        ft.Text(f"🎟 Місце {b.seat_id}", size=12, color=MUTED),
                        ft.Text(f"💰 {b.price} грн", size=12, color=ACCENT2,
                                weight=ft.FontWeight.W_600),
                        ft.Text(f"🕐 {date_str}", size=11, color=MUTED),
                    ], spacing=14, wrap=True),
                ], spacing=6),
                bgcolor=CARD2, border_radius=12, padding=14,
                border=ft.border.all(1, BORDER),
            ))

        content_col.controls = [
            ft.Text("Всі транзакції", size=22, weight=ft.FontWeight.BOLD,
                    color=TEXT, font_family="Rajdhani"),
            ft.Text(f"Всього: {len(bookings)}", size=13, color=MUTED),
            ft.Divider(height=6, color="transparent"),
            ft.Column(cards, spacing=8),
        ]
        page.update()

    # ── Tab: Матчі ───────────────────────────────────────────────────────────
    def build_matches():
        matches = match_service.get_all()
        bookings = booking_service.get_all_bookings()

        b_by_match: dict[str, list] = {}
        for b in bookings:
            b_by_match.setdefault(b.match_id, []).append(b)

        cards = []
        for m in matches:
            mb    = b_by_match.get(m.id, [])
            paid  = sum(1 for b in mb if b.status == "paid")
            book  = sum(1 for b in mb if b.status == "booked")
            rev   = sum(b.price for b in mb if b.status == "paid")
            free  = m.free_seats
            total = len(m.seats)

            cards.append(ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(m.sport, size=12, color=ACCENT),
                        ft.Text(m.category, size=11, color=MUTED),
                    ], spacing=8),
                    ft.Text(f"{m.home} vs {m.away}", size=16,
                            weight=ft.FontWeight.BOLD, color=TEXT,
                            font_family="Rajdhani"),
                    ft.Text(f"📅 {m.date}  🕐 {m.time}  📍 {m.stadium}, {m.city}",
                            size=12, color=MUTED),
                    ft.Divider(height=6, color=BORDER),
                    ft.Row([
                        _stat_mini("Місць всього", str(total)),
                        _stat_mini("Вільних", str(free), SUCCESS),
                        _stat_mini("Куплено", str(paid), _PAID_COLOR),
                        _stat_mini("Заброньовано", str(book), _BOOK_COLOR),
                        _stat_mini("Дохід", f"{rev:,} грн", ACCENT2),
                    ], spacing=8, wrap=True),
                ], spacing=6),
                bgcolor=CARD2, border_radius=14, padding=16,
                border=ft.border.all(1, BORDER),
                shadow=ft.BoxShadow(blur_radius=8, color="#00000040",
                                    offset=ft.Offset(0, 3)),
            ))

        content_col.controls = [
            ft.Text("Матчі", size=22, weight=ft.FontWeight.BOLD,
                    color=TEXT, font_family="Rajdhani"),
            ft.Divider(height=6, color="transparent"),
            ft.Column(cards, spacing=12),
        ]
        page.update()

    # ── Tabs ────────────────────────────────────────────────────────────────
    TAB_LABELS = ["📊 Огляд", "🎟 Транзакції", "🏟 Матчі"]
    TAB_BUILDERS = [build_overview, build_bookings, build_matches]

    tabs_row_ref = ft.Ref[ft.Row]()

    def build_tabs_row():
        tabs = []
        for i, lbl in enumerate(TAB_LABELS):
            active = tab_index[0] == i

            def on_tab(_, idx=i):
                tab_index[0] = idx
                refresh_tabs()
                TAB_BUILDERS[idx]()

            tabs.append(ft.Container(
                content=ft.Text(lbl, size=13,
                                color="#0a0e1a" if active else TEXT,
                                weight=ft.FontWeight.W_600 if active
                                else ft.FontWeight.NORMAL),
                bgcolor=ACCENT if active else CARD2,
                border_radius=20,
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                border=ft.border.all(1, ACCENT if active else BORDER),
                on_click=on_tab,
                animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            ))
        return tabs

    tabs_container = ft.Row([], spacing=8)

    def refresh_tabs():
        tabs_container.controls = build_tabs_row()
        page.update()

    refresh_tabs()
    build_overview()

    # ── Navbar ──────────────────────────────────────────────────────────────
    navbar = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=MUTED,
                              tooltip="На головну",
                              on_click=lambda _: navigate("/home")),
                ft.Container(
                    content=ft.Text("SB", size=14, weight=ft.FontWeight.BOLD,
                                    color="#0a0e1a", font_family="Rajdhani"),
                    bgcolor=ACCENT, border_radius=8,
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                ),
                ft.Text("Адмін-панель", size=17, weight=ft.FontWeight.BOLD,
                        color=TEXT, font_family="Rajdhani"),
            ], spacing=8),
            ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS,
                                color=ACCENT2, size=16),
                        ft.Text(session.username, size=13, color=ACCENT2),
                    ], spacing=6, tight=True),
                    bgcolor="#0d1520", border_radius=20,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border=ft.border.all(1, BORDER),
                ),
                ft.IconButton(icon=ft.Icons.REFRESH, icon_color=MUTED,
                              tooltip="Оновити",
                              on_click=lambda _: TAB_BUILDERS[tab_index[0]]()),
            ], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor=CARD, padding=ft.padding.symmetric(horizontal=24, vertical=14),
        border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
    )

    tabs_bar = ft.Container(
        content=tabs_container,
        bgcolor=CARD, padding=ft.padding.symmetric(horizontal=24, vertical=10),
        border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
    )

    body = ft.Container(
        content=content_col,
        padding=ft.padding.symmetric(horizontal=24, vertical=20),
        expand=True,
    )

    return ft.Column([navbar, tabs_bar, body], spacing=0, expand=True)


def _stat_mini(label: str, value: str,
               color: str = "#e8eaf0") -> ft.Control:
    return ft.Container(
        content=ft.Column([
            ft.Text(value, size=15, color=color,
                    weight=ft.FontWeight.BOLD, font_family="Rajdhani"),
            ft.Text(label, size=10, color="#6b7a99"),
        ], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor="#0a0e1a", border_radius=8, padding=8,
        border=ft.border.all(1, "#1e2d45"),
    )
