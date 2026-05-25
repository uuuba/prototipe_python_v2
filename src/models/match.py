from dataclasses import dataclass, field


@dataclass
class Seat:
    id: str
    row: str
    number: int
    zone: str
    booked: bool = False

    def to_dict(self) -> dict:
        return {"id": self.id, "row": self.row,
                "number": self.number, "zone": self.zone, "booked": self.booked}

    @staticmethod
    def from_dict(d: dict) -> "Seat":
        return Seat(id=d["id"], row=d["row"],
                    number=d["number"], zone=d["zone"], booked=d["booked"])


@dataclass
class Match:
    id: str
    sport: str
    home: str
    away: str
    date: str
    time: str
    stadium: str
    city: str
    category: str
    seats: list[Seat] = field(default_factory=list)
    price_zones: dict = field(default_factory=dict)   # {"A": 800, "B": 500, "C": 250}

    @property
    def free_seats(self) -> int:
        return sum(1 for s in self.seats if not s.booked)

    @property
    def min_price(self) -> int:
        return min(self.price_zones.values()) if self.price_zones else 0

    def to_dict(self) -> dict:
        return {
            "id": self.id, "sport": self.sport,
            "home": self.home, "away": self.away,
            "date": self.date, "time": self.time,
            "stadium": self.stadium, "city": self.city,
            "category": self.category,
            "seats": [s.to_dict() for s in self.seats],
            "price_zones": self.price_zones,
        }

    @staticmethod
    def from_dict(d: dict) -> "Match":
        return Match(
            id=d["id"], sport=d["sport"],
            home=d["home"], away=d["away"],
            date=d["date"], time=d["time"],
            stadium=d["stadium"], city=d["city"],
            category=d["category"],
            seats=[Seat.from_dict(s) for s in d.get("seats", [])],
            price_zones=d.get("price_zones", {}),
        )
