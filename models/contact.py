from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Contact(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    title: str
    company: str
    linkedin_url: Optional[str] = None
    phone: Optional[str] = None
    last_interaction_date: datetime
    created_date: datetime

    # Data quality
    email_verified: bool = False
    title_verified: bool = False
    company_verified: bool = False
    data_health_score: float = 0.0
    last_enriched: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def tracking_eligible(self) -> bool:
        from compliance.gdpr import GDPRPolicy
        return GDPRPolicy.is_tracking_eligible(self.last_interaction_date)

    @property
    def alert_eligible(self) -> bool:
        from compliance.gdpr import GDPRPolicy
        return GDPRPolicy.is_alert_eligible(self.last_interaction_date)

    @property
    def health_status(self) -> str:
        if self.data_health_score >= 80:
            return "Verified"
        elif self.data_health_score >= 50:
            return "Partial"
        else:
            return "Needs Attention"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "title": self.title,
            "company": self.company,
            "linkedin_url": self.linkedin_url,
            "phone": self.phone,
            "last_interaction_date": self.last_interaction_date.isoformat(),
            "email_verified": self.email_verified,
            "title_verified": self.title_verified,
            "company_verified": self.company_verified,
            "data_health_score": self.data_health_score,
            "health_status": self.health_status,
            "tracking_eligible": self.tracking_eligible,
            "alert_eligible": self.alert_eligible,
        }


class JobChangeAlert(BaseModel):
    contact_id: str
    contact_name: str
    old_company: str
    new_company: str
    old_title: str
    new_title: str
    detected_at: datetime = datetime.now()
    source: str = "LinkedIn"
