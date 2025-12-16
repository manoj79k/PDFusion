# a2a_models.py
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

A2A_PROTOCOL_VERSION = "a2a.v1"


class Principal(BaseModel):
    user_id: str
    tenant_id: Optional[str] = None
    scopes: Optional[List[str]] = None


class SecurityContext(BaseModel):
    type: str
    token: str
    principal: Optional[Principal] = None


class Intent(BaseModel):
    name: str
    priority: Optional[str] = "normal"
    deadline: Optional[str] = None


class Context(BaseModel):
    conversation_id: Optional[str] = None
    locale: Optional[str] = "en-US"
    currency: Optional[str] = "USD"
    time_zone: Optional[str] = "America/New_York"


class Meta(BaseModel):
    source_channel: Optional[str] = None
    trace_id: Optional[str] = None
    retries: int = 0


class A2ARequest(BaseModel):
    protocol: str
    message_id: str
    sender: str
    receiver: str
    capability: str
    security: SecurityContext
    payload: Dict[str, Any]
    intent: Optional[Intent] = None
    context: Optional[Context] = None
    meta: Optional[Meta] = None


class A2AResponse(BaseModel):
    protocol: str
    message_id: str
    correlation_id: str
    sender: str
    receiver: str
    status: str
    status_code: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    meta: Optional[Meta] = None