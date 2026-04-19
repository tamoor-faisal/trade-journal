from flask import Flask
from flask_login import LoginManager
from app.models import db, User
from config import config


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access your journal.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app(config_name='default'):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config[config_name])

    # Initialise extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.trades import trades_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(trades_bp, url_prefix='/trades')

    # Create tables
    with app.app_context():
        db.create_all()

    return app