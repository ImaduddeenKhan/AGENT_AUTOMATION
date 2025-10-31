from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EventPlatform(str, Enum):
    PEATIX = "peatix"
    EVENTBRITE = "eventbrite"
    CONNPASS = "connpass"
    MEETUP = "meetup"
    DOORKEEPER = "doorkeeper"
    JETRO = "jetro"
    CHAMBER = "chamber"


class Event(BaseModel):
    title: str
    description: str
    date: datetime
    venue: str
    city: str
    source_url: str
    source_platform: EventPlatform
    price: str = "Unknown"
    registration_required: bool = False

    class Config:
        use_enum_values = True


class RankedEvent(BaseModel):
    event: Event
    relevance_score: float = Field(ge=0, le=1)
    matched_keywords: List[str] = []
    confidence: float = Field(ge=0, le=1)


class RegistrationResult(BaseModel):
    event: RankedEvent
    success: bool
    confirmation_data: Optional[Dict[str, Any]] = None
    qr_code_url: Optional[str] = None
    error_message: Optional[str] = None


class DigestEvent(BaseModel):
    title: str
    date: str
    venue: str
    description: str
    source_link: str
    relevance_score: float
    registration_status: str