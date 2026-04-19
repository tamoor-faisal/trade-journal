from app.repository.abstract import AbstractTradeRepository, AbstractUserRepository
from app.models import db, Trade, User
from typing import List


class SQLiteTradeRepository(AbstractTradeRepository):

    def get_all_by_user(self, user_id: int) -> List[Trade]:
        return Trade.query.filter_by(user_id=user_id)\
                          .order_by(Trade.trade_date.desc())\
                          .all()

    def get_by_id(self, trade_id: int, user_id: int):
        return Trade.query.filter_by(id=trade_id, user_id=user_id).first()

    def add(self, trade: Trade) -> None:
        db.session.add(trade)
        db.session.commit()

    def update(self, trade: Trade) -> None:
        db.session.commit()

    def delete(self, trade_id: int, user_id: int) -> bool:
        trade = self.get_by_id(trade_id, user_id)
        if not trade:
            return False
        db.session.delete(trade)
        db.session.commit()
        return True

    def search(self, user_id: int, instrument: str = None,
               direction: str = None, status: str = None,
               flagged_only: bool = False) -> List[Trade]:
        query = Trade.query.filter_by(user_id=user_id)
        if instrument:
            query = query.filter(Trade.instrument.ilike(f'%{instrument}%'))
        if direction:
            query = query.filter_by(direction=direction)
        if status:
            query = query.filter_by(status=status)
        if flagged_only:
            query = query.filter_by(is_flagged=True)
        return query.order_by(Trade.trade_date.desc()).all()

    def get_flagged(self, user_id: int) -> List[Trade]:
        return Trade.query.filter_by(user_id=user_id, is_flagged=True)\
                          .order_by(Trade.trade_date.desc())\
                          .all()


class SQLiteUserRepository(AbstractUserRepository):

    def get_by_id(self, user_id: int):
        return User.query.get(user_id)

    def get_by_email(self, email: str):
        return User.query.filter_by(email=email).first()

    def get_by_username(self, username: str):
        return User.query.filter_by(username=username).first()

    def add(self, user: User) -> None:
        db.session.add(user)
        db.session.commit()
