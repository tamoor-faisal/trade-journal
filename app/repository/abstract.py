from abc import ABC, abstractmethod
from typing import List, Optional


class AbstractTradeRepository(ABC):

    @abstractmethod
    def get_all_by_user(self, user_id: int) -> List:
        """Return all trades for a given user."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, trade_id: int, user_id: int):
        """Return a single trade by ID, scoped to user."""
        raise NotImplementedError

    @abstractmethod
    def add(self, trade) -> None:
        """Persist a new trade."""
        raise NotImplementedError

    @abstractmethod
    def update(self, trade) -> None:
        """Persist changes to an existing trade."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, trade_id: int, user_id: int) -> bool:
        """Delete a trade. Returns True if deleted, False if not found."""
        raise NotImplementedError

    @abstractmethod
    def search(self, user_id: int, instrument: str = None,
               direction: str = None, status: str = None,
               flagged_only: bool = False) -> List:
        """Search/filter trades for a user."""
        raise NotImplementedError

    @abstractmethod
    def get_flagged(self, user_id: int) -> List:
        """Return all flagged (notable) trades for a user."""
        raise NotImplementedError


class AbstractUserRepository(ABC):

    @abstractmethod
    def get_by_id(self, user_id: int):
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: str):
        raise NotImplementedError

    @abstractmethod
    def get_by_username(self, username: str):
        raise NotImplementedError

    @abstractmethod
    def add(self, user) -> None:
        raise NotImplementedError