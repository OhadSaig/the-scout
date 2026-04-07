from __future__ import annotations
"""
CRM tool implementations — read/write operations against the MockCRM.
"""

import re
from datetime import datetime
from data.mock_crm import MockCRM


class CRMTools:
    def __init__(self, crm: MockCRM):
        self.crm = crm

    # ── Reads ──────────────────────────────────────────────────────────────────

    def get_contacts(self, filter_type: str = "all", limit: int = 50) -> dict:
        if filter_type == "all":
            contacts = self.crm.get_all()
        elif filter_type == "trackable":
            contacts = self.crm.get_trackable()
        elif filter_type == "stale":
            contacts = self.crm.get_stale()
        elif filter_type == "unverified":
            contacts = self.crm.get_unverified()
        else:
            return {"error": f"Unknown filter_type: {filter_type}"}

        contacts = contacts[:limit]
        return {
            "filter": filter_type,
            "count": len(contacts),
            "contacts": [c.to_dict() for c in contacts],
        }

    def get_contact_details(self, contact_id: str) -> dict:
        contact = self.crm.get_by_id(contact_id)
        if not contact:
            return {"error": f"Contact {contact_id} not found"}
        return contact.to_dict()

    # ── Duplicates ─────────────────────────────────────────────────────────────

    def find_duplicates(self) -> dict:
        contacts = self.crm.get_all()
        groups: dict[str, list[str]] = {}

        # Group by (normalised full name + company)
        for c in contacts:
            key_name = f"{c.first_name.lower().strip()}_{c.last_name.lower().strip()}_{c.company.lower().strip()}"
            groups.setdefault(key_name, []).append(c.id)

        # Group by LinkedIn URL
        by_li: dict[str, list[str]] = {}
        for c in contacts:
            if c.linkedin_url:
                by_li.setdefault(c.linkedin_url, []).append(c.id)

        duplicate_groups = []
        seen_pairs: set[frozenset] = set()

        for ids in list(groups.values()) + list(by_li.values()):
            if len(ids) > 1:
                pair = frozenset(ids)
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    records = []
                    for cid in ids:
                        c = self.crm.get_by_id(cid)
                        if c:
                            records.append({
                                "id": c.id,
                                "name": c.full_name,
                                "email": c.email,
                                "title": c.title,
                                "data_health_score": c.data_health_score,
                            })
                    duplicate_groups.append({"ids": list(ids), "records": records})

        return {
            "duplicate_groups_found": len(duplicate_groups),
            "duplicates": duplicate_groups,
        }

    def merge_contacts(self, primary_id: str, duplicate_id: str) -> dict:
        primary = self.crm.get_by_id(primary_id)
        duplicate = self.crm.get_by_id(duplicate_id)

        if not primary:
            return {"error": f"Primary contact {primary_id} not found"}
        if not duplicate:
            return {"error": f"Duplicate contact {duplicate_id} not found"}

        merged_fields = []

        # Copy verified fields from duplicate to primary if primary is missing them
        if not primary.phone and duplicate.phone:
            self.crm.update_field(primary_id, "phone", duplicate.phone)
            merged_fields.append("phone")
        if not primary.linkedin_url and duplicate.linkedin_url:
            self.crm.update_field(primary_id, "linkedin_url", duplicate.linkedin_url)
            merged_fields.append("linkedin_url")
        if duplicate.data_health_score > primary.data_health_score:
            # Keep primary but note we could selectively inherit higher-confidence fields
            merged_fields.append("(kept primary as higher-quality record)")

        self.crm.remove(duplicate_id)

        return {
            "status": "merged",
            "primary_id": primary_id,
            "removed_id": duplicate_id,
            "merged_fields": merged_fields,
            "primary_name": primary.full_name,
        }

    # ── Standardisation ────────────────────────────────────────────────────────

    def standardize_contact(self, contact_id: str) -> dict:
        contact = self.crm.get_by_id(contact_id)
        if not contact:
            return {"error": f"Contact {contact_id} not found"}

        changes: list[str] = []

        # Capitalise first name
        proper_first = contact.first_name.strip().title()
        if proper_first != contact.first_name:
            self.crm.update_field(contact_id, "first_name", proper_first)
            changes.append(f"first_name: '{contact.first_name}' → '{proper_first}'")

        # Capitalise last name
        proper_last = contact.last_name.strip().title()
        if proper_last != contact.last_name:
            self.crm.update_field(contact_id, "last_name", proper_last)
            changes.append(f"last_name: '{contact.last_name}' → '{proper_last}'")

        # Title case job title
        if contact.title:
            proper_title = contact.title.strip().title()
            if proper_title != contact.title:
                self.crm.update_field(contact_id, "title", proper_title)
                changes.append(f"title: '{contact.title}' → '{proper_title}'")

        # Validate email (simple check)
        email_valid = bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", contact.email or ""))
        if not email_valid and contact.email:
            changes.append(f"email '{contact.email}' flagged as INVALID — needs manual review")

        # Format phone (10-digit US numbers)
        if contact.phone:
            digits = re.sub(r"\D", "", contact.phone)
            if len(digits) == 10:
                formatted = f"+1-{digits[:3]}-{digits[3:6]}-{digits[6:]}"
                if formatted != contact.phone:
                    self.crm.update_field(contact_id, "phone", formatted)
                    changes.append(f"phone: '{contact.phone}' → '{formatted}'")

        # Recalculate health score
        new_score = self._calculate_health_score(contact_id)
        self.crm.update_field(contact_id, "data_health_score", new_score)

        return {
            "contact_id": contact_id,
            "contact_name": contact.full_name,
            "changes_made": len([c for c in changes if "flagged" not in c]),
            "changes": changes,
            "new_health_score": new_score,
        }

    # ── Updates ────────────────────────────────────────────────────────────────

    def update_contact(self, contact_id: str, field: str, new_value: str, source: str) -> dict:
        contact = self.crm.get_by_id(contact_id)
        if not contact:
            return {"error": f"Contact {contact_id} not found"}

        old_value = getattr(contact, field, None)
        success = self.crm.update_field(contact_id, field, new_value)

        if not success:
            return {"error": f"Failed to update field '{field}'"}

        # Mark field as verified if it came from a trusted source
        if field == "title":
            self.crm.update_field(contact_id, "title_verified", True)
        elif field == "email":
            self.crm.update_field(contact_id, "email_verified", True)
        elif field == "company":
            self.crm.update_field(contact_id, "company_verified", True)

        # Recalculate health score
        new_score = self._calculate_health_score(contact_id)
        self.crm.update_field(contact_id, "data_health_score", new_score)
        self.crm.update_field(contact_id, "last_enriched", datetime.now())

        return {
            "status": "updated",
            "contact_id": contact_id,
            "contact_name": contact.full_name,
            "field": field,
            "old_value": str(old_value),
            "new_value": new_value,
            "source": source,
            "new_health_score": new_score,
        }

    # ── Reporting ──────────────────────────────────────────────────────────────

    def get_data_health_report(self) -> dict:
        from compliance.gdpr import GDPRPolicy

        contacts = self.crm.get_all()
        if not contacts:
            return {"error": "No contacts found"}

        scores = [c.data_health_score for c in contacts]
        avg = sum(scores) / len(scores)

        verified = [c for c in contacts if c.data_health_score >= 80]
        partial = [c for c in contacts if 50 <= c.data_health_score < 80]
        needs_attention = [c for c in contacts if c.data_health_score < 50]
        trackable = self.crm.get_trackable()
        stale = self.crm.get_stale()

        email_verified = sum(1 for c in contacts if c.email_verified)
        title_verified = sum(1 for c in contacts if c.title_verified)
        company_verified = sum(1 for c in contacts if c.company_verified)

        return {
            "total_contacts": len(contacts),
            "average_health_score": round(avg, 1),
            "breakdown": {
                "verified_80_plus": len(verified),
                "partial_50_to_79": len(partial),
                "needs_attention_under_50": len(needs_attention),
            },
            "gdpr_compliance": {
                "trackable_contacts": len(trackable),
                "stale_contacts_outside_window": len(stale),
                "tracking_window_months": 24,
                "alert_window_months": 12,
            },
            "field_verification_rates": {
                "email_verified_pct": round(email_verified / len(contacts) * 100, 1),
                "title_verified_pct": round(title_verified / len(contacts) * 100, 1),
                "company_verified_pct": round(company_verified / len(contacts) * 100, 1),
            },
            "compliance": GDPRPolicy.compliance_summary(),
        }

    # ── Internal ───────────────────────────────────────────────────────────────

    def _calculate_health_score(self, contact_id: str) -> float:
        contact = self.crm.get_by_id(contact_id)
        if not contact:
            return 0.0

        score = 0.0
        # Email (30 pts)
        email_valid = bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", contact.email or ""))
        if email_valid:
            score += 20
        if contact.email_verified:
            score += 10
        # Title (25 pts)
        if contact.title and contact.title.strip():
            score += 15
        if contact.title_verified:
            score += 10
        # Company (25 pts)
        if contact.company and contact.company.strip():
            score += 15
        if contact.company_verified:
            score += 10
        # LinkedIn (10 pts)
        if contact.linkedin_url:
            score += 10
        # Phone (10 pts)
        if contact.phone:
            score += 10

        return round(score, 1)
