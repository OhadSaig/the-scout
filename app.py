"""
The Scout — Streamlit UI
Run with: streamlit run app.py
"""
from __future__ import annotations

import sys
import os
import time
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Scout",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .scout-header { font-size: 2rem; font-weight: 700; color: #4F8BF9; }
    .metric-card {
        background: #1E1E2E; border-radius: 10px;
        padding: 1rem 1.2rem; margin-bottom: 0.5rem;
    }
    .alert-card {
        background: #2D1B2E; border-left: 4px solid #FF4B4B;
        border-radius: 6px; padding: 0.8rem 1rem; margin-bottom: 0.5rem;
    }
    .tool-call {
        background: #1A2332; border-left: 3px solid #4F8BF9;
        border-radius: 4px; padding: 0.4rem 0.8rem;
        font-family: monospace; font-size: 0.85rem; margin: 2px 0;
    }
    .tool-ok   { color: #00CC88; font-size: 0.85rem; margin-left: 12px; }
    .tool-warn { color: #FFB800; font-size: 0.85rem; margin-left: 12px; }
    .thinking  {
        color: #888; font-style: italic; font-size: 0.8rem;
        border-left: 2px solid #444; padding-left: 8px; margin: 4px 0;
    }
    .gdpr-badge {
        background: #0E3A27; color: #00CC88;
        border-radius: 12px; padding: 2px 10px;
        font-size: 0.75rem; font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ── Shared CRM instance (persisted across reruns via session_state) ────────────
def get_crm():
    if "crm" not in st.session_state:
        from data.mock_crm import MockCRM
        st.session_state.crm = MockCRM()
    return st.session_state.crm


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 The Scout")
    st.markdown("*Autonomous CRM Perfectionist*")
    st.divider()

    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "🧹 Deep Clean", "📡 Career Tracker"],
        label_visibility="collapsed",
    )
    st.divider()

    dry_run = st.toggle("Dry-run mode (no API cost)", value=True)
    if not dry_run:
        api_key = st.text_input("Anthropic API Key", type="password",
                                placeholder="sk-ant-...")
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
    else:
        st.info("Using scripted mock — identical to real Claude output, zero cost.")

    st.divider()
    st.markdown('<span class="gdpr-badge">⚖️ GDPR Zero-Copy</span>',
                unsafe_allow_html=True)
    st.caption("All processing in-memory. No shadow database.")


# ══════════════════════════════════════════════════════════════════════════════
# Shared agent runner (used by both Deep Clean and Career Tracker pages)
# ══════════════════════════════════════════════════════════════════════════════
def run_agent_ui(mode: str):
    from agents.scout import ScoutAgent

    crm = get_crm()
    agent = ScoutAgent(dry_run=dry_run)
    agent.crm = crm  # use the shared CRM so dashboard reflects changes

    # Re-wire tool layer onto the shared CRM instance
    from tools.crm_tools import CRMTools
    agent._crm_tools = CRMTools(crm)

    col_log, col_alerts = st.columns([3, 2])

    with col_log:
        st.subheader("Agent Activity")
        log_container = st.empty()

    with col_alerts:
        st.subheader("🚨 Job Change Alerts")
        alert_container = st.empty()

    log_lines: list[str] = []
    alerts: list[dict] = []

    def render_log():
        log_container.markdown("\n\n".join(log_lines[-60:]), unsafe_allow_html=True)

    def render_alerts():
        if not alerts:
            alert_container.info("No job changes detected yet.")
            return
        html = ""
        for a in alerts:
            html += (
                f'<div class="alert-card">'
                f'<strong>🚨 {a["contact"]}</strong><br>'
                f'<span style="color:#aaa">{a["old_title"]} @ {a["old_company"]}</span><br>'
                f'<span style="color:#fff">➜ {a["new_title"]} @ {a["new_company"]}</span>'
                f'</div>'
            )
        alert_container.markdown(html, unsafe_allow_html=True)

    render_alerts()

    # Set up the right iterator
    if mode == "deep_clean":
        if dry_run:
            from dry_run import MockAnthropicClient, DEEP_CLEAN_TURNS
            agent.client = MockAnthropicClient(DEEP_CLEAN_TURNS)
        from agents.scout import DEEP_CLEAN_SYSTEM
        iterator = agent._run_agent_iter(DEEP_CLEAN_SYSTEM, "Begin the Utopian Deep Clean.")
    else:
        if dry_run:
            from dry_run import MockAnthropicClient, MONITOR_TURNS
            agent.client = MockAnthropicClient(MONITOR_TURNS)
        from agents.scout import MONITOR_SYSTEM
        iterator = agent._run_agent_iter(MONITOR_SYSTEM, "Run the Career Tracker.")

    for event in iterator:
        t = event["type"]

        if t == "status":
            log_lines.append(f'<span style="color:#888">⏳ {event["text"]}</span>')

        elif t == "thinking":
            snippet = event["text"][:200].replace("\n", " ")
            log_lines.append(f'<div class="thinking">💭 {snippet}{"…" if len(event["text"])>200 else ""}</div>')

        elif t == "text":
            # Convert markdown bold to HTML
            text = event["text"].replace("**", "<strong>", 1)
            while "**" in text:
                text = text.replace("**", "</strong>", 1).replace("**", "<strong>", 1)
            log_lines.append(
                f'<div style="background:#162032;border-left:3px solid #4F8BF9;'
                f'border-radius:4px;padding:8px 12px;margin:6px 0">{text}</div>'
            )

        elif t == "tool_call":
            args_str = "  ".join(f'{k}=<em>{str(v)[:40]}</em>' for k, v in event["input"].items())
            log_lines.append(
                f'<div class="tool-call">🔧 <strong>{event["name"]}</strong>  {args_str}</div>'
            )

        elif t == "tool_result":
            colour = "#FFB800" if event["result"].get("job_change_detected") else "#00CC88"
            log_lines.append(
                f'<span style="color:{colour};margin-left:16px;font-size:0.85rem">'
                f'✓ {event["summary"]}</span>'
            )

        elif t == "alert":
            alerts.append(event)
            render_alerts()

        render_log()
        time.sleep(0.05)   # slight pacing so the UI updates feel real

    log_lines.append('<br><strong style="color:#00CC88">✅ Done.</strong>')
    render_log()

    # Force dashboard to re-render with updated CRM data
    st.session_state.crm = crm
    st.success("Agent finished — switch to **📊 Dashboard** to see the updated CRM.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Dashboard
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown('<p class="scout-header">📊 CRM Dashboard</p>', unsafe_allow_html=True)
    st.caption("Live view of the in-memory CRM. Reflects all changes made by the agent.")

    crm = get_crm()
    summary = crm.summary()
    contacts = sorted(crm.get_all(), key=lambda c: c.data_health_score, reverse=True)

    # ── Top metrics ────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Contacts",    summary["total"])
    c2.metric("GDPR Trackable",    summary["trackable"],
              delta=f"-{summary['stale_gdpr']} stale", delta_color="inverse")
    c3.metric("Avg Health Score",  f"{summary['average_health_score']}/100")
    c4.metric("Verified (≥80)",    summary["verified"])
    c5.metric("Needs Attention",   summary["needs_attention"],
              delta=None if summary["needs_attention"] == 0 else "⚠️", delta_color="inverse")

    st.divider()

    # ── Health score bar chart ─────────────────────────────────────────────────
    import pandas as pd

    df = pd.DataFrame([
        {
            "Name": c.full_name,
            "Company": c.company,
            "Health Score": c.data_health_score,
            "Status": c.health_status,
            "GDPR Trackable": "✓" if c.tracking_eligible else "✗",
            "Email ✓": "✓" if c.email_verified else "✗",
            "Title ✓": "✓" if c.title_verified else "✗",
            "Company ✓": "✓" if c.company_verified else "✗",
            "Title": c.title,
            "Last Interaction": c.last_interaction_date.strftime("%Y-%m-%d"),
        }
        for c in contacts
    ])

    left, right = st.columns([3, 2])

    with left:
        st.subheader("Health Score by Contact")
        st.bar_chart(df.set_index("Name")["Health Score"], height=320)

    with right:
        st.subheader("Status Breakdown")
        verified  = sum(1 for c in contacts if c.data_health_score >= 80)
        partial   = sum(1 for c in contacts if 50 <= c.data_health_score < 80)
        attention = sum(1 for c in contacts if c.data_health_score < 50)
        breakdown_df = pd.DataFrame({
            "Status": ["Verified", "Partial", "Needs Attention"],
            "Count":  [verified, partial, attention],
        })
        st.bar_chart(breakdown_df.set_index("Status"), height=160)

        st.subheader("GDPR Window")
        gdpr_df = pd.DataFrame({
            "Category": ["Trackable (≤24 mo)", "Stale (>24 mo)"],
            "Count": [summary["trackable"], summary["stale_gdpr"]],
        })
        st.bar_chart(gdpr_df.set_index("Category"), height=120)

    st.divider()
    st.subheader("All Contacts")

    def _colour_score(val):
        if isinstance(val, float):
            if val >= 80:   return "background-color: #0E3A27; color: #00CC88"
            if val >= 50:   return "background-color: #3A3000; color: #FFB800"
            return "background-color: #3A1010; color: #FF4B4B"
        return ""

    styled = df.style.applymap(_colour_score, subset=["Health Score"])
    st.dataframe(styled, use_container_width=True, height=420)

    if st.button("🔄 Reset CRM to original data"):
        if "crm" in st.session_state:
            del st.session_state.crm
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Deep Clean
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧹 Deep Clean":
    st.markdown('<p class="scout-header">🧹 Utopian Deep Clean</p>',
                unsafe_allow_html=True)
    st.markdown(
        "One-time foundational pass: **merge duplicates**, **standardise formatting**, "
        "**verify titles via LinkedIn**, **validate emails via ZoomInfo**, and "
        "**fire job-change alerts** for eligible champions."
    )

    col1, col2, col3 = st.columns(3)
    col1.info("🔁 Deduplicates contacts")
    col2.info("✏️ Fixes name/phone/email formatting")
    col3.info("🔗 Cross-references LinkedIn + ZoomInfo")

    st.divider()

    if st.button("▶️ Run Deep Clean", type="primary", use_container_width=True):
        with st.spinner("Scout is working…"):
            run_agent_ui("deep_clean")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Career Tracker
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📡 Career Tracker":
    st.markdown('<p class="scout-header">📡 Career Tracker</p>',
                unsafe_allow_html=True)
    st.markdown(
        "Always-on scan of every GDPR-eligible contact. "
        "Detects **job changes**, updates the CRM, and sends **Proactive Change Alerts** "
        "to the sales team — no automated outreach to contacts."
    )

    col1, col2, col3 = st.columns(3)
    col1.info("👥 13 trackable contacts")
    col2.info("🚨 3 job changes in mock data")
    col3.info("⚖️ GDPR 12-mo alert window")

    st.divider()

    if st.button("▶️ Run Career Tracker", type="primary", use_container_width=True):
        with st.spinner("Scout is scanning…"):
            run_agent_ui("monitor")
