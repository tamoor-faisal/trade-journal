from app.models import User


class UserService:

    def __init__(self, user_repo):
        self.repo = user_repo

    def register(self, username: str, email: str, password: str):
        """Register a new user. Returns (user, error_message)."""
        if self.repo.get_by_email(email):
            return None, 'An account with that email already exists.'
        if self.repo.get_by_username(username):
            return None, 'That username is already taken.'
        user = User(username=username, email=email)
        user.set_password(password)
        self.repo.add(user)
        return user, None

    def authenticate(self, email: str, password: str):
        """Authenticate a user. Returns (user, error_message)."""
        user = self.repo.get_by_email(email)
        if not user or not user.check_password(password):
            return None, 'Invalid email or password.'
        return user, None

    def get_by_id(self, user_id: int):
        return self.repo.get_by_id(user_id)
