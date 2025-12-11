from datetime import datetime, timezone
import uuid
import random
import string

def generate_id() -> str:
    return str(uuid.uuid4())

def generate_code(prefix: str, length: int = 10) -> str:
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=length - len(timestamp)))
    return f'{prefix}{timestamp}{random_str}'

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def format_currency(amount: float) -> str:
    return f'Rp {amount:,.0f}'.replace(',', '.')

def serialize_datetime(dt: datetime) -> str:
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt

def parse_datetime(dt_str: str) -> datetime:
    if isinstance(dt_str, str):
        return datetime.fromisoformat(dt_str)
    return dt_str
