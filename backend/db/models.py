from dataclasses import dataclass
from datetime import datetime


@dataclass
class Trace:
    request_id: str
    created_at: datetime
    event: str
    payload: dict