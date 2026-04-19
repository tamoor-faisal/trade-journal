from flask import Blueprint

trades_bp = Blueprint('trades', __name__, template_folder='../../templates/trades')

from app.blueprints.trades import routes  # noqa: E402, F401