from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ValidationFail:
    hint: str
    kwargs: dict[str, Any]
    failed_at: datetime
