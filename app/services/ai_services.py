import os
import json
import urllib.request
import urllib.error


ANTHROPIC_API_URL = 'https://api.anthropic.com/v1/messages'
MODEL = 'claude-sonnet-4-20250514'


def _call_claude(system_prompt: str, user_prompt: str, max_tokens: int = 800) -> str:
    """Make a synchronous call to the Anthropic API. Returns the text response."""
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return 'AI Coach unavailable: ANTHROPIC_API_KEY is not set in your .env file.'

    payload = json.dumps({
        'model': MODEL,
        'max_tokens': max_tokens,
        'system': system_prompt,
        'messages': [{'role': 'user', 'content': user_prompt}]
    }).encode('utf-8')

    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data['content'][0]['text']
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            msg = json.loads(body).get('error', {}).get('message', body)
        except Exception:
            msg = body
        return f'API error {e.code}: {msg}'
    except Exception as e:
        return f'Connection error: {str(e)}'


TRADE_SYSTEM_PROMPT = """You are EdgeLog AI Coach — a professional trading mentor who analyses journal entries with precision and empathy.

Your role is to give honest, specific, actionable feedback on individual trades. You are direct but constructive. You never give generic advice. Every point must reference the actual trade data provided.

Format your response in clear sections using plain text (no markdown asterisks or hashes). Use these section headers exactly:
VERDICT
RISK MANAGEMENT
EXECUTION
WHAT TO IMPROVE
SCORE

For SCORE give a number out of 10 with one sentence of justification."""


SESSION_SYSTEM_PROMPT = """You are EdgeLog AI Coach — a professional trading mentor who analyses a trader's full session or recent trading history.

Your role is to identify patterns, behavioural tendencies, and give one clear weekly focus. Be specific — reference actual instruments, setups, and numbers from the data. Never give generic advice.

Format your response in clear sections using plain text (no markdown asterisks or hashes). Use these exact section headers:
SESSION SUMMARY
WHAT'S WORKING
BEHAVIOURAL PATTERNS TO WATCH
BEST SETUP THIS PERIOD
WEEKLY FOCUS

Keep the total response under 400 words. Be a coach, not a cheerleader."""


def get_trade_feedback(trade) -> str:
    """Generate AI feedback for a single trade."""
    direction_word = 'long' if trade.direction == 'LONG' else 'short'
    risk = abs(trade.entry_price - trade.stop_loss)
    risk_pct = round((risk / trade.entry_price) * 100, 2) if trade.entry_price else 0

    user_prompt = f"""Analyse this trade from my journal:

Instrument: {trade.instrument}
Direction: {trade.direction}
Setup: {trade.setup}
Session: {trade.session or 'Not recorded'}
Date: {trade.trade_date}
Status: {trade.status}

Entry: {trade.entry_price}
Stop Loss: {trade.stop_loss} (risk: {risk_pct}% / {round(risk, 4)} points)
Take Profit: {trade.take_profit or 'Not set'}
Exit: {trade.exit_price or 'Still open'}
Position Size: {trade.position_size}

P&L: {'$' + str(trade.pnl) if trade.pnl is not None else 'Open'}
R-Multiple: {str(trade.r_multiple) + 'R' if trade.r_multiple is not None else 'Open/not calculated'}

Trader notes: {trade.notes or 'No notes recorded.'}

Give me honest, specific feedback on this trade."""

    return _call_claude(TRADE_SYSTEM_PROMPT, user_prompt, max_tokens=600)


def get_session_feedback(trades: list, stats: dict, username: str) -> str:
    """Generate AI session debrief based on recent trades."""
    if not trades:
        return 'No trades found to analyse. Log some trades first.'

    closed = [t for t in trades if t.status == 'CLOSED' and t.pnl is not None]

    trade_lines = []
    for t in trades[:20]:  # cap at 20 to stay within token limits
        r_str = f'{t.r_multiple}R' if t.r_multiple is not None else 'open'
        pnl_str = f'${t.pnl}' if t.pnl is not None else 'open'
        trade_lines.append(
            f'  {t.trade_date} | {t.instrument} | {t.direction} | {t.setup} | '
            f'{t.session or "?"} | {pnl_str} | {r_str}'
        )

    trades_text = '\n'.join(trade_lines)

    user_prompt = f"""Analyse the recent trading performance for {username}:

STATS (last period):
- Total trades: {stats['total_trades']}
- Closed trades: {stats['closed_trades']}
- Win rate: {stats['win_rate']}%
- Total P&L: ${stats['total_pnl']}
- Average R-multiple: {stats['avg_r']}R
- Wins: {stats['wins']} | Losses: {stats['losses']}

RECENT TRADES (newest first):
  Date       | Instrument | Dir   | Setup | Session | P&L | R
{trades_text}

Give me a full session debrief and coaching report."""

    return _call_claude(SESSION_SYSTEM_PROMPT, user_prompt, max_tokens=700)
