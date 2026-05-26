import flet as ft
from src.core.session import Session
from src.ui.auth_page import AuthPage
from src.ui.home_page import HomePage
from src.ui.my_bookings_page import MyBookingsPage
from src.ui.profile_page import ProfilePage
from src.ui.admin_page import AdminPage


def main(page: ft.Page) -> None:
    page.title       = "SportBook — Бронювання місць"
    page.theme_mode  = ft.ThemeMode.DARK
    page.bgcolor     = "#0a0e1a"
    page.padding     = 0
    page.fonts       = {
        "Rajdhani": "https://fonts.gstatic.com/s/rajdhani/v15/LDIxapCSOBg7S-QT7pasEcOsc-bGkqIw.woff2",
        "Exo2":     "https://fonts.gstatic.com/s/exo2/v21/7cH1v4okm5zmbvwkAx_sfcEuiD8jvvKcPtq6H.woff2",
    }
    page.theme = ft.Theme(font_family="Exo2")

    session = Session()

    _ROUTES = {
        "/auth":        lambda: AuthPage(page, session, navigate),
        "/home":        lambda: HomePage(page, session, navigate),
        "/my-bookings": lambda: MyBookingsPage(page, session, navigate),
        "/profile":     lambda: ProfilePage(page, session, navigate),
        "/admin": lambda: AdminPage(page, session, navigate),
    }

    def navigate(route: str) -> None:
        page.controls.clear()
        builder = _ROUTES.get(route)
        if builder:
            page.controls.append(builder())
        page.update()

    navigate("/auth")

if __name__ == '__main__':
        ft.run(main, view=ft.AppView.WEB_BROWSER)