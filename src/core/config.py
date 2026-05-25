import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
BOOKINGS_FILE = os.path.join(DATA_DIR, "bookings.json")
MATCHES_FILE = os.path.join(DATA_DIR, "matches.json")


BG       = "#0a0e1a"
CARD     = "#111827"
CARD2    = "#0d1520"
BORDER   = "#1e2d45"
TEXT     = "#e8eaf0"
MUTED    = "#6b7a99"
ACCENT   = "#00d4ff"
ACCENT2  = "#ff6b35"
SUCCESS  = "#00c896"
DANGER   = "#ff4d6d"

ZONE_COLORS: dict[str, str] = {
    "A": "#ff6b35",
    "B": "#00d4ff",
    "C": "#a78bfa",
}


APP_NAME    = "SportBook"
APP_VERSION = "1.0.0"
