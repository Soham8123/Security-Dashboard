from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SecurityEvent(BaseModel):
    event_type: str
    severity: str
    source_ip: Optional[str] = None
    description: str
    raw_log: Optional[str] = None

class SecurityEventResponse(BaseModel):
    id: int
    event_type: str
    severity: str
    source_ip: Optional[str] = None
    description: str
    raw_log: Optional[str] = None
    created_at: datetime

class AlertRule(BaseModel):
    rule_name: str
    pattern: str
    severity: str

