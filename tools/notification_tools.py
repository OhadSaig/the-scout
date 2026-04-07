from __future__ import annotations
"""
Notification tools — Slack and CRM alert simulation.

Per the PDR legal guidance: The Scout flags job changes as "Prospective Lead"
opportunities for human review. It does NOT send automated outreach emails
(prohibited under ePrivacy Directive). Alerts go to the sales team only.
"""

from datetime import datetime


class NotificationTools:
    def __init__(self):
        self._sent_alerts: list[dict] = []

    def send_job_change_alert(
        self,
        contact_id: str,
        contact_name: str,
        old_company: str,
        new_company: str,
        old_title: str,
        new_title: str,
        alert_channel: str = "both",
    ) -> dict:
        """
        Dispatch a Proactive Change Alert.

        NOTE: This notifies YOUR SALES TEAM — it does not send any outreach
        to the contact themselves (that would violate the ePrivacy Directive).
        """
        timestamp = datetime.now().isoformat()

        slack_message = (
            f"🚨 *Career Change Detected* — Action Required\n\n"
            f"*{contact_name}* has moved:\n"
            f"  • *From:* {old_title} @ {old_company}\n"
            f"  • *To:* {new_title} @ {new_company}\n\n"
            f"➡️ They are now flagged as a *Prospective Lead* at {new_company}.\n"
            f"   Please provide a Privacy Notice within 30 days (GDPR Art. 14)\n"
            f"   before any outreach. CRM record has been updated.\n\n"
            f"_CRM ID: {contact_id} | Detected: {timestamp}_"
        )

        crm_task = {
            "type": "FOLLOW_UP_TASK",
            "priority": "HIGH",
            "title": f"Champion moved — {contact_name} now at {new_company}",
            "description": (
                f"{contact_name} has left {old_company} and joined {new_company} "
                f"as {new_title}. They are flagged as a Prospective Lead. "
                f"Send Privacy Notice before outreach (GDPR Art. 14)."
            ),
            "due_date": "within 30 days",
            "contact_id": contact_id,
        }

        result = {
            "status": "sent",
            "contact_id": contact_id,
            "contact_name": contact_name,
            "timestamp": timestamp,
            "channels": [],
        }

        if alert_channel in ("slack", "both"):
            # Simulated Slack post
            result["channels"].append("slack")
            result["slack_message"] = slack_message
            print(f"\n[SLACK ALERT SIMULATED]\n{slack_message}")

        if alert_channel in ("crm", "both"):
            result["channels"].append("crm")
            result["crm_task"] = crm_task

        result["gdpr_note"] = (
            "Alert sent to sales team only. No automated outreach to contact. "
            "Sales rep must send GDPR Art. 14 Privacy Notice before any contact."
        )
        result["prospective_lead_created"] = True

        self._sent_alerts.append(result)
        return result

    def get_sent_alerts(self) -> list[dict]:
        return self._sent_alerts
