import hashlib
from src.core.config import USERS_FILE
from src.models import User
from src.services.storage import load_json, save_json


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register(username: str, password: str, email: str) -> tuple[bool, str]:
    users_raw = load_json(USERS_FILE)
    if any(u["username"] == username for u in users_raw):
        return False, "Користувач з таким іменем вже існує"
    if any(u["email"] == email for u in users_raw):
        return False, "Email вже використовується"
    user = User(username=username, password=_hash(password), email=email)
    users_raw.append(user.to_dict())
    save_json(USERS_FILE, users_raw)
    return True, "Реєстрація успішна"


def login(username: str, password: str) -> tuple[bool, User | str]:
    for u in load_json(USERS_FILE):
        if u["username"] == username and u["password"] == _hash(password):
            return True, User.from_dict(u)
    return False, "Невірне ім'я користувача або пароль"
