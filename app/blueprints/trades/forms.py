from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, TextAreaField, SubmitField, DateField
from wtforms.validators import DataRequired, Optional, NumberRange
from datetime import date


class TradeForm(FlaskForm):
    instrument = StringField('Instrument', validators=[DataRequired()],
                             render_kw={'placeholder': 'e.g. BTC/USD, NQ1!, EUR/USD'})
    direction = SelectField('Direction', choices=[('LONG', 'Long'), ('SHORT', 'Short')],
                            validators=[DataRequired()])
    setup = StringField('Setup', validators=[DataRequired()],
                        render_kw={'placeholder': 'e.g. Break of Structure, FVG Retest'})
    status = SelectField('Status', choices=[('OPEN', 'Open'), ('CLOSED', 'Closed')],
                         validators=[DataRequired()])
    session = SelectField('Session', choices=[
        ('', '— Select Session —'),
        ('Asia', 'Asia'),
        ('London', 'London'),
        ('New York', 'New York'),
        ('London Close', 'London Close'),
    ], validators=[Optional()])

    trade_date = DateField('Trade Date', validators=[DataRequired()], default=date.today)
    entry_price = FloatField('Entry Price', validators=[DataRequired(), NumberRange(min=0)])
    stop_loss = FloatField('Stop Loss', validators=[DataRequired(), NumberRange(min=0)])
    take_profit = FloatField('Take Profit', validators=[Optional(), NumberRange(min=0)])
    exit_price = FloatField('Exit Price', validators=[Optional(), NumberRange(min=0)])
    position_size = FloatField('Position Size', validators=[DataRequired(), NumberRange(min=0)],
                               render_kw={'placeholder': 'Units / contracts'})

    notes = TextAreaField('Notes', validators=[Optional()],
                          render_kw={'placeholder': 'What did you observe? What went well?', 'rows': 4})
    submit = SubmitField('Save Trade')


class SearchForm(FlaskForm):
    instrument = StringField('Instrument', validators=[Optional()])
    direction = SelectField('Direction', choices=[
        ('', 'Any'), ('LONG', 'Long'), ('SHORT', 'Short')
    ], validators=[Optional()])
    status = SelectField('Status', choices=[
        ('', 'Any'), ('OPEN', 'Open'), ('CLOSED', 'Closed')
    ], validators=[Optional()])
    flagged_only = SelectField('Flagged', choices=[
        ('', 'All'), ('1', 'Flagged Only')
    ], validators=[Optional()])
    submit = SubmitField('Search')