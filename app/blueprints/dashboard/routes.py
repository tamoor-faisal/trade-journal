from flask import render_template
from flask_login import login_required, current_user
from app.blueprints.dashboard import dashboard_bp
from app.services import get_trade_service


@dashboard_bp.route('/')
@login_required
def index():
    svc = get_trade_service()
    stats = svc.get_stats(current_user.id)
    recent_trades = svc.get_all(current_user.id)[:5]
    flagged = svc.get_flagged(current_user.id)[:5]

    # Build equity curve data for chart (cumulative PnL)
    all_closed = [t for t in svc.get_all(current_user.id)
                  if t.status == 'CLOSED' and t.pnl is not None]
    all_closed.sort(key=lambda t: t.trade_date)
    cumulative = 0
    equity_curve = []
    for t in all_closed:
        cumulative += t.pnl
        equity_curve.append({
            'date': t.trade_date.strftime('%d %b'),
            'pnl': round(cumulative, 2)
        })

    return render_template(
        'dashboard/index.html',
        stats=stats,
        recent_trades=recent_trades,
        flagged=flagged,
        equity_curve=equity_curve
    )