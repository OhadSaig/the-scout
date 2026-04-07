from __future__ import annotations
"""
The Scout — Autonomous CRM Perfectionist Agent.

Orchestrates two modes via Claude Opus 4.6 + adaptive thinking:
  1. deep_clean  — Utopian Deep Clean of the full CRM
  2. monitor     — Career Tracker (detect job changes, fire alerts)
"""

import json
import os
import sys
import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from config import SCOUT_MODEL
from data.mock_crm import MockCRM
from tools.definitions import ALL_TOOLS
from tools.crm_tools import CRMTools
from tools.enrichment_tools import EnrichmentTools
from tools.notification_tools import NotificationTools

console = Console()


DEEP_CLEAN_SYSTEM = """You are The Scout, an Autonomous CRM Perfectionist operating inside \
the customer's secure data environment.

Your mission for this session: perform a complete "Utopian Deep Clean".

Step-by-step plan:
1. Fetch ALL contacts (filter_type="all") and review the landscape.
2. Find duplicate contact records — merge each group, keeping the highest-quality primary.
3. Standardize every contact that has formatting issues (bad casing, malformed phone, etc.).
4. For each contact with a LinkedIn URL, run check_linkedin to verify title/company.
   - If a job change is detected AND the contact is alert_eligible: call send_job_change_alert.
   - If the contact is NOT alert_eligible (stale): do NOT track them — skip.
5. For contacts missing a verified email, run check_zoominfo.
6. Write all verified updates back with update_contact, citing the source.
7. When all contacts are processed, call get_data_health_report to generate the final report.
8. Summarise your findings clearly: what was fixed, what changed, what alerts were sent.

GDPR rules you must enforce:
- Only send job-change alerts for contacts where alert_eligible=true (12-month window).
- Never create a shadow database — all processing is in-memory only.
- Do not trigger automated outreach to contacts — alerts go to the SALES TEAM only.
- Stale contacts (tracking_eligible=false) should be noted but NOT tracked or alerted.

Source reconciliation:
- LinkedIn is the gold standard for job titles.
- ZoomInfo is preferred for email, phone, and firmographic data.
"""

MONITOR_SYSTEM = """You are The Scout, running the Always-On Career Tracker.

Your mission: scan every GDPR-eligible contact for job changes and fire alerts.

Steps:
1. Fetch trackable contacts (filter_type="trackable") — these are GDPR-eligible.
2. For each contact that has a linkedin_url, call check_linkedin.
3. If job_change_detected=true:
   a. Call update_contact to update title and company in the CRM.
   b. If alert_eligible=true, call send_job_change_alert on channel "both".
4. Generate a Career Tracker summary when done.

GDPR rules:
- Only process trackable contacts (last interaction ≤ 24 months).
- Alerts only for alert_eligible contacts (≤ 12 months).
- Zero-Copy: no data stored externally.
"""


class ScoutAgent:
    def __init__(self, dry_run: bool = False):
        self._dry_run = dry_run
        # Client is created lazily — only needed when actually calling Claude
        self.client = None
        self.crm = MockCRM()
        self._crm_tools = CRMTools(self.crm)
        self._enrichment_tools = EnrichmentTools()
        self._notification_tools = NotificationTools()

    # ── Public entry points ────────────────────────────────────────────────────

    def _get_client(self):
        """Lazily create the Anthropic client, checking for the API key."""
        if self.client is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                console.print(
                    "[red bold]Error:[/red bold] ANTHROPIC_API_KEY is not set.\n"
                    "Create a [bold].env[/bold] file from [dim].env.example[/dim] "
                    "or export the variable:\n\n"
                    "  [bold]export ANTHROPIC_API_KEY=sk-ant-...[/bold]\n"
                    "\nTip: run with [bold]--dry-run[/bold] to test without an API key."
                )
                sys.exit(1)
            self.client = anthropic.Anthropic(api_key=api_key)
        return self.client

    def run_deep_clean(self):
        self._print_header(
            "Utopian Deep Clean",
            "Scanning and perfecting your entire CRM"
            + ("  [dim][dry-run — no API calls][/dim]" if self._dry_run else ""),
        )
        if self._dry_run:
            from dry_run import MockAnthropicClient, DEEP_CLEAN_TURNS
            self.client = MockAnthropicClient(DEEP_CLEAN_TURNS)
        else:
            self._get_client()
        self._run_agent(DEEP_CLEAN_SYSTEM, "Begin the Utopian Deep Clean.")

    def run_monitor(self):
        self._print_header(
            "Career Tracker",
            "Scanning for job changes across eligible contacts"
            + ("  [dim][dry-run — no API calls][/dim]" if self._dry_run else ""),
        )
        if self._dry_run:
            from dry_run import MockAnthropicClient, MONITOR_TURNS
            self.client = MockAnthropicClient(MONITOR_TURNS)
        else:
            self._get_client()
        self._run_agent(MONITOR_SYSTEM, "Run the Career Tracker.")

    def show_status(self):
        """Quick CRM status without invoking Claude."""
        summary = self.crm.summary()
        contacts = self.crm.get_all()

        table = Table(title="CRM Status", box=box.ROUNDED, show_header=True)
        table.add_column("Metric", style="bold cyan")
        table.add_column("Value", justify="right")

        table.add_row("Total contacts", str(summary["total"]))
        table.add_row("GDPR-trackable (≤24 mo)", str(summary["trackable"]))
        table.add_row("Stale / outside window", str(summary["stale_gdpr"]))
        table.add_row("Avg data health score", f"{summary['average_health_score']}/100")
        table.add_row("Verified (≥80)", str(summary["verified"]))
        table.add_row("Needs attention (<50)", str(summary["needs_attention"]))

        console.print()
        console.print(table)

        # Per-contact breakdown
        detail = Table(title="Contact Overview", box=box.SIMPLE, show_header=True)
        detail.add_column("ID", style="dim")
        detail.add_column("Name")
        detail.add_column("Company")
        detail.add_column("Health", justify="right")
        detail.add_column("Trackable", justify="center")

        for c in sorted(contacts, key=lambda x: x.data_health_score, reverse=True):
            score = c.data_health_score
            score_text = Text(str(score))
            if score >= 80:
                score_text.stylize("green")
            elif score >= 50:
                score_text.stylize("yellow")
            else:
                score_text.stylize("red")

            trackable = "✓" if c.tracking_eligible else "✗"
            trackable_style = "green" if c.tracking_eligible else "red"
            detail.add_row(
                c.id,
                c.full_name,
                c.company,
                score_text,
                Text(trackable, style=trackable_style),
            )

        console.print()
        console.print(detail)

    # ── Core agent loop ────────────────────────────────────────────────────────

    def _run_agent_iter(self, system_prompt: str, user_prompt: str):
        """
        Generator — yields event dicts consumed by both the console runner
        and the Streamlit UI.  Event shapes:
          {"type": "thinking",     "text": str}
          {"type": "text",         "text": str}
          {"type": "tool_call",    "name": str, "input": dict}
          {"type": "tool_result",  "name": str, "result": dict, "summary": str}
          {"type": "alert",        "contact": str, "old_company": str,
                                   "new_company": str, "old_title": str, "new_title": str}
        """
        messages = [{"role": "user", "content": user_prompt}]
        turn = 0

        while True:
            turn += 1
            yield {"type": "status", "text": f"Thinking (turn {turn})…"}

            response = self.client.messages.create(
                model=SCOUT_MODEL,
                max_tokens=8096,
                thinking={"type": "adaptive"},
                system=system_prompt,
                tools=ALL_TOOLS,
                messages=messages,
            )

            for block in response.content:
                if block.type == "thinking" and block.thinking.strip():
                    yield {"type": "thinking", "text": block.thinking}
                elif block.type == "text" and block.text.strip():
                    yield {"type": "text", "text": block.text}

            if response.stop_reason == "end_turn":
                break

            messages.append({"role": "assistant", "content": response.content})
            tool_results = []

            for block in response.content:
                if block.type != "tool_use":
                    continue

                yield {"type": "tool_call", "name": block.name, "input": block.input}

                result_str = self._dispatch_tool(block.name, block.input)
                result_data = json.loads(result_str)
                summary = self._fmt_tool_summary(block.name, result_data)
                yield {"type": "tool_result", "name": block.name,
                       "result": result_data, "summary": summary}

                # Surface job-change alerts as a dedicated event
                if block.name == "send_job_change_alert":
                    yield {
                        "type": "alert",
                        "contact":     block.input.get("contact_name", ""),
                        "old_company": block.input.get("old_company", ""),
                        "new_company": block.input.get("new_company", ""),
                        "old_title":   block.input.get("old_title", ""),
                        "new_title":   block.input.get("new_title", ""),
                    }

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_str,
                })

            messages.append({"role": "user", "content": tool_results})

    def _run_agent(self, system_prompt: str, user_prompt: str):
        """Console runner — iterates the generator and prints with Rich."""
        for event in self._run_agent_iter(system_prompt, user_prompt):
            t = event["type"]
            if t == "status":
                pass  # console uses its own status spinner at API call time
            elif t == "thinking":
                snippet = event["text"][:300].replace("\n", " ")
                if len(event["text"]) > 300:
                    snippet += "…"
                console.print(f"[dim italic]  💭 {snippet}[/dim italic]")
            elif t == "text":
                console.print(Panel(event["text"],
                                    title="[bold green]Scout[/bold green]",
                                    border_style="green"))
            elif t == "tool_call":
                console.print(f"  [cyan]🔧 {event['name']}[/cyan]  "
                               f"{self._format_input(event['input'])}")
            elif t == "tool_result":
                colour = ("yellow" if event["result"].get("job_change_detected")
                          else "green")
                console.print(f"    [{colour}]✓[/{colour}] {event['summary']}")

    # ── Tool dispatcher ────────────────────────────────────────────────────────

    def _dispatch_tool(self, name: str, inputs: dict) -> str:
        tool_map = {
            "get_contacts":          self._crm_tools.get_contacts,
            "get_contact_details":   self._crm_tools.get_contact_details,
            "find_duplicates":       self._crm_tools.find_duplicates,
            "merge_contacts":        self._crm_tools.merge_contacts,
            "standardize_contact":   self._crm_tools.standardize_contact,
            "check_linkedin":        self._enrichment_tools.check_linkedin,
            "check_zoominfo":        self._enrichment_tools.check_zoominfo,
            "update_contact":        self._crm_tools.update_contact,
            "send_job_change_alert": self._notification_tools.send_job_change_alert,
            "get_data_health_report": self._crm_tools.get_data_health_report,
        }

        fn = tool_map.get(name)
        if not fn:
            return json.dumps({"error": f"Unknown tool: {name}"})

        try:
            result = fn(**inputs)
            return json.dumps(result, default=str)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    # ── Display helpers ────────────────────────────────────────────────────────

    def _print_header(self, title: str, subtitle: str):
        console.print()
        console.rule(f"[bold blue]The Scout — {title}[/bold blue]")
        console.print(f"[dim]{subtitle}[/dim]")
        console.print()

    def _format_input(self, inputs: dict) -> str:
        """Compact, readable summary of tool inputs."""
        parts = []
        for k, v in inputs.items():
            val = str(v)
            if len(val) > 40:
                val = val[:37] + "…"
            parts.append(f"{k}={val!r}")
        return "  ".join(parts)

    def _fmt_tool_summary(self, tool_name: str, result: dict) -> str:
        """One-line human-readable summary of a tool result (shared by console + UI)."""
        if "error" in result:
            return f"Error: {result['error']}"
        mapping = {
            "get_contacts":           f"→ {result.get('count', 0)} contacts retrieved",
            "get_contact_details":    f"→ {result.get('full_name', '')} ({result.get('health_status', '')})",
            "find_duplicates":        f"→ {result.get('duplicate_groups_found', 0)} duplicate group(s) found",
            "merge_contacts":         f"→ Merged {result.get('removed_id', '')} into {result.get('primary_id', '')}",
            "standardize_contact":    f"→ {result.get('changes_made', 0)} fix(es): {', '.join(result.get('changes', [])[:2])}",
            "check_linkedin":         self._fmt_linkedin(result),
            "check_zoominfo":         f"→ {result.get('fields_verified', 0)} field(s) verified  email_valid={result.get('email_valid')}",
            "update_contact":         f"→ [{result.get('source','')}] {result.get('field','')} updated  score={result.get('new_health_score','')}",
            "send_job_change_alert":  f"→ Alert sent via {result.get('channels', [])}  prospective_lead={result.get('prospective_lead_created')}",
            "get_data_health_report": f"→ Avg score={result.get('average_health_score','')}  total={result.get('total_contacts','')}",
        }
        return mapping.get(tool_name, "→ done")

    def _fmt_linkedin(self, result: dict) -> str:
        if not result.get("found"):
            return "→ Profile not found"
        changed = result.get("job_change_detected", False)
        flag = " 🚨 JOB CHANGE DETECTED" if changed else ""
        return (
            f"→ {result.get('current_title','')} @ {result.get('current_company','')}"
            f"  conf={result.get('confidence','')}{flag}"
        )
