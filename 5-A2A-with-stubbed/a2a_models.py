# a2a_models.py
from pydantic import BaseModel
from typing import Dict, Any, Optional

A2A_PROTOCOL_VERSION = "a2a.v1"

class SecurityContext(BaseModel):
    type: str
    token:str

class A2ARequest(BaseModel):
    protocol: str = A2A_PROTOCOL_VERSION
    message_id: str
    sender: str
    receiver: str
    capability: str
    security: SecurityContext
    payload: Dict[str, Any]

class A2AResponse(BaseModel):
    protocol: str 
    message_id: str
    correlation_id: str
    sender: str
    receiver: str
    status: str
    result:Optional[Dict[str, Any]] = None
    error:Optional[Dict[str, Any]] = None
  