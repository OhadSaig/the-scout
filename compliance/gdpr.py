from __future__ import annotations
from datetime import datetime, timedelta
from config import TRACKING_RETENTION_MONTHS, ALERT_RETENTION_MONTHS


class GDPRPolicy:
    """
    GDPR compliance engine for The Scout.

    Legal basis: Legitimate Interest (GDPR Art. 6(1)(f))
    Scope: Only contacts with meaningful interaction in the past 12-24 months.
    Architecture: Zero-Copy — all processing is in-memory, no shadow database.
    """

    @classmethod
    def is_tracking_eligible(cls, last_interaction_date: datetime) -> bool:
        """Contact had a meaningful interaction within the retention window."""
        cutoff = datetime.now() - timedelta(days=TRACKING_RETENTION_MONTHS * 30)
        return last_interaction_date > cutoff

    @classmethod
    def is_alert_eligible(cls, last_interaction_date: datetime) -> bool:
        """Contact warrants a job-change alert (stricter 12-month window)."""
        cutoff = datetime.now() - timedelta(days=ALERT_RETENTION_MONTHS * 30)
        return last_interaction_date > cutoff

    @classmethod
    def filter_trackable(cls, contacts: list) -> list:
        return [c for c in contacts if cls.is_tracking_eligible(c.last_interaction_date)]

    @classmethod
    def compliance_summary(cls) -> dict:
        return {
            "legal_basis": "Legitimate Interest (GDPR Art. 6(1)(f))",
            "tracking_window_months": TRACKING_RETENTION_MONTHS,
            "alert_window_months": ALERT_RETENTION_MONTHS,
            "architecture": "Zero-Copy — in-memory processing only",
            "prohibited": "No shadow database, no indefinite tracking, no automated outreach",
        }
