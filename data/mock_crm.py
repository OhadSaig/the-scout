"""
Mock CRM database — stands in for a real Salesforce / Snowflake integration.
Simulates realistic B2B contact data with intentional quality issues:
  - Some records have missing / malformed fields
  - A few duplicates
  - Some contacts outside the GDPR retention window (stale / dead leads)
  - 3 contacts who have "recently" changed jobs (Career Tracker bait)
"""
from __future__ import annotations

from datetime import datetime, timedelta
from models.contact import Contact

_now = datetime.now()

_RAW_CONTACTS = [
    # ── Active champions ──────────────────────────────────────────────────────
    {
        "id": "c001",
        "first_name": "Sarah",
        "last_name": "Johnson",
        "email": "sarah.johnson@techcorp.com",
        "title": "VP of Engineering",           # Will show as changed on LinkedIn
        "company": "TechCorp Inc",
        "linkedin_url": "linkedin.com/in/sarahjohnson",
        "phone": "+1-415-555-0101",
        "last_interaction_date": _now - timedelta(days=30),
        "created_date": _now - timedelta(days=540),
        "email_verified": True,
        "title_verified": False,
        "company_verified": True,
        "data_health_score": 62.0,
    },
    {
        "id": "c002",
        "first_name": "Marcus",
        "last_name": "Rivera",
        "email": "mrivera@cloudwave.io",
        "title": "Head of Sales",               # Will show as changed on LinkedIn
        "company": "CloudWave",
        "linkedin_url": "linkedin.com/in/marcusrivera",
        "phone": "+1-312-555-0202",
        "last_interaction_date": _now - timedelta(days=14),
        "created_date": _now - timedelta(days=720),
        "email_verified": True,
        "title_verified": True,
        "company_verified": True,
        "data_health_score": 88.0,
    },
    {
        "id": "c003",
        "first_name": "Priya",
        "last_name": "Nair",
        "email": "p.nair@datadriven.co",
        "title": "Director of RevOps",
        "company": "DataDriven Co",
        "linkedin_url": "linkedin.com/in/priyanair",
        "phone": None,
        "last_interaction_date": _now - timedelta(days=60),
        "created_date": _now - timedelta(days=400),
        "email_verified": True,
        "title_verified": True,
        "company_verified": True,
        "data_health_score": 79.0,
    },
    {
        "id": "c004",
        "first_name": "James",
        "last_name": "O'Brien",
        "email": "jobrien@scaleit.com",
        "title": "CTO",                          # Will show as changed on LinkedIn
        "company": "ScaleIt Solutions",
        "linkedin_url": "linkedin.com/in/jamesobrien",
        "phone": "+1-628-555-0404",
        "last_interaction_date": _now - timedelta(days=7),
        "created_date": _now - timedelta(days=800),
        "email_verified": True,
        "title_verified": False,
        "company_verified": True,
        "data_health_score": 71.0,
    },
    {
        "id": "c005",
        "first_name": "Elena",
        "last_name": "Vasquez",
        "email": "elena@growthlab.io",
        "title": "CMO",
        "company": "GrowthLab",
        "linkedin_url": "linkedin.com/in/elenavasquez",
        "phone": "+1-512-555-0505",
        "last_interaction_date": _now - timedelta(days=45),
        "created_date": _now - timedelta(days=300),
        "email_verified": True,
        "title_verified": True,
        "company_verified": True,
        "data_health_score": 91.0,
    },
    # ── Data quality issues ───────────────────────────────────────────────────
    {
        "id": "c006",
        "first_name": "tom",              # lowercase — needs standardisation
        "last_name": "CHEN",             # ALL CAPS — needs standardisation
        "email": "t.chen@nextech",       # missing TLD — invalid email
        "title": "product manager",      # no capitalisation
        "company": "NexTech",
        "linkedin_url": None,
        "phone": "5551234567",           # no formatting
        "last_interaction_date": _now - timedelta(days=90),
        "created_date": _now - timedelta(days=200),
        "email_verified": False,
        "title_verified": False,
        "company_verified": False,
        "data_health_score": 18.0,
    },
    {
        "id": "c007",
        "first_name": "Aisha",
        "last_name": "Patel",
        "email": "aisha.patel@innovate.com",
        "title": "",                     # missing title
        "company": "Innovate Corp",
        "linkedin_url": "linkedin.com/in/aishapatel",
        "phone": "+1-202-555-0707",
        "last_interaction_date": _now - timedelta(days=120),
        "created_date": _now - timedelta(days=600),
        "email_verified": True,
        "title_verified": False,
        "company_verified": True,
        "data_health_score": 44.0,
    },
    # ── Duplicates ────────────────────────────────────────────────────────────
    {
        "id": "c008",
        "first_name": "Sarah",
        "last_name": "Johnson",
        "email": "s.johnson@techcorp.com",   # different email alias
        "title": "VP Engineering",            # slight title variation
        "company": "TechCorp Inc",
        "linkedin_url": "linkedin.com/in/sarahjohnson",
        "phone": "+1-415-555-0101",
        "last_interaction_date": _now - timedelta(days=60),
        "created_date": _now - timedelta(days=200),
        "email_verified": False,
        "title_verified": False,
        "company_verified": True,
        "data_health_score": 35.0,
    },
    {
        "id": "c009",
        "first_name": "Marcus",
        "last_name": "Rivera",
        "email": "marcus@cloudwave.io",      # duplicate with different primary email
        "title": "Head of Sales",
        "company": "CloudWave",
        "linkedin_url": "linkedin.com/in/marcusrivera",
        "phone": None,
        "last_interaction_date": _now - timedelta(days=120),
        "created_date": _now - timedelta(days=900),
        "email_verified": True,
        "title_verified": True,
        "company_verified": True,
        "data_health_score": 55.0,
    },
    # ── Partial / low quality ─────────────────────────────────────────────────
    {
        "id": "c010",
        "first_name": "David",
        "last_name": "Kim",
        "email": "david.kim@",             # malformed email
        "title": "Senior SDR",
        "company": "Accelerate Inc",
        "linkedin_url": None,
        "phone": None,
        "last_interaction_date": _now - timedelta(days=150),
        "created_date": _now - timedelta(days=180),
        "email_verified": False,
        "title_verified": False,
        "company_verified": False,
        "data_health_score": 12.0,
    },
    {
        "id": "c011",
        "first_name": "Fatima",
        "last_name": "Al-Hassan",
        "email": "fatima@meridian.ai",
        "title": "VP Product",
        "company": "Meridian AI",
        "linkedin_url": "linkedin.com/in/fatimaalhassan",
        "phone": "+1-347-555-1100",
        "last_interaction_date": _now - timedelta(days=80),
        "created_date": _now - timedelta(days=365),
        "email_verified": True,
        "title_verified": False,
        "company_verified": True,
        "data_health_score": 58.0,
    },
    # ── Stale / outside GDPR window (> 24 months) ────────────────────────────
    {
        "id": "c012",
        "first_name": "Robert",
        "last_name": "Thornton",
        "email": "rthornton@oldco.com",
        "title": "Sales Director",
        "company": "OldCo Ltd",
        "linkedin_url": None,
        "phone": "+1-800-555-1212",
        "last_interaction_date": _now - timedelta(days=900),  # 30 months ago — STALE
        "created_date": _now - timedelta(days=1200),
        "email_verified": True,
        "title_verified": True,
        "company_verified": False,
        "data_health_score": 40.0,
    },
    {
        "id": "c013",
        "first_name": "Linda",
        "last_name": "Park",
        "email": "lpark@retro.com",
        "title": "Marketing Manager",
        "company": "Retro Systems",
        "linkedin_url": "linkedin.com/in/lindapark",
        "phone": None,
        "last_interaction_date": _now - timedelta(days=800),  # 26 months ago — STALE
        "created_date": _now - timedelta(days=1000),
        "email_verified": False,
        "title_verified": False,
        "company_verified": False,
        "data_health_score": 22.0,
    },
    # ── Well-maintained active records ────────────────────────────────────────
    {
        "id": "c014",
        "first_name": "Noah",
        "last_name": "Fischer",
        "email": "noah.fischer@pinnacle.com",
        "title": "Chief Revenue Officer",
        "company": "Pinnacle Corp",
        "linkedin_url": "linkedin.com/in/noahfischer",
        "phone": "+1-650-555-1400",
        "last_interaction_date": _now - timedelta(days=20),
        "created_date": _now - timedelta(days=500),
        "email_verified": True,
        "title_verified": True,
        "company_verified": True,
        "data_health_score": 95.0,
    },
    {
        "id": "c015",
        "first_name": "Yuki",
        "last_name": "Tanaka",
        "email": "y.tanaka@blueshift.tech",
        "title": "Head of Partnerships",
        "company": "Blueshift Tech",
        "linkedin_url": "linkedin.com/in/yukitanaka",
        "phone": "+1-206-555-1500",
        "last_interaction_date": _now - timedelta(days=10),
        "created_date": _now - timedelta(days=250),
        "email_verified": True,
        "title_verified": True,
        "company_verified": True,
        "data_health_score": 92.0,
    },
]


class MockCRM:
    """In-memory CRM — Zero-Copy architecture, nothing persisted externally."""

    def __init__(self):
        self._contacts: dict[str, Contact] = {
            r["id"]: Contact(**r) for r in _RAW_CONTACTS
        }

    # ── Reads ──────────────────────────────────────────────────────────────────

    def get_all(self) -> list[Contact]:
        return list(self._contacts.values())

    def get_by_id(self, contact_id: str) -> Contact | None:
        return self._contacts.get(contact_id)

    def get_trackable(self) -> list[Contact]:
        return [c for c in self._contacts.values() if c.tracking_eligible]

    def get_stale(self) -> list[Contact]:
        return [c for c in self._contacts.values() if not c.tracking_eligible]

    def get_unverified(self) -> list[Contact]:
        return [
            c for c in self._contacts.values()
            if not (c.email_verified and c.title_verified and c.company_verified)
        ]

    # ── Writes ─────────────────────────────────────────────────────────────────

    def update_field(self, contact_id: str, field: str, value) -> bool:
        contact = self._contacts.get(contact_id)
        if not contact:
            return False
        data = contact.model_dump()
        data[field] = value
        self._contacts[contact_id] = Contact(**data)
        return True

    def remove(self, contact_id: str) -> bool:
        if contact_id in self._contacts:
            del self._contacts[contact_id]
            return True
        return False

    # ── Utilities ──────────────────────────────────────────────────────────────

    def count(self) -> int:
        return len(self._contacts)

    def summary(self) -> dict:
        contacts = self.get_all()
        trackable = self.get_trackable()
        stale = self.get_stale()
        avg_health = sum(c.data_health_score for c in contacts) / len(contacts) if contacts else 0
        return {
            "total": len(contacts),
            "trackable": len(trackable),
            "stale_gdpr": len(stale),
            "average_health_score": round(avg_health, 1),
            "verified": sum(1 for c in contacts if c.data_health_score >= 80),
            "needs_attention": sum(1 for c in contacts if c.data_health_score < 50),
        }
