"""
The Scout — Streamlit UI
Run with: streamlit run app.py
"""
from __future__ import annotations

import re
import sys
import os
import time
import datetime
import streamlit as st
import pandas as pd

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
    /* ── Global ── */
    [data-testid="stAppViewContainer"] { background: #0D1117; }
    [data-testid="stSidebar"] { background: #161B22; border-right: 1px solid #30363D; }

    /* ── Page hero header ── */
    .page-hero {
        background: linear-gradient(135deg, #1a2845 0%, #0D1117 60%);
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 1.6rem 2rem 1.4rem;
        margin-bottom: 1.5rem;
    }
    .page-hero h1 { font-size: 1.9rem; font-weight: 700; color: #E6EDF3; margin: 0 0 0.3rem; }
    .page-hero p  { color: #8B949E; font-size: 0.95rem; margin: 0; }

    /* ── Stat pills on feature pages ── */
    .stat-pill {
        display: inline-flex; align-items: center; gap: 6px;
        background: #1C2128; border: 1px solid #30363D;
        border-radius: 20px; padding: 6px 14px;
        font-size: 0.85rem; color: #C9D1D9;
    }
    .stat-pill strong { color: #58A6FF; }

    /* ── Alert cards ── */
    .alert-card {
        background: #1C1117;
        border: 1px solid #6E2B2B;
        border-left: 4px solid #FF4B4B;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.6rem;
        animation: pulse-border 2s ease-in-out infinite;
    }
    .alert-card .contact-name { font-weight: 700; color: #FF7070; font-size: 1rem; }
    .alert-card .old-role { color: #8B949E; font-size: 0.85rem; margin-top: 4px; }
    .alert-card .new-role { color: #E6EDF3; font-size: 0.9rem; font-weight: 600; margin-top: 2px; }
    @keyframes pulse-border {
        0%, 100% { border-left-color: #FF4B4B; }
        50%       { border-left-color: #FF8080; }
    }

    /* ── Agent log items ── */
    .log-tool {
        background: #161B22; border-left: 3px solid #58A6FF;
        border-radius: 6px; padding: 5px 10px;
        font-family: 'SF Mono', monospace; font-size: 0.82rem;
        color: #C9D1D9; margin: 3px 0;
    }
    .log-tool .tool-name { color: #79C0FF; font-weight: 600; }
    .log-ok   { color: #3FB950; font-size: 0.82rem; margin-left: 14px; }
    .log-warn { color: #D29922; font-size: 0.82rem; margin-left: 14px; }
    .log-text {
        background: #161B22; border-left: 3px solid #58A6FF;
        border-radius: 6px; padding: 10px 14px; margin: 8px 0;
        color: #C9D1D9; font-size: 0.9rem; line-height: 1.55;
    }
    .log-thinking {
        color: #6E7681; font-style: italic; font-size: 0.78rem;
        border-left: 2px solid #30363D; padding-left: 8px;
        margin: 2px 0 2px 4px;
    }
    .log-status { color: #6E7681; font-size: 0.8rem; padding: 2px 0; }
    .log-done { color: #3FB950; font-weight: 700; font-size: 0.95rem; margin-top: 8px; }

    /* ── GDPR badge ── */
    .gdpr-badge {
        display: inline-flex; align-items: center; gap: 5px;
        background: #0D2119; color: #3FB950;
        border: 1px solid #1E4D33;
        border-radius: 20px; padding: 4px 12px;
        font-size: 0.78rem; font-weight: 600;
    }

    /* ── Feature info cards ── */
    .feature-card {
        background: #161B22; border: 1px solid #30363D;
        border-radius: 8px; padding: 0.9rem 1rem;
        text-align: center;
    }
    .feature-card .fc-icon { font-size: 1.5rem; }
    .feature-card .fc-label { font-size: 0.85rem; color: #8B949E; margin-top: 4px; }

    /* ── Next-step banner ── */
    .next-step {
        background: #0D2119; border: 1px solid #1E4D33;
        border-radius: 8px; padding: 0.9rem 1.1rem;
        color: #3FB950; margin-top: 1rem; font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def md_to_html(text: str) -> str:
    """Convert a small subset of Markdown to HTML (bold, newlines)."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = text.replace("\n", "<br>")
    return text


def get_crm():
    if "crm" not in st.session_state:
        from data.mock_crm import MockCRM
        st.session_state.crm = MockCRM()
    return st.session_state.crm


def _health_status(score: float) -> str:
    if score >= 80: return "Verified"
    if score >= 50: return "Partial"
    return "Needs Attention"


def _score_color(score: float) -> str:
    if score >= 80: return "#3FB950"
    if score >= 50: return "#D29922"
    return "#F85149"


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
        st.caption("Scripted mock — full agent flow, zero cost.")

    st.divider()

    # Live CRM pulse in sidebar
    crm_sb = get_crm()
    sb_summary = crm_sb.summary()
    sb_col1, sb_col2 = st.columns(2)
    sb_col1.metric("Contacts", sb_summary["total"])
    sb_col2.metric("Avg Health", f"{sb_summary['average_health_score']:.0f}")

    st.divider()
    st.markdown('<span class="gdpr-badge">⚖️ GDPR Zero-Copy</span>',
                unsafe_allow_html=True)
    st.caption("All processing in-memory. No shadow database.")


# ══════════════════════════════════════════════════════════════════════════════
# Shared agent runner
# ══════════════════════════════════════════════════════════════════════════════
def run_agent_ui(mode: str):
    from agents.scout import ScoutAgent

    crm = get_crm()
    agent = ScoutAgent(dry_run=dry_run)
    agent.crm = crm

    from tools.crm_tools import CRMTools
    agent._crm_tools = CRMTools(crm)

    col_log, col_alerts = st.columns([3, 2])

    with col_log:
        st.markdown("**Agent Activity**")
        log_container = st.empty()

    with col_alerts:
        st.markdown("**🚨 Job-Change Alerts**")
        alert_container = st.empty()

    log_lines: list[str] = []
    alerts: list[dict] = []
    tool_step = 0
    start_time = time.time()

    def render_log():
        log_container.markdown(
            '<div style="max-height:520px;overflow-y:auto">'
            + "\n".join(log_lines[-80:])
            + "</div>",
            unsafe_allow_html=True,
        )

    def render_alerts():
        if not alerts:
            alert_container.info("No job changes detected yet.")
            return
        html = ""
        for a in alerts:
            html += (
                f'<div class="alert-card">'
                f'<div class="contact-name">🚨 {a["contact"]}</div>'
                f'<div class="old-role">📌 {a["old_title"]} @ {a["old_company"]}</div>'
                f'<div class="new-role">➜ {a["new_title"]} @ {a["new_company"]}</div>'
                f'</div>'
            )
        alert_container.markdown(html, unsafe_allow_html=True)

    render_alerts()

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
            log_lines.append(f'<div class="log-status">⏳ {event["text"]}</div>')

        elif t == "thinking":
            snippet = event["text"][:120].replace("\n", " ")
            if len(event["text"]) > 120:
                snippet += "…"
            log_lines.append(f'<div class="log-thinking">💭 {snippet}</div>')

        elif t == "text":
            log_lines.append(f'<div class="log-text">{md_to_html(event["text"])}</div>')

        elif t == "tool_call":
            tool_step += 1
            args_str = "  ".join(
                f'<span style="color:#8B949E">{k}</span>=<em style="color:#A5D6FF">{str(v)[:35]}</em>'
                for k, v in event["input"].items()
            )
            log_lines.append(
                f'<div class="log-tool">'
                f'<span style="color:#6E7681;font-size:0.75rem">#{tool_step}</span> '
                f'<span class="tool-name">{event["name"]}</span>  {args_str}'
                f'</div>'
            )

        elif t == "tool_result":
            if event["result"].get("job_change_detected"):
                log_lines.append(f'<div class="log-warn">⚡ {event["summary"]}</div>')
            elif "error" in event["result"]:
                log_lines.append(f'<div style="color:#F85149;font-size:0.82rem;margin-left:14px">✗ {event["summary"]}</div>')
            else:
                log_lines.append(f'<div class="log-ok">✓ {event["summary"]}</div>')

        elif t == "alert":
            alerts.append(event)
            render_alerts()

        render_log()
        time.sleep(0.04)

    elapsed = time.time() - start_time
    log_lines.append(f'<div class="log-done">✅ Done in {elapsed:.1f}s — {tool_step} tool calls</div>')
    render_log()

    st.session_state.crm = crm
    st.session_state[f"last_run_{mode}"] = datetime.datetime.now().strftime("%H:%M:%S")

    st.markdown(
        f'<div class="next-step">✅ Agent finished in <strong>{elapsed:.1f}s</strong> '
        f'with <strong>{tool_step}</strong> tool calls and '
        f'<strong>{len(alerts)}</strong> alert(s) fired.<br>'
        f'Switch to <strong>📊 Dashboard</strong> in the sidebar to see the updated CRM.</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Dashboard
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("""
    <div class="page-hero">
        <h1>📊 CRM Dashboard</h1>
        <p>Live view of the in-memory CRM — reflects every change made by the agent.</p>
    </div>
    """, unsafe_allow_html=True)

    crm = get_crm()
    summary = crm.summary()
    contacts = sorted(crm.get_all(), key=lambda c: c.data_health_score, reverse=True)

    # ── Top metrics ────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Contacts",   summary["total"])
    c2.metric("GDPR Trackable",   summary["trackable"],
              delta=f"-{summary['stale_gdpr']} stale", delta_color="inverse")
    c3.metric("Avg Health Score", f"{summary['average_health_score']:.1f}/100")
    c4.metric("Verified (≥80)",   summary["verified"])
    c5.metric("Needs Attention",  summary["needs_attention"],
              delta=None if summary["needs_attention"] == 0 else "⚠️",
              delta_color="inverse")

    st.divider()

    # ── Charts ─────────────────────────────────────────────────────────────────
    import altair as alt

    chart_data = pd.DataFrame([
        {
            "Name": c.full_name,
            "Score": c.data_health_score,
            "Status": _health_status(c.data_health_score),
        }
        for c in contacts
    ])

    color_scale = alt.Scale(
        domain=["Verified", "Partial", "Needs Attention"],
        range=["#3FB950", "#D29922", "#F85149"],
    )

    health_chart = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X("Score:Q", scale=alt.Scale(domain=[0, 100]),
                    axis=alt.Axis(title="Health Score")),
            y=alt.Y("Name:N", sort="-x", axis=alt.Axis(title=None)),
            color=alt.Color("Status:N", scale=color_scale,
                            legend=alt.Legend(title="Status")),
            tooltip=["Name:N", "Score:Q", "Status:N"],
        )
        .properties(height=420, title="Data Health Score by Contact")
        .configure_view(strokeWidth=0)
        .configure_axis(labelColor="#8B949E", titleColor="#8B949E", gridColor="#21262D")
        .configure_title(color="#C9D1D9")
        .configure_legend(labelColor="#C9D1D9", titleColor="#8B949E")
    )

    left, right = st.columns([3, 2])

    with left:
        st.altair_chart(health_chart, use_container_width=True)

    with right:
        verified  = sum(1 for c in contacts if c.data_health_score >= 80)
        partial   = sum(1 for c in contacts if 50 <= c.data_health_score < 80)
        attention = sum(1 for c in contacts if c.data_health_score < 50)

        st.markdown("**Status Breakdown**")
        breakdown_df = pd.DataFrame({
            "Status": ["Verified", "Partial", "Needs Attention"],
            "Count":  [verified, partial, attention],
        })
        status_chart = (
            alt.Chart(breakdown_df)
            .mark_bar(cornerRadiusEnd=4)
            .encode(
                x=alt.X("Count:Q", axis=alt.Axis(tickMinStep=1)),
                y=alt.Y("Status:N", sort=None),
                color=alt.Color("Status:N", scale=color_scale, legend=None),
                tooltip=["Status:N", "Count:Q"],
            )
            .properties(height=130)
            .configure_view(strokeWidth=0)
            .configure_axis(labelColor="#8B949E", titleColor="#8B949E", gridColor="#21262D")
        )
        st.altair_chart(status_chart, use_container_width=True)

        st.markdown("**GDPR Tracking Window**")
        gdpr_df = pd.DataFrame({
            "Category": ["Trackable (≤24 mo)", "Stale (>24 mo)"],
            "Count": [summary["trackable"], summary["stale_gdpr"]],
        })
        gdpr_chart = (
            alt.Chart(gdpr_df)
            .mark_bar(cornerRadiusEnd=4)
            .encode(
                x=alt.X("Count:Q", axis=alt.Axis(tickMinStep=1)),
                y=alt.Y("Category:N", sort=None),
                color=alt.condition(
                    alt.datum.Category == "Trackable (≤24 mo)",
                    alt.value("#3FB950"),
                    alt.value("#F85149"),
                ),
                tooltip=["Category:N", "Count:Q"],
            )
            .properties(height=100)
            .configure_view(strokeWidth=0)
            .configure_axis(labelColor="#8B949E", gridColor="#21262D")
        )
        st.altair_chart(gdpr_chart, use_container_width=True)

    st.divider()
    st.markdown("**All Contacts**")

    df = pd.DataFrame([
        {
            "Name": c.full_name,
            "Title": c.title or "—",
            "Company": c.company,
            "Health": c.data_health_score,
            "Status": _health_status(c.data_health_score),
            "GDPR": "✓" if c.tracking_eligible else "✗",
            "Email ✓": "✓" if c.email_verified else "✗",
            "Title ✓": "✓" if c.title_verified else "✗",
            "Last Interaction": c.last_interaction_date.strftime("%Y-%m-%d"),
        }
        for c in contacts
    ])

    def _style_health(val):
        if not isinstance(val, (int, float)):
            return ""
        if val >= 80:   return "background-color: #0D2119; color: #3FB950; font-weight:600"
        if val >= 50:   return "background-color: #2D2000; color: #D29922; font-weight:600"
        return "background-color: #2D0D0D; color: #F85149; font-weight:600"

    styled = df.style.map(_style_health, subset=["Health"])
    st.dataframe(styled, use_container_width=True, height=420)

    if st.button("🔄 Reset CRM to original data", use_container_width=False):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Deep Clean
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧹 Deep Clean":
    last_run = st.session_state.get("last_run_deep_clean")
    last_run_str = f" &nbsp;·&nbsp; Last run: {last_run}" if last_run else ""
    st.markdown(f"""
    <div class="page-hero">
        <h1>🧹 Utopian Deep Clean</h1>
        <p>One-time foundational pass — merge duplicates, fix formatting, verify via
        LinkedIn &amp; ZoomInfo, fire job-change alerts for eligible contacts.{last_run_str}</p>
    </div>
    """, unsafe_allow_html=True)

    # Dynamic stats from live CRM
    from tools.crm_tools import CRMTools as _CRMTools
    crm = get_crm()
    contacts_all = crm.get_all()
    dupes_count  = _CRMTools(crm).find_duplicates().get("duplicate_groups_found", 0)
    bad_fmt      = sum(1 for c in contacts_all
                       if not c.email_verified or not c.title or not c.company_verified)
    with_li      = sum(1 for c in contacts_all if c.linkedin_url)

    fc1, fc2, fc3, fc4 = st.columns(4)
    fc1.metric("Total contacts",     len(contacts_all))
    fc2.metric("Duplicate groups",   dupes_count)
    fc3.metric("Need formatting fix", bad_fmt)
    fc4.metric("Have LinkedIn URL",  with_li)

    st.divider()

    already_ran = last_run is not None
    btn_label = "▶️ Run Again" if already_ran else "▶️ Run Deep Clean"

    if st.button(btn_label, type="primary", use_container_width=True):
        run_agent_ui("deep_clean")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Career Tracker
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📡 Career Tracker":
    last_run = st.session_state.get("last_run_monitor")
    last_run_str = f" &nbsp;·&nbsp; Last run: {last_run}" if last_run else ""
    st.markdown(f"""
    <div class="page-hero">
        <h1>📡 Career Tracker</h1>
        <p>Always-on scan of every GDPR-eligible contact — detects job changes and
        sends Proactive Change Alerts to the sales team.{last_run_str}</p>
    </div>
    """, unsafe_allow_html=True)

    # Dynamic stats from live CRM
    crm = get_crm()
    summary = crm.summary()
    contacts_all = crm.get_all()
    trackable    = [c for c in contacts_all if c.tracking_eligible]
    alert_elig   = [c for c in trackable if c.alert_eligible]
    with_li      = sum(1 for c in trackable if c.linkedin_url)

    fc1, fc2, fc3, fc4 = st.columns(4)
    fc1.metric("Trackable contacts",   len(trackable),
               help="Last interaction ≤ 24 months (GDPR tracking window)")
    fc2.metric("Alert-eligible",       len(alert_elig),
               help="Last interaction ≤ 12 months — alerts will fire on job change")
    fc3.metric("With LinkedIn URL",    with_li)
    fc4.metric("Stale / excluded",     summary["stale_gdpr"],
               delta="outside GDPR window", delta_color="off")

    st.divider()

    already_ran = last_run is not None
    btn_label = "▶️ Run Again" if already_ran else "▶️ Run Career Tracker"

    if st.button(btn_label, type="primary", use_container_width=True):
        run_agent_ui("monitor")
