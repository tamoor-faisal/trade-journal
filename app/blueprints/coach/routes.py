from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.blueprints.coach import coach_bp
from app.services import get_trade_service
from app.services.ai_services import get_session_feedback, get_trade_feedback
from app.models import db, TradeFeedback


@coach_bp.route('/')
@login_required
def index():
    svc = get_trade_service()
    trades = svc.get_all(current_user.id)
    stats = svc.get_stats(current_user.id)

    # Load latest session feedback if it exists
    session_feedback = TradeFeedback.query.filter_by(
        user_id=current_user.id,
        feedback_type='session'
    ).order_by(TradeFeedback.created_at.desc()).first()

    return render_template(
        'coach/index.html',
        trades=trades,
        stats=stats,
        session_feedback=session_feedback,
    )


@coach_bp.route('/session-debrief', methods=['POST'])
@login_required
def session_debrief():
    svc = get_trade_service()
    trades = svc.get_all(current_user.id)
    stats = svc.get_stats(current_user.id)

    feedback_text = get_session_feedback(trades, stats, current_user.username)

    # Save to DB (replace previous session feedback)
    existing = TradeFeedback.query.filter_by(
        user_id=current_user.id,
        feedback_type='session'
    ).first()

    if existing:
        existing.content = feedback_text
        from datetime import datetime, timezone
        existing.created_at = datetime.now(timezone.utc)
    else:
        fb = TradeFeedback(
            user_id=current_user.id,
            feedback_type='session',
            content=feedback_text
        )
        db.session.add(fb)

    db.session.commit()
    flash('Session debrief updated.', 'success')
    return redirect(url_for('coach.index'))


@coach_bp.route('/trade/<int:trade_id>', methods=['POST'])
@login_required
def trade_feedback(trade_id):
    svc = get_trade_service()
    trade = svc.get_by_id(trade_id, current_user.id)
    if not trade:
        flash('Trade not found.', 'danger')
        return redirect(url_for('trades.list_trades'))

    feedback_text = get_trade_feedback(trade)

    # Save or update feedback for this trade
    existing = TradeFeedback.query.filter_by(
        trade_id=trade_id,
        feedback_type='trade'
    ).first()

    if existing:
        existing.content = feedback_text
        from datetime import datetime, timezone
        existing.created_at = datetime.now(timezone.utc)
    else:
        fb = TradeFeedback(
            trade_id=trade_id,
            user_id=current_user.id,
            feedback_type='trade',
            content=feedback_text
        )
        db.session.add(fb)

    db.session.commit()
    flash('AI feedback generated.', 'success')
    return redirect(url_for('trades.edit', trade_id=trade_id))
