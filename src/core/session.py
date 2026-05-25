from src.models import User


class Session:
    """Зберігає стан поточного авторизованого користувача."""

    def __init__(self):
        self._user: User | None = None

    def login(self, user: User) -> None:
        self._user = user

    def logout(self) -> None:
        self._user = None

    @property
    def is_logged_in(self) -> bool:
        return self._user is not None

    @property
    def username(self) -> str:
        return self._user.username if self._user else ""

    @property
    def current_user(self) -> User | None:
        return self._user
