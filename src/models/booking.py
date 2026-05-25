from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Booking:
    id: str
    username: str
    match_id: str
    seat_id: str
    zone: str
    price: int
    match_info: dict = field(default_factory=dict)
    booked_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "match_id": self.match_id,
            "seat_id": self.seat_id,
            "zone": self.zone,
            "price": self.price,
            "match_info": self.match_info,
            "booked_at": self.booked_at,
        }

    @staticmethod
    def from_dict(d: dict) -> "Booking":
        return Booking(
            id=d["id"], username=d["username"],
            match_id=d["match_id"], seat_id=d["seat_id"],
            zone=d["zone"], price=d["price"],
            match_info=d.get("match_info", {}),
            booked_at=d.get("booked_at", ""),
        )
