"""
All tool definitions passed to the Claude API.
"""

ALL_TOOLS = [
    {
        "name": "get_contacts",
        "description": (
            "Retrieve contacts from the CRM. Use filter_type='trackable' to respect "
            "GDPR retention rules (only contacts active in the last 24 months). "
            "Use 'stale' to find dead leads outside the tracking window. "
            "Use 'unverified' to find contacts with missing or unvalidated fields."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filter_type": {
                    "type": "string",
                    "enum": ["all", "trackable", "stale", "unverified"],
                    "description": "Which subset of contacts to return.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of contacts to return (default 50).",
                },
            },
            "required": ["filter_type"],
        },
    },
    {
        "name": "get_contact_details",
        "description": "Get full details for a single contact by their CRM ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "contact_id": {
                    "type": "string",
                    "description": "The CRM contact ID (e.g. 'c001').",
                },
            },
            "required": ["contact_id"],
        },
    },
    {
        "name": "find_duplicates",
        "description": (
            "Scan the CRM for duplicate contacts by matching name + company or "
            "LinkedIn URL. Returns groups of likely duplicates with their IDs."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "merge_contacts",
        "description": (
            "Merge a duplicate contact into a primary record. The duplicate is removed "
            "and the primary is updated with any verified fields from the duplicate."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "primary_id": {
                    "type": "string",
                    "description": "ID of the contact to keep.",
                },
                "duplicate_id": {
                    "type": "string",
                    "description": "ID of the contact to remove.",
                },
            },
            "required": ["primary_id", "duplicate_id"],
        },
    },
    {
        "name": "standardize_contact",
        "description": (
            "Fix data formatting issues on a contact: capitalise names, validate and "
            "format phone numbers, trim whitespace, and flag invalid emails."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "contact_id": {
                    "type": "string",
                    "description": "The CRM contact ID to standardise.",
                },
            },
            "required": ["contact_id"],
        },
    },
    {
        "name": "check_linkedin",
        "description": (
            "Cross-reference a contact's LinkedIn profile to verify their current "
            "job title and employer. Returns current data and flags any changes "
            "from what is in the CRM. Preferred source for title accuracy."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "contact_id": {
                    "type": "string",
                    "description": "The CRM contact ID.",
                },
                "linkedin_url": {
                    "type": "string",
                    "description": "LinkedIn profile URL.",
                },
            },
            "required": ["contact_id", "linkedin_url"],
        },
    },
    {
        "name": "check_zoominfo",
        "description": (
            "Query ZoomInfo for firmographic and contact data: email, phone, "
            "company size, industry. Preferred source for contact/firmographic data."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "contact_id": {
                    "type": "string",
                    "description": "The CRM contact ID.",
                },
                "email": {
                    "type": "string",
                    "description": "Primary email to look up.",
                },
            },
            "required": ["contact_id", "email"],
        },
    },
    {
        "name": "update_contact",
        "description": (
            "Write a verified field update back to the CRM contact record. "
            "Only call this after confirming the new value from an external source."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "contact_id": {
                    "type": "string",
                    "description": "The CRM contact ID.",
                },
                "field": {
                    "type": "string",
                    "description": "Field to update (e.g. 'title', 'email', 'company').",
                },
                "new_value": {
                    "type": "string",
                    "description": "The verified new value.",
                },
                "source": {
                    "type": "string",
                    "description": "Source of the update (e.g. 'LinkedIn', 'ZoomInfo').",
                },
            },
            "required": ["contact_id", "field", "new_value", "source"],
        },
    },
    {
        "name": "send_job_change_alert",
        "description": (
            "Send a Proactive Change Alert when a champion or key contact has moved "
            "to a new company or role. Only call for contacts inside the 12-month "
            "alert window (alert_eligible=true) to maintain GDPR compliance."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "contact_id": {
                    "type": "string",
                    "description": "The CRM contact ID.",
                },
                "contact_name": {
                    "type": "string",
                    "description": "Full name of the contact.",
                },
                "old_company": {"type": "string"},
                "new_company": {"type": "string"},
                "old_title": {"type": "string"},
                "new_title": {"type": "string"},
                "alert_channel": {
                    "type": "string",
                    "enum": ["slack", "crm", "both"],
                    "description": "Where to send the alert.",
                },
            },
            "required": [
                "contact_id",
                "contact_name",
                "old_company",
                "new_company",
                "old_title",
                "new_title",
                "alert_channel",
            ],
        },
    },
    {
        "name": "get_data_health_report",
        "description": (
            "Generate an aggregate CRM data health report: overall score, breakdown "
            "by field, number of verified/partial/needs-attention contacts, and "
            "GDPR compliance summary."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]
