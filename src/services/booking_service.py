from src.core.config import BOOKINGS_FILE
from src.models import Booking
from src.services.storage import load_json, save_json
from src.services import match_service

MAX_SEATS_PER_USER_PER_MATCH = 3


def book_seat(match_id: str, seat_id: str, username: str) -> tuple[bool, str]:
    match = match_service.get_by_id(match_id)
    if not match:
        return False, "Матч не знайдено"

    seat = next((s for s in match.seats if s.id == seat_id), None)
    if not seat:
        return False, "Місце не знайдено"
    if seat.booked:
        return False, "Місце вже заброньовано"

    # Перевірка ліміту: не більше MAX_SEATS_PER_USER_PER_MATCH місць на особу
    bookings_raw = load_json(BOOKINGS_FILE)
    user_match_bookings = [
        b for b in bookings_raw
        if b["username"] == username and b["match_id"] == match_id
    ]
    if len(user_match_bookings) >= MAX_SEATS_PER_USER_PER_MATCH:
        return False, (
            f"Ліміт досягнуто: максимум {MAX_SEATS_PER_USER_PER_MATCH} місця "
            f"на одну особу для цього матчу"
        )

    seat.booked = True
    match_service.save_match(match)

    booking = Booking(
        id=f"b{len(bookings_raw) + 1}",
        username=username,
        match_id=match_id,
        seat_id=seat_id,
        zone=seat.zone,
        price=match.price_zones[seat.zone],
        match_info={
            "sport": match.sport, "home": match.home, "away": match.away,
            "date": match.date,   "time": match.time,
            "stadium": match.stadium, "city": match.city,
        },
    )
    bookings_raw.append(booking.to_dict())
    save_json(BOOKINGS_FILE, bookings_raw)
    return True, f"Місце {seat_id} успішно заброньовано!"


def get_user_bookings(username: str) -> list[Booking]:
    return [Booking.from_dict(b) for b in load_json(BOOKINGS_FILE)
            if b["username"] == username]


def cancel_booking(booking_id: str, username: str) -> tuple[bool, str]:
    bookings_raw = load_json(BOOKINGS_FILE)
    target = next((b for b in bookings_raw
                   if b["id"] == booking_id and b["username"] == username), None)
    if not target:
        return False, "Бронювання не знайдено"

    match = match_service.get_by_id(target["match_id"])
    if match:
        for seat in match.seats:
            if seat.id == target["seat_id"]:
                seat.booked = False
                break
        match_service.save_match(match)

    save_json(BOOKINGS_FILE, [b for b in bookings_raw if b["id"] != booking_id])
    return True, "Бронювання скасовано"


def get_user_match_booking_count(match_id: str, username: str) -> int:
    bookings_raw = load_json(BOOKINGS_FILE)
    return sum(
        1 for b in bookings_raw
        if b["username"] == username and b["match_id"] == match_id
    )
