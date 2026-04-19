from app.repository.abstract import AbstractTradeRepository, AbstractUserRepository
from typing import List, Optional
from copy import deepcopy


class InMemoryTradeRepository(AbstractTradeRepository):

    def __init__(self):
        self._trades = {}
        self._next_id = 1

    def get_all_by_user(self, user_id: int) -> List:
        return sorted(
            [t for t in self._trades.values() if t.user_id == user_id],
            key=lambda t: t.trade_date,
            reverse=True
        )

    def get_by_id(self, trade_id: int, user_id: int):
        trade = self._trades.get(trade_id)
        if trade and trade.user_id == user_id:
            return trade
        return None

    def add(self, trade) -> None:
        trade.id = self._next_id
        self._trades[self._next_id] = trade
        self._next_id += 1

    def update(self, trade) -> None:
        if trade.id in self._trades:
            self._trades[trade.id] = trade

    def delete(self, trade_id: int, user_id: int) -> bool:
        trade = self.get_by_id(trade_id, user_id)
        if not trade:
            return False
        del self._trades[trade_id]
        return True

    def search(self, user_id: int, instrument: str = None,
               direction: str = None, status: str = None,
               flagged_only: bool = False) -> List:
        results = self.get_all_by_user(user_id)
        if instrument:
            results = [t for t in results if instrument.lower() in t.instrument.lower()]
        if direction:
            results = [t for t in results if t.direction == direction]
        if status:
            results = [t for t in results if t.status == status]
        if flagged_only:
            results = [t for t in results if t.is_flagged]
        return results

    def get_flagged(self, user_id: int) -> List:
        return [t for t in self.get_all_by_user(user_id) if t.is_flagged]


class InMemoryUserRepository(AbstractUserRepository):

    def __init__(self):
        self._users = {}
        self._next_id = 1

    def get_by_id(self, user_id: int):
        return self._users.get(user_id)

    def get_by_email(self, email: str):
        return next((u for u in self._users.values() if u.email == email), None)

    def get_by_username(self, username: str):
        return next((u for u in self._users.values() if u.username == username), None)

    def add(self, user) -> None:
        user.id = self._next_id
        self._users[self._next_id] = user
        self._next_id += 1