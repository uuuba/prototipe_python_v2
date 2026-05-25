import random
from src.core.config import MATCHES_FILE
from src.models import Match, Seat
from src.services.storage import load_json, save_json




def _gen_seats(count: int) -> list[dict]:
    rows = ["A", "B", "C", "D", "E", "F"]
    per_row = count // len(rows)
    rng = random.Random(42)
    seats = []
    for row in rows:
        for num in range(1, per_row + 1):
            zone = "A" if row in ("A", "B") else ("B" if row in ("C", "D") else "C")
            seats.append(Seat(
                id=f"{row}{num}", row=row, number=num,
                zone=zone, booked=rng.random() < 0.3
            ).to_dict())
    return seats


_SEED: list[dict] = [
    {"id": "m1", "sport": "⚽ Футбол",    "home": "Динамо Київ",     "away": "Шахтар",
     "date": "2025-06-14", "time": "18:00", "stadium": "НСК Олімпійський", "city": "Київ",
     "category": "Прем'єр-ліга",  "price_zones": {"A": 800, "B": 500, "C": 250}},
    {"id": "m2", "sport": "🏀 Баскетбол", "home": "Будівельник",     "away": "Київ-Баскет",
     "date": "2025-06-18", "time": "19:30", "stadium": "Палац спорту",      "city": "Київ",
     "category": "Суперліга",     "price_zones": {"A": 600, "B": 350, "C": 150}},
    {"id": "m3", "sport": "⚽ Футбол",    "home": "Карпати",          "away": "Металіст",
     "date": "2025-06-21", "time": "17:00", "stadium": "Арена Львів",        "city": "Львів",
     "category": "Прем'єр-ліга",  "price_zones": {"A": 700, "B": 400, "C": 200}},
    {"id": "m4", "sport": "🏐 Волейбол",  "home": "Барком-Кажани",   "away": "Решетилівка",
     "date": "2025-06-25", "time": "16:00", "stadium": "СК Електрон",        "city": "Львів",
     "category": "Суперліга",     "price_zones": {"A": 400, "B": 250, "C": 100}},
    {"id": "m5", "sport": "🥊 Бокс",      "home": "Олександр Усик",  "away": "Даніель Дюбуа",
     "date": "2025-07-05", "time": "20:00", "stadium": "Палац Україна",       "city": "Київ",
     "category": "Чемпіонат світу WBA", "price_zones": {"A": 2000, "B": 1200, "C": 600}},
    {"id": "m6", "sport": "🎾 Теніс",     "home": "Еліна Світоліна", "away": "Ірина Бегу",
     "date": "2025-07-10", "time": "14:00", "stadium": "Тенісний центр",      "city": "Одеса",
     "category": "WTA 250",       "price_zones": {"A": 500, "B": 300, "C": 120}},
]


def _ensure_matches() -> None:
    import os
    if not os.path.exists(MATCHES_FILE):
        data = [{**m, "seats": _gen_seats(50 if "Футбол" in m["sport"] else 30)}
                for m in _SEED]
        save_json(MATCHES_FILE, data)




def get_all() -> list[Match]:
    _ensure_matches()
    return [Match.from_dict(d) for d in load_json(MATCHES_FILE)]


def get_by_id(match_id: str) -> Match | None:
    for m in get_all():
        if m.id == match_id:
            return m
    return None


def save_match(match: Match) -> None:
    matches_raw = load_json(MATCHES_FILE)
    for i, m in enumerate(matches_raw):
        if m["id"] == match.id:
            matches_raw[i] = match.to_dict()
            break
    save_json(MATCHES_FILE, matches_raw)
