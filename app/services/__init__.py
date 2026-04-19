from app.services.trade_service import TradeService
from app.services.user_service import UserService
from app.repository import get_trade_repo, get_user_repo


def get_trade_service() -> TradeService:
    return TradeService(get_trade_repo())


def get_user_service() -> UserService:
    return UserService(get_user_repo())