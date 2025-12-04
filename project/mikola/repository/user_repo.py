from typing import List, Optional
from werkzeug.security import generate_password_hash
from ..models import User


class UserRepository:
    def __init__(self):
        # Initialize with a default admin user
        # Seed with a default admin user (password: admin123)
        self._users: List[User] = [
            User(
                id=1,
                email="admin@mikola.com",
                password_hash=generate_password_hash("admin123"),
                role="admin",
                first_name="Admin",
                last_name="User"
            )
        ]
        self._next_id = 2

    def get_next_id(self) -> int:
        """Get the next available user ID"""
        current_id = self._next_id
        self._next_id += 1
        return current_id

    def add_user(self, user: User) -> None:
        """Add a new user to the repository"""
        self._users.append(user)

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        for user in self._users:
            if user.id == user_id:
                return user
        return None

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        for user in self._users:
            if user.email == email:
                return user
        return None

    def get_all(self) -> List[User]:
        """Get all users"""
        return self._users.copy()

    def update_user(self, user: User) -> bool:
        """Update an existing user"""
        for i, existing_user in enumerate(self._users):
            if existing_user.id == user.id:
                self._users[i] = user
                return True
        return False

    def delete_user(self, user_id: int) -> bool:
        """Delete a user by ID"""
        for i, user in enumerate(self._users):
            if user.id == user_id:
                del self._users[i]
                return True
        return False


# Global instance
user_repository = UserRepository()

