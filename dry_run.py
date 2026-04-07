"""
Dry-run mock for The Scout.

Replaces the Anthropic API client with a pre-scripted session that mimics
what Claude Opus would do — identical tool dispatch loop, zero API cost.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


# ── Lightweight stand-ins for the SDK types the agent expects ──────────────────

@dataclass
class _ThinkingBlock:
    type: str = "thinking"
    thinking: str = ""

@dataclass
class _TextBlock:
    type: str = "text"
    text: str = ""

@dataclass
class _ToolUseBlock:
    type: str = "tool_use"
    id: str = field(default_factory=lambda: f"tool_{uuid.uuid4().hex[:8]}")
    name: str = ""
    input: dict = field(default_factory=dict)

@dataclass
class _FakeResponse:
    content: list
    stop_reason: str = "tool_use"


def _think(text: str) -> _ThinkingBlock:
    return _ThinkingBlock(thinking=text)

def _say(text: str) -> _TextBlock:
    return _TextBlock(text=text)

def _call(name: str, **kwargs) -> _ToolUseBlock:
    return _ToolUseBlock(name=name, input=kwargs)


# ── Scripted turn sequences ────────────────────────────────────────────────────

DEEP_CLEAN_TURNS = [
    # Turn 1 — survey the landscape
    _FakeResponse([
        _think("First I should get all contacts and understand the full dataset."),
        _say("Starting the Utopian Deep Clean. Let me first load all contacts."),
        _call("get_contacts", filter_type="all"),
    ]),
    # Turn 2 — hunt for duplicates
    _FakeResponse([
        _think("Good overview. Now I need to find any duplicate records before enriching."),
        _say("Scanning for duplicate records…"),
        _call("find_duplicates"),
    ]),
    # Turn 3 — merge Sarah Johnson duplicates
    _FakeResponse([
        _think("Two duplicate groups found. c001 has higher health score than c008 — keep c001 as primary."),
        _say("Merging duplicate Sarah Johnson records (keeping c001, removing c008)…"),
        _call("merge_contacts", primary_id="c001", duplicate_id="c008"),
    ]),
    # Turn 4 — merge Marcus Rivera duplicates
    _FakeResponse([
        _call("merge_contacts", primary_id="c002", duplicate_id="c009"),
    ]),
    # Turn 5 — standardise bad records
    _FakeResponse([
        _think("Now fix the formatting issues. c006 has 'tom CHEN', invalid email, unformatted phone."),
        _say("Standardising contact c006 (tom CHEN)…"),
        _call("standardize_contact", contact_id="c006"),
    ]),
    _FakeResponse([_call("standardize_contact", contact_id="c007")]),
    _FakeResponse([_call("standardize_contact", contact_id="c010")]),
    # Turn 6 — LinkedIn enrichment for active contacts
    _FakeResponse([
        _think("Now cross-reference LinkedIn for every trackable contact that has a URL."),
        _say("Checking LinkedIn profiles for all GDPR-eligible contacts…"),
        _call("check_linkedin", contact_id="c001", linkedin_url="linkedin.com/in/sarahjohnson"),
    ]),
    # Turn 7 — Sarah Johnson job change detected → alert
    _FakeResponse([
        _think("Sarah Johnson has moved from TechCorp Inc to NexGen Ventures as CTO. She is alert_eligible. I must update the CRM and send an alert."),
        _say("🚨 Job change detected for Sarah Johnson — updating CRM and sending alert."),
        _call("update_contact", contact_id="c001", field="title",   new_value="CTO",             source="LinkedIn"),
    ]),
    _FakeResponse([
        _call("update_contact", contact_id="c001", field="company", new_value="NexGen Ventures",  source="LinkedIn"),
    ]),
    _FakeResponse([
        _call("send_job_change_alert",
              contact_id="c001", contact_name="Sarah Johnson",
              old_company="TechCorp Inc", new_company="NexGen Ventures",
              old_title="VP of Engineering", new_title="CTO",
              alert_channel="both"),
    ]),
    # Marcus Rivera
    _FakeResponse([_call("check_linkedin", contact_id="c002", linkedin_url="linkedin.com/in/marcusrivera")]),
    _FakeResponse([_call("update_contact", contact_id="c002", field="title",   new_value="VP of Sales",          source="LinkedIn")]),
    _FakeResponse([_call("update_contact", contact_id="c002", field="company", new_value="Apex Growth Partners",  source="LinkedIn")]),
    _FakeResponse([
        _call("send_job_change_alert",
              contact_id="c002", contact_name="Marcus Rivera",
              old_company="CloudWave", new_company="Apex Growth Partners",
              old_title="Head of Sales", new_title="VP of Sales",
              alert_channel="both"),
    ]),
    # Priya Nair — no change
    _FakeResponse([_call("check_linkedin", contact_id="c003", linkedin_url="linkedin.com/in/priyanair")]),
    # James O'Brien
    _FakeResponse([_call("check_linkedin", contact_id="c004", linkedin_url="linkedin.com/in/jamesobrien")]),
    _FakeResponse([_call("update_contact", contact_id="c004", field="title",   new_value="Chief Technology Officer", source="LinkedIn")]),
    _FakeResponse([_call("update_contact", contact_id="c004", field="company", new_value="Momentum Systems",         source="LinkedIn")]),
    _FakeResponse([
        _call("send_job_change_alert",
              contact_id="c004", contact_name="James O'Brien",
              old_company="ScaleIt Solutions", new_company="Momentum Systems",
              old_title="CTO", new_title="Chief Technology Officer",
              alert_channel="both"),
    ]),
    # Remaining LinkedIn checks
    _FakeResponse([_call("check_linkedin", contact_id="c005", linkedin_url="linkedin.com/in/elenavasquez")]),
    _FakeResponse([_call("check_linkedin", contact_id="c007", linkedin_url="linkedin.com/in/aishapatel")]),
    _FakeResponse([_call("update_contact", contact_id="c007", field="title", new_value="Senior Product Manager", source="LinkedIn")]),
    _FakeResponse([_call("check_linkedin", contact_id="c011", linkedin_url="linkedin.com/in/fatimaalhassan")]),
    _FakeResponse([_call("check_linkedin", contact_id="c014", linkedin_url="linkedin.com/in/noahfischer")]),
    _FakeResponse([_call("check_linkedin", contact_id="c015", linkedin_url="linkedin.com/in/yukitanaka")]),
    # ZoomInfo for bad emails
    _FakeResponse([
        _think("Now validate emails via ZoomInfo for contacts with unverified or malformed addresses."),
        _say("Running ZoomInfo checks for email validation…"),
        _call("check_zoominfo", contact_id="c006", email="t.chen@nextech"),
    ]),
    _FakeResponse([_call("check_zoominfo", contact_id="c010", email="david.kim@")]),
    _FakeResponse([_call("check_zoominfo", contact_id="c003", email="p.nair@datadriven.co")]),
    _FakeResponse([_call("update_contact", contact_id="c003", field="phone", new_value="+1-929-555-0303", source="ZoomInfo")]),
    # Final report
    _FakeResponse([
        _think("All contacts processed. Time to generate the final data health report."),
        _say("All contacts processed. Generating final data health report…"),
        _call("get_data_health_report"),
    ]),
    # End turn
    _FakeResponse([
        _say(
            "✅ Utopian Deep Clean complete!\n\n"
            "**Summary:**\n"
            "• Merged 2 duplicate groups (Sarah Johnson ×2, Marcus Rivera ×2)\n"
            "• Standardised 3 contacts with formatting issues (tom CHEN, missing title, malformed email)\n"
            "• Detected 3 job changes via LinkedIn:\n"
            "  - Sarah Johnson → CTO @ NexGen Ventures\n"
            "  - Marcus Rivera → VP of Sales @ Apex Growth Partners\n"
            "  - James O'Brien → CTO @ Momentum Systems\n"
            "• Sent 3 Proactive Change Alerts to sales team (no automated outreach to contacts)\n"
            "• Filled in missing title for Aisha Patel via LinkedIn\n"
            "• Flagged 2 invalid emails (tom CHEN, David Kim) for manual review\n"
            "• Updated phone for Priya Nair via ZoomInfo\n"
            "• 2 stale contacts (Robert Thornton, Linda Park) excluded — outside GDPR 24-month window\n\n"
            "**GDPR:** Zero-Copy architecture maintained. All processing in-memory. "
            "No shadow database created."
        ),
    ], stop_reason="end_turn"),
]

MONITOR_TURNS = [
    _FakeResponse([
        _think("Fetch only GDPR-trackable contacts — those with interaction in the last 24 months."),
        _say("Career Tracker starting. Loading GDPR-eligible contacts…"),
        _call("get_contacts", filter_type="trackable"),
    ]),
    _FakeResponse([
        _think("13 trackable contacts. I'll check each one that has a LinkedIn URL."),
        _say("Checking LinkedIn for all trackable contacts with a profile URL…"),
        _call("check_linkedin", contact_id="c001", linkedin_url="linkedin.com/in/sarahjohnson"),
    ]),
    _FakeResponse([
        _think("Job change! Sarah is alert_eligible (interaction 30 days ago). Update CRM and alert."),
        _call("update_contact", contact_id="c001", field="title",   new_value="CTO",            source="LinkedIn"),
    ]),
    _FakeResponse([_call("update_contact", contact_id="c001", field="company", new_value="NexGen Ventures", source="LinkedIn")]),
    _FakeResponse([
        _call("send_job_change_alert",
              contact_id="c001", contact_name="Sarah Johnson",
              old_company="TechCorp Inc", new_company="NexGen Ventures",
              old_title="VP of Engineering", new_title="CTO",
              alert_channel="both"),
    ]),
    _FakeResponse([_call("check_linkedin", contact_id="c002", linkedin_url="linkedin.com/in/marcusrivera")]),
    _FakeResponse([_call("update_contact", contact_id="c002", field="title",   new_value="VP of Sales",         source="LinkedIn")]),
    _FakeResponse([_call("update_contact", contact_id="c002", field="company", new_value="Apex Growth Partners", source="LinkedIn")]),
    _FakeResponse([
        _call("send_job_change_alert",
              contact_id="c002", contact_name="Marcus Rivera",
              old_company="CloudWave", new_company="Apex Growth Partners",
              old_title="Head of Sales", new_title="VP of Sales",
              alert_channel="both"),
    ]),
    _FakeResponse([_call("check_linkedin", contact_id="c003", linkedin_url="linkedin.com/in/priyanair")]),
    _FakeResponse([_call("check_linkedin", contact_id="c004", linkedin_url="linkedin.com/in/jamesobrien")]),
    _FakeResponse([_call("update_contact", contact_id="c004", field="title",   new_value="Chief Technology Officer", source="LinkedIn")]),
    _FakeResponse([_call("update_contact", contact_id="c004", field="company", new_value="Momentum Systems",         source="LinkedIn")]),
    _FakeResponse([
        _call("send_job_change_alert",
              contact_id="c004", contact_name="James O'Brien",
              old_company="ScaleIt Solutions", new_company="Momentum Systems",
              old_title="CTO", new_title="Chief Technology Officer",
              alert_channel="both"),
    ]),
    _FakeResponse([_call("check_linkedin", contact_id="c005", linkedin_url="linkedin.com/in/elenavasquez")]),
    _FakeResponse([_call("check_linkedin", contact_id="c007", linkedin_url="linkedin.com/in/aishapatel")]),
    _FakeResponse([_call("check_linkedin", contact_id="c011", linkedin_url="linkedin.com/in/fatimaalhassan")]),
    _FakeResponse([_call("check_linkedin", contact_id="c014", linkedin_url="linkedin.com/in/noahfischer")]),
    _FakeResponse([_call("check_linkedin", contact_id="c015", linkedin_url="linkedin.com/in/yukitanaka")]),
    _FakeResponse([
        _say(
            "✅ Career Tracker scan complete!\n\n"
            "**3 job changes detected:**\n"
            "• Sarah Johnson — VP of Engineering @ TechCorp → CTO @ NexGen Ventures 🚨\n"
            "• Marcus Rivera — Head of Sales @ CloudWave → VP of Sales @ Apex Growth Partners 🚨\n"
            "• James O'Brien — CTO @ ScaleIt Solutions → CTO @ Momentum Systems 🚨\n\n"
            "**6 contacts confirmed unchanged** (Priya Nair, Elena Vasquez, Aisha Patel, "
            "Fatima Al-Hassan, Noah Fischer, Yuki Tanaka)\n\n"
            "**2 contacts excluded** — outside GDPR 24-month tracking window "
            "(Robert Thornton, Linda Park)\n\n"
            "3 Proactive Change Alerts sent to sales team via Slack + CRM. "
            "No automated outreach to contacts. GDPR Art. 14 Privacy Notice required before any contact."
        ),
    ], stop_reason="end_turn"),
]


class MockAnthropicClient:
    """Drop-in replacement for anthropic.Anthropic() — no network calls."""

    def __init__(self, turns: list[_FakeResponse]):
        self._turns = iter(turns)
        self.messages = self  # agent calls self.client.messages.create(...)

    def create(self, **kwargs) -> _FakeResponse:
        try:
            return next(self._turns)
        except StopIteration:
            # Safety fallback — should never be reached with a complete script
            return _FakeResponse([_say("(dry-run complete)")], stop_reason="end_turn")
