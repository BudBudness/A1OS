from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ProgramCategory(str, Enum):
    orphan_support = "orphan_support"
    widow_support = "widow_support"
    youth_empowerment = "youth_empowerment"
    health_awareness = "health_awareness"
    blood_donation = "blood_donation"
    mental_health = "mental_health"
    refugee_outreach = "refugee_outreach"
    orphanage_partnerships = "orphanage_partnerships"
    women_in_tech = "women_in_tech"
    environmental_awareness = "environmental_awareness"
    partnerships = "partnerships"


class VolunteerCreate(BaseModel):
    full_name: str = Field(min_length=2)
    phone: str = Field(min_length=7)
    email: Optional[EmailStr] = None
    location: Optional[str] = None
    interests: list[ProgramCategory] = Field(default_factory=list)
    message: Optional[str] = None


class VolunteerRead(VolunteerCreate):
    id: UUID
    status: str
    created_at: datetime


class PartnerCreate(BaseModel):
    organization_name: str = Field(min_length=2)
    contact_person: str = Field(min_length=2)
    phone: str = Field(min_length=7)
    email: Optional[EmailStr] = None
    partnership_area: ProgramCategory
    message: Optional[str] = None


class PartnerRead(PartnerCreate):
    id: UUID
    status: str
    created_at: datetime


class DonationIntent(BaseModel):
    full_name: str = Field(min_length=2)
    phone: str = Field(min_length=7)
    amount_ugx: int = Field(gt=0)
    campaign: Optional[str] = None
    message: Optional[str] = None


class DonationRead(DonationIntent):
    id: UUID
    status: str
    created_at: datetime


class OutreachReportCreate(BaseModel):
    title: str = Field(min_length=3)
    category: ProgramCategory
    location: Optional[str] = None
    summary: str = Field(min_length=10)
    people_reached: int = Field(default=0, ge=0)
    media_urls: list[str] = Field(default_factory=list)


class OutreachReportRead(OutreachReportCreate):
    id: UUID
    created_at: datetime


class Event(BaseModel):
    slug: str
    title: str
    category: ProgramCategory
    summary: str
    target_month: Optional[str] = None