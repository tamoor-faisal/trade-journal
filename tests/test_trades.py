import pytest
from datetime import date
from tests.conftest import register_user, login_user


TRADE_DATA = {
    'instrument': 'BTC/USD',
    'direction': 'LONG',
    'setup': 'Break of Structure',
    'status': 'OPEN',
    'session': 'London',
    'trade_date': date.today().isoformat(),
    'entry_price': '65000.0',
    'stop_loss': '64000.0',
    'take_profit': '67000.0',
    'exit_price': '',
    'position_size': '0.1',
    'notes': 'Clean BOS on 4H',
}


@pytest.fixture
def logged_in_client(client):
    register_user(client)
    login_user(client)
    return client


class TestTradeCreation:

    def test_create_trade_success(self, logged_in_client):
        response = logged_in_client.post('/trades/create', data=TRADE_DATA, follow_redirects=True)
        assert response.status_code == 200
        assert b'BTC/USD' in response.data

    def test_create_trade_unauthenticated(self, client):
        response = client.post('/trades/create', data=TRADE_DATA, follow_redirects=False)
        assert response.status_code == 302

    def test_create_closed_trade_calculates_pnl(self, logged_in_client):
        data = {**TRADE_DATA, 'exit_price': '66000.0', 'status': 'CLOSED'}
        response = logged_in_client.post('/trades/create', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'CLOSED' in response.data

    def test_create_trade_missing_instrument(self, logged_in_client):
        data = {**TRADE_DATA, 'instrument': ''}
        response = logged_in_client.post('/trades/create', data=data, follow_redirects=True)
        assert b'Trade logged' not in response.data


class TestTradeList:

    def test_list_shows_user_trades(self, logged_in_client):
        logged_in_client.post('/trades/create', data=TRADE_DATA, follow_redirects=True)
        response = logged_in_client.get('/trades/')
        assert b'BTC/USD' in response.data

    def test_list_search_by_instrument(self, logged_in_client):
        logged_in_client.post('/trades/create', data=TRADE_DATA, follow_redirects=True)
        nq_data = {**TRADE_DATA, 'instrument': 'NQ1!'}
        logged_in_client.post('/trades/create', data=nq_data, follow_redirects=True)
        response = logged_in_client.get('/trades/?instrument=NQ')
        assert b'NQ1!' in response.data
        assert b'BTC/USD' not in response.data

    def test_list_filter_by_direction(self, logged_in_client):
        logged_in_client.post('/trades/create', data=TRADE_DATA, follow_redirects=True)
        short_data = {**TRADE_DATA, 'instrument': 'EUR/USD', 'direction': 'SHORT'}
        logged_in_client.post('/trades/create', data=short_data, follow_redirects=True)
        response = logged_in_client.get('/trades/?direction=SHORT')
        assert b'EUR/USD' in response.data
        assert b'BTC/USD' not in response.data


class TestTradeEdit:

    def test_edit_trade(self, logged_in_client):
        logged_in_client.post('/trades/create', data=TRADE_DATA, follow_redirects=True)
        response = logged_in_client.get('/trades/')
        # Edit trade id=1
        updated = {**TRADE_DATA, 'instrument': 'ETH/USD'}
        response = logged_in_client.post('/trades/1/edit', data=updated, follow_redirects=True)
        assert response.status_code == 200

    def test_edit_nonexistent_trade(self, logged_in_client):
        response = logged_in_client.post('/trades/9999/edit', data=TRADE_DATA, follow_redirects=True)
        assert b'not found' in response.data


class TestTradeDelete:

    def test_delete_trade(self, logged_in_client):
        logged_in_client.post('/trades/create', data=TRADE_DATA, follow_redirects=True)
        response = logged_in_client.post('/trades/1/delete', follow_redirects=True)
        assert response.status_code == 200
        assert b'deleted' in response.data

    def test_delete_nonexistent_trade(self, logged_in_client):
        response = logged_in_client.post('/trades/9999/delete', follow_redirects=True)
        assert b'not found' in response.data


class TestTradeService:
    """Unit tests for the trade service using in-memory repo."""

    def test_r_multiple_long(self, app):
        from app.services.trade_service import TradeService
        from app.repository.memory_repo import InMemoryTradeRepository
        from app.models import Trade

        with app.app_context():
            svc = TradeService(InMemoryTradeRepository())
            trade = Trade(
                user_id=1,
                instrument='BTC/USD',
                direction='LONG',
                setup='BOS',
                status='CLOSED',
                entry_price=65000,
                exit_price=67000,
                stop_loss=64000,
                position_size=0.1,
                trade_date=date.today(),
            )
            r = trade.calculate_r_multiple()
            assert r == 2.0

    def test_r_multiple_short(self, app):
        from app.models import Trade

        with app.app_context():
            trade = Trade(
                user_id=1,
                instrument='NQ1!',
                direction='SHORT',
                setup='FVG',
                status='CLOSED',
                entry_price=18000,
                exit_price=17500,
                stop_loss=18250,
                position_size=1,
                trade_date=date.today(),
            )
            r = trade.calculate_r_multiple()
            assert r == 2.0

    def test_stats_empty(self, app):
        from app.services.trade_service import TradeService
        from app.repository.memory_repo import InMemoryTradeRepository

        with app.app_context():
            svc = TradeService(InMemoryTradeRepository())
            stats = svc.get_stats(user_id=99)
            assert stats['total_trades'] == 0
            assert stats['win_rate'] == 0
            assert stats['total_pnl'] == 0
