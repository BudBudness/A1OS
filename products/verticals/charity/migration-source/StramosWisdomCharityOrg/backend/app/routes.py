from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from .data import CONTACTS, EVENTS, PROGRAMS
from .database import SessionLocal
from .models import Donation, OutreachReport, Partner, Volunteer
from .schemas import (
    DonationIntent,
    DonationRead,
    Event,
    OutreachReportCreate,
    OutreachReportRead,
    PartnerCreate,
    PartnerRead,
    VolunteerCreate,
    VolunteerRead,
)
from .serializers import (
    serialize_donation,
    serialize_partner,
    serialize_report,
    serialize_volunteer,
)

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "Stramos Wisdom Charity API",
        "time": datetime.utcnow().isoformat(),
    }


@router.get("/api/contact")
def get_contact() -> dict:
    return CONTACTS


@router.get("/api/programs")
def list_programs() -> list[dict]:
    return PROGRAMS


@router.get("/api/events", response_model=list[Event])
def list_events() -> list[Event]:
    return EVENTS


@router.get("/api/events/{slug}", response_model=Event)
def get_event(slug: str) -> Event:
    for event in EVENTS:
        if event.slug == slug:
            return event
    raise HTTPException(status_code=404, detail="Event not found")


@router.post("/api/volunteers", response_model=VolunteerRead)
def create_volunteer(payload: VolunteerCreate) -> VolunteerRead:
    with SessionLocal() as db:
        item = Volunteer(
            full_name=payload.full_name,
            phone=payload.phone,
            email=str(payload.email) if payload.email else None,
            location=payload.location,
            interests=[interest.value for interest in payload.interests],
            message=payload.message,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return serialize_volunteer(item)


@router.get("/api/volunteers", response_model=list[VolunteerRead])
def list_volunteers(limit: int = Query(default=50, ge=1, le=200)) -> list[VolunteerRead]:
    with SessionLocal() as db:
        rows = db.scalars(
            select(Volunteer).order_by(Volunteer.created_at.desc()).limit(limit)
        ).all()
        return [serialize_volunteer(row) for row in rows]


@router.post("/api/partners", response_model=PartnerRead)
def create_partner(payload: PartnerCreate) -> PartnerRead:
    with SessionLocal() as db:
        item = Partner(
            organization_name=payload.organization_name,
            contact_person=payload.contact_person,
            phone=payload.phone,
            email=str(payload.email) if payload.email else None,
            partnership_area=payload.partnership_area.value,
            message=payload.message,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return serialize_partner(item)


@router.get("/api/partners", response_model=list[PartnerRead])
def list_partners(limit: int = Query(default=50, ge=1, le=200)) -> list[PartnerRead]:
    with SessionLocal() as db:
        rows = db.scalars(
            select(Partner).order_by(Partner.created_at.desc()).limit(limit)
        ).all()
        return [serialize_partner(row) for row in rows]


@router.post("/api/donations/intent", response_model=DonationRead)
def create_donation_intent(payload: DonationIntent) -> DonationRead:
    with SessionLocal() as db:
        item = Donation(
            full_name=payload.full_name,
            phone=payload.phone,
            amount_ugx=payload.amount_ugx,
            campaign=payload.campaign,
            message=payload.message,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return serialize_donation(item)


@router.get("/api/donations", response_model=list[DonationRead])
def list_donations(limit: int = Query(default=50, ge=1, le=200)) -> list[DonationRead]:
    with SessionLocal() as db:
        rows = db.scalars(
            select(Donation).order_by(Donation.created_at.desc()).limit(limit)
        ).all()
        return [serialize_donation(row) for row in rows]


@router.post("/api/outreach-reports", response_model=OutreachReportRead)
def create_outreach_report(payload: OutreachReportCreate) -> OutreachReportRead:
    with SessionLocal() as db:
        item = OutreachReport(
            title=payload.title,
            category=payload.category.value,
            location=payload.location,
            summary=payload.summary,
            people_reached=payload.people_reached,
            media_urls=payload.media_urls,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return serialize_report(item)


@router.get("/api/outreach-reports", response_model=list[OutreachReportRead])
def list_outreach_reports(
    limit: int = Query(default=50, ge=1, le=200)
) -> list[OutreachReportRead]:
    with SessionLocal() as db:
        rows = db.scalars(
            select(OutreachReport).order_by(OutreachReport.created_at.desc()).limit(limit)
        ).all()
        return [serialize_report(row) for row in rows]