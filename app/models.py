from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    trades = db.relationship('Trade', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Trade(db.Model):
    __tablename__ = 'trades'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Core trade info
    instrument = db.Column(db.String(20), nullable=False)
    direction = db.Column(db.String(5), nullable=False)       # LONG / SHORT
    setup = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(10), nullable=False, default='OPEN')  # OPEN / CLOSED

    # Entry & exit
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float, nullable=True)
    stop_loss = db.Column(db.Float, nullable=False)
    take_profit = db.Column(db.Float, nullable=True)
    position_size = db.Column(db.Float, nullable=False)

    # Outcome
    pnl = db.Column(db.Float, nullable=True)
    r_multiple = db.Column(db.Float, nullable=True)

    # Session & metadata
    session = db.Column(db.String(20), nullable=True)         # London, NY, Asia
    notes = db.Column(db.Text, nullable=True)
    is_flagged = db.Column(db.Boolean, default=False)         # favourite/notable

    # Timestamps
    trade_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime,
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def calculate_r_multiple(self):
        """Calculate R-multiple based on entry, exit, and stop loss."""
        if self.exit_price is None:
            return None
        risk = abs(self.entry_price - self.stop_loss)
        if risk == 0:
            return None
        if self.direction == 'LONG':
            reward = self.exit_price - self.entry_price
        else:
            reward = self.entry_price - self.exit_price
        return round(reward / risk, 2)

    def __repr__(self):
        return f'<Trade {self.instrument} {self.direction} {self.trade_date}>'