from uuid import UUID

from .models import Donation, OutreachReport, Partner, Volunteer
from .schemas import (
    DonationRead,
    OutreachReportRead,
    PartnerRead,
    ProgramCategory,
    VolunteerRead,
)


def serialize_volunteer(item: Volunteer) -> VolunteerRead:
    return VolunteerRead(
        id=UUID(item.id),
        full_name=item.full_name,
        phone=item.phone,
        email=item.email,
        location=item.location,
        interests=[ProgramCategory(value) for value in item.interests],
        message=item.message,
        status=item.status,
        created_at=item.created_at,
    )


def serialize_partner(item: Partner) -> PartnerRead:
    return PartnerRead(
        id=UUID(item.id),
        organization_name=item.organization_name,
        contact_person=item.contact_person,
        phone=item.phone,
        email=item.email,
        partnership_area=ProgramCategory(item.partnership_area),
        message=item.message,
        status=item.status,
        created_at=item.created_at,
    )


def serialize_donation(item: Donation) -> DonationRead:
    return DonationRead(
        id=UUID(item.id),
        full_name=item.full_name,
        phone=item.phone,
        amount_ugx=item.amount_ugx,
        campaign=item.campaign,
        message=item.message,
        status=item.status,
        created_at=item.created_at,
    )


def serialize_report(item: OutreachReport) -> OutreachReportRead:
    return OutreachReportRead(
        id=UUID(item.id),
        title=item.title,
        category=ProgramCategory(item.category),
        location=item.location,
        summary=item.summary,
        people_reached=item.people_reached,
        media_urls=item.media_urls,
        created_at=item.created_at,
    )