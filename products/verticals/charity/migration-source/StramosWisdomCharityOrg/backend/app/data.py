from .schemas import Event, ProgramCategory


EVENTS = [
    Event(
        slug="run-for-hope",
        title="Stramos Run For Hope",
        category=ProgramCategory.youth_empowerment,
        summary="Community charity marathon/walk for awareness, mobilization, and support.",
        target_month="October",
    ),
    Event(
        slug="lifeshare-blood-drive",
        title="Stramos LifeShare Blood Drive",
        category=ProgramCategory.blood_donation,
        summary="Blood donation and emergency health awareness drive.",
    ),
    Event(
        slug="mind-and-hope",
        title="Stramos Mind & Hope Conference",
        category=ProgramCategory.mental_health,
        summary="Mental health awareness, trauma healing, addiction awareness, and youth wellness.",
    ),
    Event(
        slug="future-builders",
        title="Stramos Future Builders Summit",
        category=ProgramCategory.youth_empowerment,
        summary="Youth mentorship, leadership, entrepreneurship, and practical skills.",
    ),
    Event(
        slug="refugee-hope",
        title="Stramos Refugee Hope Outreach",
        category=ProgramCategory.refugee_outreach,
        summary="Humanitarian support and dignity restoration for refugee communities.",
    ),
    Event(
        slug="women-in-tech",
        title="Stramos Women in Tech Summit",
        category=ProgramCategory.women_in_tech,
        summary="Girls and women digital inclusion, coding exposure, AI awareness, and cyber safety.",
    ),
    Event(
        slug="green-future",
        title="Stramos Green Future Initiative",
        category=ProgramCategory.environmental_awareness,
        summary="Environmental awareness, clean-up drives, tree planting, sanitation, and sustainability education.",
    ),
]


PROGRAMS = [
    {
        "title": "Orphan Support",
        "category": ProgramCategory.orphan_support,
        "summary": "Food, bedding, clothing, school support, emotional care, and orphanage visits.",
    },
    {
        "title": "Widow & Vulnerable Family Support",
        "category": ProgramCategory.widow_support,
        "summary": "Welfare support, emergency aid, livelihood support, and empowerment.",
    },
    {
        "title": "Youth Empowerment",
        "category": ProgramCategory.youth_empowerment,
        "summary": "Mentorship, discipline, entrepreneurship, leadership, digital literacy, and practical skills.",
    },
    {
        "title": "Health & Awareness",
        "category": ProgramCategory.health_awareness,
        "summary": "Achieved and active health awareness programs including blood donation and mental health outreach.",
    },
    {
        "title": "Refugee Outreach",
        "category": ProgramCategory.refugee_outreach,
        "summary": "Food, clothing, psychosocial support, children support, and dignity restoration.",
    },
    {
        "title": "Orphanage Partnerships",
        "category": ProgramCategory.orphanage_partnerships,
        "summary": "Partnerships with children homes, shelters, and humanitarian centers.",
    },
    {
        "title": "Women/Girls in Tech",
        "category": ProgramCategory.women_in_tech,
        "summary": "Digital inclusion, beginner coding, AI awareness, online work, and cyber safety.",
    },
    {
        "title": "Environmental Awareness",
        "category": ProgramCategory.environmental_awareness,
        "summary": "Clean-up drives, tree planting, waste management, and school awareness.",
    },
]


CONTACTS = {
    "email": "igahussein4@gmail.com",
    "phones": ["+256700709940", "+256783409327", "+256759902139"],
    "tiktok": "@stramoswisdomcharity",
    "slogan": "James 1:27 in Action",
    "public_message": "Love Wins",
}