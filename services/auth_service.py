"""Authentication service: signup, login, password reset, sessions."""
from __future__ import annotations

from typing import Optional

from database import UserRepository
from models.schemas import User
from utils.logger import logger


class AuthService:
    @staticmethod
    def signup(username: str, email: str, password: str) -> tuple[bool, str, Optional[User]]:
        if not username or not email or not password:
            return False, "All fields are required.", None
        if len(password) < 6:
            return False, "Password must be at least 6 characters.", None
        if UserRepository.get_by_username(username):
            return False, "Username already taken.", None
        if UserRepository.get_by_email(email):
            return False, "Email already registered.", None
        try:
            user = UserRepository.create(username, email, password)
            return True, "Account created successfully.", user
        except Exception as exc:  # noqa: BLE001
            logger.error("Signup failed: %s", exc)
            return False, "Could not create account.", None

    @staticmethod
    def login(username: str, password: str) -> tuple[bool, str, Optional[User]]:
        user = UserRepository.verify(username, password)
        if not user:
            return False, "Invalid username or password.", None
        return True, "Logged in.", user

    @staticmethod
    def reset_password(email: str, new_password: str) -> tuple[bool, str]:
        if len(new_password) < 6:
            return False, "Password must be at least 6 characters."
        ok = UserRepository.reset_password(email, new_password)
        if ok:
            return True, "Password reset successfully."
        return False, "No account found with that email."
