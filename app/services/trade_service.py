from app.models import Trade
from datetime import date


class TradeService:

    def __init__(self, trade_repo):
        self.repo = trade_repo

    def get_all(self, user_id: int):
        return self.repo.get_all_by_user(user_id)

    def get_by_id(self, trade_id: int, user_id: int):
        return self.repo.get_by_id(trade_id, user_id)

    def create(self, user_id: int, form_data: dict) -> Trade:
        trade = Trade(
            user_id=user_id,
            instrument=form_data['instrument'].upper(),
            direction=form_data['direction'],
            setup=form_data['setup'],
            status=form_data.get('status', 'OPEN'),
            entry_price=float(form_data['entry_price']),
            stop_loss=float(form_data['stop_loss']),
            take_profit=float(form_data['take_profit']) if form_data.get('take_profit') else None,
            position_size=float(form_data['position_size']),
            session=form_data.get('session'),
            notes=form_data.get('notes'),
            trade_date=form_data.get('trade_date', date.today()),
        )
        if form_data.get('exit_price'):
            trade.exit_price = float(form_data['exit_price'])
            trade.pnl = self._calculate_pnl(trade)
            trade.r_multiple = trade.calculate_r_multiple()
        self.repo.add(trade)
        return trade

    def update(self, trade: Trade, form_data: dict) -> Trade:
        trade.instrument = form_data['instrument'].upper()
        trade.direction = form_data['direction']
        trade.setup = form_data['setup']
        trade.status = form_data.get('status', trade.status)
        trade.entry_price = float(form_data['entry_price'])
        trade.stop_loss = float(form_data['stop_loss'])
        trade.take_profit = float(form_data['take_profit']) if form_data.get('take_profit') else None
        trade.position_size = float(form_data['position_size'])
        trade.session = form_data.get('session')
        trade.notes = form_data.get('notes')
        if form_data.get('trade_date'):
            trade.trade_date = form_data['trade_date']
        if form_data.get('exit_price'):
            trade.exit_price = float(form_data['exit_price'])
            trade.pnl = self._calculate_pnl(trade)
            trade.r_multiple = trade.calculate_r_multiple()
        else:
            trade.exit_price = None
            trade.pnl = None
            trade.r_multiple = None
        self.repo.update(trade)
        return trade

    def delete(self, trade_id: int, user_id: int) -> bool:
        return self.repo.delete(trade_id, user_id)

    def toggle_flag(self, trade_id: int, user_id: int) -> bool:
        trade = self.repo.get_by_id(trade_id, user_id)
        if not trade:
            return False
        trade.is_flagged = not trade.is_flagged
        self.repo.update(trade)
        return trade.is_flagged

    def search(self, user_id: int, **filters):
        return self.repo.search(user_id, **filters)

    def get_flagged(self, user_id: int):
        return self.repo.get_flagged(user_id)

    def get_stats(self, user_id: int) -> dict:
        """Compute summary statistics for the dashboard."""
        trades = self.get_all(user_id)
        closed = [t for t in trades if t.status == 'CLOSED' and t.pnl is not None]

        if not closed:
            return {
                'total_trades': len(trades),
                'closed_trades': 0,
                'open_trades': len([t for t in trades if t.status == 'OPEN']),
                'win_rate': 0,
                'total_pnl': 0,
                'avg_r': 0,
                'wins': 0,
                'losses': 0,
            }

        wins = [t for t in closed if t.pnl > 0]
        losses = [t for t in closed if t.pnl <= 0]
        r_multiples = [t.r_multiple for t in closed if t.r_multiple is not None]

        return {
            'total_trades': len(trades),
            'closed_trades': len(closed),
            'open_trades': len([t for t in trades if t.status == 'OPEN']),
            'win_rate': round(len(wins) / len(closed) * 100, 1) if closed else 0,
            'total_pnl': round(sum(t.pnl for t in closed), 2),
            'avg_r': round(sum(r_multiples) / len(r_multiples), 2) if r_multiples else 0,
            'wins': len(wins),
            'losses': len(losses),
        }

    def _calculate_pnl(self, trade: Trade) -> float:
        if trade.exit_price is None:
            return 0.0
        if trade.direction == 'LONG':
            pnl = (trade.exit_price - trade.entry_price) * trade.position_size
        else:
            pnl = (trade.entry_price - trade.exit_price) * trade.position_size
        return round(pnl, 2)
