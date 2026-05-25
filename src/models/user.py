from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    username: str
    password: str
    email: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(d: dict) -> "User":
        return User(
            username=d["username"],
            password=d["password"],
            email=d["email"],
            created_at=d.get("created_at", ""),
        )
