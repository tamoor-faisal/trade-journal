from flask import Blueprint

coach_bp = Blueprint('coach', __name__, template_folder='../../templates/coach')

from app.blueprints.coach import routes  # noqa: E402, F401
