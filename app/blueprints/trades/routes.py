from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.blueprints.trades import trades_bp
from app.blueprints.trades.forms import TradeForm, SearchForm
from app.services import get_trade_service
from app import csrf


@trades_bp.route('/', methods=['GET'])
@login_required
def list_trades():
    svc = get_trade_service()
    form = SearchForm(request.args, meta={'csrf': False})

    filters = {}
    if form.instrument.data:
        filters['instrument'] = form.instrument.data
    if form.direction.data:
        filters['direction'] = form.direction.data
    if form.status.data:
        filters['status'] = form.status.data
    if form.flagged_only.data == '1':
        filters['flagged_only'] = True

    trades = svc.search(current_user.id, **filters) if filters else svc.get_all(current_user.id)

    return render_template('trades/list.html', trades=trades, form=form)


@trades_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = TradeForm()
    if form.validate_on_submit():
        svc = get_trade_service()
        svc.create(current_user.id, {
            'instrument': form.instrument.data,
            'direction': form.direction.data,
            'setup': form.setup.data,
            'status': form.status.data,
            'session': form.session.data,
            'trade_date': form.trade_date.data,
            'entry_price': form.entry_price.data,
            'stop_loss': form.stop_loss.data,
            'take_profit': form.take_profit.data,
            'exit_price': form.exit_price.data,
            'position_size': form.position_size.data,
            'notes': form.notes.data,
        })
        flash('Trade logged successfully.', 'success')
        return redirect(url_for('trades.list_trades'))
    return render_template('trades/create.html', form=form)


@trades_bp.route('/<int:trade_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(trade_id):
    svc = get_trade_service()
    trade = svc.get_by_id(trade_id, current_user.id)
    if not trade:
        flash('Trade not found.', 'danger')
        return redirect(url_for('trades.list_trades'))

    form = TradeForm(obj=trade)
    if form.validate_on_submit():
        svc.update(trade, {
            'instrument': form.instrument.data,
            'direction': form.direction.data,
            'setup': form.setup.data,
            'status': form.status.data,
            'session': form.session.data,
            'trade_date': form.trade_date.data,
            'entry_price': form.entry_price.data,
            'stop_loss': form.stop_loss.data,
            'take_profit': form.take_profit.data,
            'exit_price': form.exit_price.data,
            'position_size': form.position_size.data,
            'notes': form.notes.data,
        })
        flash('Trade updated.', 'success')
        return redirect(url_for('trades.list_trades'))
    return render_template('trades/edit.html', form=form, trade=trade)


@trades_bp.route('/<int:trade_id>/delete', methods=['POST'])
@login_required
def delete(trade_id):
    svc = get_trade_service()
    deleted = svc.delete(trade_id, current_user.id)
    if deleted:
        flash('Trade deleted.', 'info')
    else:
        flash('Trade not found.', 'danger')
    return redirect(url_for('trades.list_trades'))


@trades_bp.route('/<int:trade_id>/flag', methods=['POST'])
@login_required
@csrf.exempt
def toggle_flag(trade_id):
    svc = get_trade_service()
    flagged = svc.toggle_flag(trade_id, current_user.id)
    return jsonify({'flagged': flagged})
