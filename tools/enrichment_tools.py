from __future__ import annotations
"""
Mock LinkedIn & ZoomInfo enrichment.

In production these would call real APIs. Here we simulate realistic responses:
  - 3 contacts have changed jobs (triggers Career Tracker alerts)
  - Most contacts have verified / unchanged data
  - A few lookups return "not found" (simulating API limits)
"""

# ── Mock LinkedIn data ─────────────────────────────────────────────────────────
# Maps linkedin_url → current profile data
_LINKEDIN_DATA: dict[str, dict] = {
    "linkedin.com/in/sarahjohnson": {
        "current_title": "CTO",                  # was VP of Engineering — JOB CHANGE
        "current_company": "NexGen Ventures",     # was TechCorp Inc — JOB CHANGE
        "confidence": 0.97,
        "profile_active": True,
        "changed": True,
    },
    "linkedin.com/in/marcusrivera": {
        "current_title": "VP of Sales",           # was Head of Sales — promotion
        "current_company": "Apex Growth Partners",# was CloudWave — JOB CHANGE
        "confidence": 0.94,
        "profile_active": True,
        "changed": True,
    },
    "linkedin.com/in/priyanair": {
        "current_title": "Director of RevOps",
        "current_company": "DataDriven Co",
        "confidence": 0.91,
        "profile_active": True,
        "changed": False,
    },
    "linkedin.com/in/jamesobrien": {
        "current_title": "Chief Technology Officer",# CTO → formal title update
        "current_company": "Momentum Systems",       # was ScaleIt Solutions — JOB CHANGE
        "confidence": 0.96,
        "profile_active": True,
        "changed": True,
    },
    "linkedin.com/in/elenavasquez": {
        "current_title": "CMO",
        "current_company": "GrowthLab",
        "confidence": 0.93,
        "profile_active": True,
        "changed": False,
    },
    "linkedin.com/in/aishapatel": {
        "current_title": "Senior Product Manager",  # fills in missing title
        "current_company": "Innovate Corp",
        "confidence": 0.88,
        "profile_active": True,
        "changed": False,
    },
    "linkedin.com/in/fatimaalhassan": {
        "current_title": "VP of Product",
        "current_company": "Meridian AI",
        "confidence": 0.90,
        "profile_active": True,
        "changed": False,
    },
    "linkedin.com/in/noahfischer": {
        "current_title": "Chief Revenue Officer",
        "current_company": "Pinnacle Corp",
        "confidence": 0.99,
        "profile_active": True,
        "changed": False,
    },
    "linkedin.com/in/yukitanaka": {
        "current_title": "Head of Partnerships",
        "current_company": "Blueshift Tech",
        "confidence": 0.98,
        "profile_active": True,
        "changed": False,
    },
    "linkedin.com/in/lindapark": {
        "current_title": "Director of Marketing",
        "current_company": "Cascade Digital",
        "confidence": 0.85,
        "profile_active": True,
        "changed": False,
    },
}

# ── Mock ZoomInfo data ─────────────────────────────────────────────────────────
# Maps email → ZoomInfo enrichment record
_ZOOMINFO_DATA: dict[str, dict] = {
    "sarah.johnson@techcorp.com": {
        "email_valid": True,
        "direct_phone": "+1-415-555-0101",
        "company_size": "501-1000",
        "industry": "Software / SaaS",
        "hq_location": "San Francisco, CA",
        "fields_verified": 4,
    },
    "mrivera@cloudwave.io": {
        "email_valid": True,
        "direct_phone": "+1-312-555-0202",
        "company_size": "51-200",
        "industry": "Cloud Infrastructure",
        "hq_location": "Chicago, IL",
        "fields_verified": 4,
    },
    "p.nair@datadriven.co": {
        "email_valid": True,
        "direct_phone": "+1-929-555-0303",
        "company_size": "201-500",
        "industry": "Data Analytics",
        "hq_location": "New York, NY",
        "fields_verified": 5,
    },
    "jobrien@scaleit.com": {
        "email_valid": True,
        "direct_phone": "+1-628-555-0404",
        "company_size": "51-200",
        "industry": "Enterprise Software",
        "hq_location": "Austin, TX",
        "fields_verified": 4,
    },
    "elena@growthlab.io": {
        "email_valid": True,
        "direct_phone": "+1-512-555-0505",
        "company_size": "11-50",
        "industry": "Marketing Technology",
        "hq_location": "Austin, TX",
        "fields_verified": 5,
    },
    "t.chen@nextech": {
        "email_valid": False,
        "note": "Email domain 'nextech' is invalid — no MX record found",
        "fields_verified": 0,
    },
    "aisha.patel@innovate.com": {
        "email_valid": True,
        "direct_phone": "+1-202-555-0707",
        "company_size": "1001-5000",
        "industry": "Enterprise Technology",
        "hq_location": "Washington, DC",
        "fields_verified": 4,
    },
    "david.kim@": {
        "email_valid": False,
        "note": "Malformed email address — no domain",
        "fields_verified": 0,
    },
    "fatima@meridian.ai": {
        "email_valid": True,
        "direct_phone": "+1-347-555-1100",
        "company_size": "51-200",
        "industry": "Artificial Intelligence",
        "hq_location": "New York, NY",
        "fields_verified": 4,
    },
    "noah.fischer@pinnacle.com": {
        "email_valid": True,
        "direct_phone": "+1-650-555-1400",
        "company_size": "201-500",
        "industry": "Financial Services",
        "hq_location": "Palo Alto, CA",
        "fields_verified": 5,
    },
    "y.tanaka@blueshift.tech": {
        "email_valid": True,
        "direct_phone": "+1-206-555-1500",
        "company_size": "51-200",
        "industry": "Technology Partnerships",
        "hq_location": "Seattle, WA",
        "fields_verified": 5,
    },
}


class EnrichmentTools:

    def check_linkedin(self, contact_id: str, linkedin_url: str) -> dict:
        """Simulate a LinkedIn profile lookup."""
        from data.mock_crm import MockCRM
        crm = MockCRM.__new__(MockCRM)   # lightweight — won't re-init data

        data = _LINKEDIN_DATA.get(linkedin_url)
        if not data:
            return {
                "contact_id": contact_id,
                "linkedin_url": linkedin_url,
                "found": False,
                "message": "Profile not found or private — may require manual review",
            }

        return {
            "contact_id": contact_id,
            "linkedin_url": linkedin_url,
            "found": True,
            "current_title": data["current_title"],
            "current_company": data["current_company"],
            "confidence": data["confidence"],
            "profile_active": data["profile_active"],
            "job_change_detected": data["changed"],
        }

    def check_zoominfo(self, contact_id: str, email: str) -> dict:
        """Simulate a ZoomInfo enrichment lookup."""
        data = _ZOOMINFO_DATA.get(email)
        if not data:
            return {
                "contact_id": contact_id,
                "email": email,
                "found": False,
                "message": "No ZoomInfo record found for this email",
            }

        return {
            "contact_id": contact_id,
            "email": email,
            "found": True,
            **data,
        }

    def validate_email(self, email: str) -> dict:
        """Quick email format validation (no live DNS in mock)."""
        import re
        valid = bool(re.match(r"^[^@]+@[^@]+\.[^@]{2,}$", email or ""))
        return {
            "email": email,
            "valid_format": valid,
            "note": "Mock validation — in production would perform MX/SMTP check",
        }
