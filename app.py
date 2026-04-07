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

st.set_page_config(
    page_title="The Scout",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design tokens (Linear + Vercel-inspired zinc/indigo palette) ──────────────
# Backgrounds
_BG       = "#09090B"   # zinc-950
_SURF     = "#18181B"   # zinc-900  (cards, panels)
_SURF2    = "#27272A"   # zinc-800  (inputs, hover)
_BORDER   = "#3F3F46"   # zinc-700
_BORDER2  = "#52525B"   # zinc-600  (emphasized)

# Text
_T1 = "#FAFAFA"   # zinc-50   — headings, numbers
_T2 = "#D4D4D8"   # zinc-300  — body copy, labels
_T3 = "#A1A1AA"   # zinc-400  — secondary labels
_T4 = "#71717A"   # zinc-500  — captions, muted

# Accent
_ACC     = "#818CF8"   # indigo-400
_ACC_DIM = "#312E81"   # indigo-900 (accent bg tint)
_ACC_BG  = "rgba(129,140,248,0.08)"

# Status
_GREEN    = "#34D399"   # emerald-400
_YELLOW   = "#FBBF24"   # amber-400
_RED      = "#F87171"   # rose-400
_G_BG     = "#022C22"   # emerald-950
_Y_BG     = "#431407"   # orange-950 (amber bg)
_R_BG     = "#450A0A"   # red-950

CSS = f"""
<style>
/* ══ Base ═══════════════════════════════════════════════════════════════════ */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main, .main .block-container {{
    background: {_BG} !important;
    color: {_T1} !important;
}}
[data-testid="stSidebar"] {{
    background: #0C0C0E !important;
    border-right: 1px solid {_BORDER} !important;
}}
/* Fix Streamlit's own top toolbar */
[data-testid="stHeader"] {{ background: {_BG} !important; }}

/* ══ Typography ═════════════════════════════════════════════════════════════ */
h1,h2,h3,h4 {{ color: {_T1} !important; letter-spacing:-0.02em; }}
p, li {{ color: {_T2} !important; }}
[data-testid="stMarkdown"] p {{ color: {_T2} !important; }}
[data-testid="stCaptionContainer"] p,
.stCaption {{ color: {_T4} !important; font-size: 0.8rem !important; }}
label {{ color: {_T3} !important; }}

/* ══ Metric cards ═══════════════════════════════════════════════════════════ */
[data-testid="metric-container"] {{
    background: {_SURF} !important;
    border: 1px solid {_BORDER} !important;
    border-radius: 10px !important;
    padding: 18px 20px 14px !important;
}}
[data-testid="stMetricValue"] {{
    color: {_T1} !important;
    font-size: 2.1rem !important;
    font-weight: 700 !important;
    line-height: 1.15 !important;
}}
[data-testid="stMetricLabel"] {{
    color: {_T3} !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}}
[data-testid="stMetricDelta"] > div {{
    color: {_T4} !important;
    font-size: 0.78rem !important;
}}

/* ══ Divider ════════════════════════════════════════════════════════════════ */
hr {{ border-color: {_BORDER} !important; opacity:1 !important; margin: 1.2rem 0 !important; }}

/* ══ Sidebar nav ════════════════════════════════════════════════════════════ */
[data-testid="stRadio"] > label {{
    color: {_T3} !important; font-size: 0.72rem !important;
    text-transform: uppercase; letter-spacing: 0.06em;
}}
[data-testid="stRadio"] div[role="radiogroup"] {{
    display: flex; flex-direction: column; gap: 2px;
}}
[data-testid="stRadio"] label[data-baseweb="radio"] {{
    background: transparent !important; border-radius: 7px !important;
    padding: 8px 12px !important; color: {_T2} !important;
    font-size: 0.9rem !important; transition: background 0.12s;
}}
[data-testid="stRadio"] label[data-baseweb="radio"]:hover {{
    background: {_SURF2} !important;
}}

/* ══ Toggle ═════════════════════════════════════════════════════════════════ */
[data-testid="stToggle"] p, [data-testid="stToggle"] span {{
    color: {_T2} !important; font-size: 0.88rem !important;
}}

/* ══ Text input ═════════════════════════════════════════════════════════════ */
[data-testid="stTextInput"] input {{
    background: {_SURF2} !important; color: {_T1} !important;
    border-color: {_BORDER} !important; border-radius: 7px !important;
}}
[data-testid="stTextInput"] input::placeholder {{ color: {_T4} !important; }}

/* ══ Buttons ════════════════════════════════════════════════════════════════ */
button[kind="primary"] {{
    background: {_ACC} !important; color: #fff !important;
    border: none !important; font-weight: 600 !important;
    border-radius: 8px !important; font-size: 0.95rem !important;
    letter-spacing: 0.01em !important; transition: all 0.15s !important;
}}
button[kind="primary"]:hover {{
    background: #6366F1 !important;
    box-shadow: 0 0 0 3px rgba(129,140,248,0.3) !important;
    transform: translateY(-1px) !important;
}}
button[kind="secondary"] {{
    background: {_SURF2} !important; color: {_T2} !important;
    border: 1px solid {_BORDER} !important; border-radius: 8px !important;
}}
button[kind="secondary"]:hover {{
    background: {_BORDER} !important; color: {_T1} !important;
}}

/* ══ Dataframe ══════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {{
    border: 1px solid {_BORDER} !important;
    border-radius: 10px !important; overflow: hidden !important;
}}
/* Header row */
[data-testid="stDataFrame"] .dvn-scroller th,
[data-testid="stDataFrame"] [role="columnheader"] {{
    background: {_SURF2} !important; color: {_T3} !important;
    font-weight: 700 !important; font-size: 0.75rem !important;
    text-transform: uppercase !important; letter-spacing: 0.05em !important;
}}
/* Data cells */
[data-testid="stDataFrame"] [role="gridcell"] {{
    background: {_SURF} !important; color: {_T1} !important;
    font-size: 0.88rem !important;
}}
[data-testid="stDataFrame"] [role="row"]:hover [role="gridcell"] {{
    background: {_SURF2} !important;
}}

/* ══ Info / success banners ═════════════════════════════════════════════════ */
[data-testid="stAlert"][data-baseweb="notification"] {{
    background: {_SURF} !important;
    border: 1px solid {_BORDER} !important;
    border-radius: 8px !important;
    color: {_T2} !important;
}}

/* ══ Vega/Altair chart bg ═══════════════════════════════════════════════════ */
.vega-embed, .vega-embed canvas {{ background: transparent !important; }}
.vega-embed summary {{ display:none !important; }}

/* ══ Scrollbar ══════════════════════════════════════════════════════════════ */
::-webkit-scrollbar {{ width:5px; height:5px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:{_BORDER}; border-radius:3px; }}

/* ══ Page hero ══════════════════════════════════════════════════════════════ */
.page-hero {{
    background: {_SURF};
    border: 1px solid {_BORDER};
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.4rem;
    position: relative; overflow: hidden;
}}
.page-hero::after {{
    content: '';
    position: absolute; inset: 0 auto 0 0;
    width: 3px; background: linear-gradient(180deg,{_ACC},#6366f1);
    border-radius: 12px 0 0 12px;
}}
.page-hero h1 {{
    font-size: 1.7rem !important; font-weight: 700 !important;
    color: {_T1} !important; margin: 0 0 0.3rem !important;
    letter-spacing: -0.025em !important;
}}
.page-hero p {{ color: {_T3} !important; font-size: 0.88rem !important; margin:0 !important; }}
.hero-tag {{
    display: inline-block;
    background: {_ACC_BG}; color: {_ACC};
    border: 1px solid rgba(129,140,248,0.25);
    border-radius: 20px; padding: 1px 9px;
    font-size: 0.72rem; font-weight: 600;
    margin-left: 8px; vertical-align: middle;
}}

/* ══ Agent log panel ════════════════════════════════════════════════════════ */
.log-wrap {{
    background: {_SURF};
    border: 1px solid {_BORDER};
    border-radius: 10px;
    padding: 12px 14px;
    max-height: 560px; overflow-y: auto;
    font-size: 0.82rem; line-height: 1.65;
}}
.log-tool {{
    background: {_SURF2}; border-left: 2px solid {_ACC};
    border-radius: 6px; padding: 5px 10px;
    font-family: 'SF Mono','Fira Code',monospace; margin: 3px 0;
}}
.log-tool .tn  {{ color: {_ACC}; font-weight: 700; }}
.log-tool .tk  {{ color: {_T4}; }}
.log-tool .tv  {{ color: #93C5FD; font-style: italic; }}
.log-tool .stp {{ color: {_T4}; font-size: 0.72rem; }}
.log-ok   {{ color: {_GREEN};  display:block; padding: 1px 0 1px 14px; }}
.log-warn {{ color: {_YELLOW}; display:block; padding: 1px 0 1px 14px; }}
.log-err  {{ color: {_RED};    display:block; padding: 1px 0 1px 14px; }}
.log-text {{
    background: {_ACC_BG}; border-left: 2px solid {_ACC};
    border-radius: 6px; padding: 9px 13px; margin: 6px 0;
    color: {_T1};
}}
.log-think {{
    color: {_T4}; font-style: italic;
    border-left: 2px solid {_BORDER};
    padding-left: 8px; margin: 2px 0; font-size: 0.77rem;
}}
.log-status {{ color:{_T4}; padding:1px 0; }}
.log-done   {{ color:{_GREEN}; font-weight:700; display:block; padding-top:8px; border-top:1px solid {_BORDER}; margin-top:6px; }}

/* ══ Alert cards ════════════════════════════════════════════════════════════ */
.alert-wrap {{ display:flex; flex-direction:column; gap:8px; }}
.alert-card {{
    background: {_R_BG};
    border: 1px solid rgba(248,113,113,0.2);
    border-left: 3px solid {_RED};
    border-radius: 8px; padding: 12px 14px;
}}
.alert-name  {{ font-weight:700; color:{_RED}; font-size:0.92rem; margin-bottom:5px; }}
.alert-from  {{ color:{_T4}; font-size:0.8rem; }}
.alert-to    {{ color:{_T1}; font-weight:600; font-size:0.85rem; margin-top:4px; }}
.alert-arrow {{ color:{_ACC}; }}
.alert-empty {{
    color:{_T4}; font-size:0.85rem; text-align:center;
    padding: 32px 0; border: 1px dashed {_BORDER};
    border-radius: 8px;
}}

/* ══ Finish banner ══════════════════════════════════════════════════════════ */
.finish-banner {{
    background: {_G_BG};
    border: 1px solid rgba(52,211,153,0.2);
    border-radius: 8px; padding: 12px 16px; margin-top:12px;
    color: {_GREEN}; font-size: 0.88rem; line-height: 1.5;
}}
.finish-banner strong {{ color: {_T1}; }}

/* ══ GDPR badge ═════════════════════════════════════════════════════════════ */
.gdpr-badge {{
    display:inline-flex; align-items:center; gap:5px;
    background: {_G_BG}; color: {_GREEN};
    border: 1px solid rgba(52,211,153,0.2);
    border-radius: 20px; padding: 4px 11px;
    font-size: 0.76rem; font-weight: 600;
}}

/* ══ Section micro-header ═══════════════════════════════════════════════════ */
.micro-header {{
    font-size: 0.72rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.07em;
    color: {_T4}; margin-bottom: 8px; margin-top: 4px;
}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def md_to_html(text: str) -> str:
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


def _altair_cfg(chart):
    """Apply shared dark-theme Altair config."""
    import altair as alt
    return (
        chart
        .configure_view(strokeWidth=0, fill="transparent")
        .configure_axis(
            labelColor=_T3, titleColor=_T4,
            gridColor="#27272A", domainColor=_BORDER,
            labelFontSize=11, tickColor="transparent",
        )
        .configure_legend(
            labelColor=_T2, titleColor=_T3,
            labelFontSize=11, titleFontSize=10,
        )
        .configure_title(color=_T2, fontSize=13, fontWeight=600)
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="padding:4px 4px 12px">'
        f'<span style="font-size:1.25rem;font-weight:700;color:{_T1}">🔍 The Scout</span><br>'
        f'<span style="font-size:0.78rem;color:{_T4}">Autonomous CRM Perfectionist</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    page = st.radio(
        "Pages",
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
        st.markdown(
            f'<p style="font-size:0.78rem;color:{_T4};margin-top:4px">'
            f'Scripted mock — full agent flow, zero API cost.</p>',
            unsafe_allow_html=True,
        )
    st.divider()

    # Live CRM pulse
    crm_sb   = get_crm()
    sb_summ  = crm_sb.summary()
    sb1, sb2 = st.columns(2)
    sb1.metric("Contacts", sb_summ["total"])
    sb2.metric("Avg Health", f"{sb_summ['average_health_score']:.0f}")

    st.divider()
    st.markdown('<span class="gdpr-badge">⚖️ GDPR Zero-Copy</span>',
                unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:0.76rem;color:{_T4};margin-top:6px">'
        f'In-memory only · No shadow database</p>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# Shared agent runner
# ══════════════════════════════════════════════════════════════════════════════
def run_agent_ui(mode: str):
    from agents.scout import ScoutAgent

    crm   = get_crm()
    agent = ScoutAgent(dry_run=dry_run)
    agent.crm = crm
    from tools.crm_tools import CRMTools
    agent._crm_tools = CRMTools(crm)

    col_log, col_alerts = st.columns([3, 2], gap="medium")

    with col_log:
        st.markdown('<div class="micro-header">Agent Activity</div>',
                    unsafe_allow_html=True)
        log_container = st.empty()

    with col_alerts:
        st.markdown('<div class="micro-header">Job-Change Alerts</div>',
                    unsafe_allow_html=True)
        alert_container = st.empty()

    log_lines: list[str] = []
    alerts:    list[dict] = []
    tool_step = 0
    start_ts  = time.time()

    def render_log():
        log_container.markdown(
            f'<div class="log-wrap">{"".join(log_lines[-80:])}</div>',
            unsafe_allow_html=True,
        )

    def render_alerts():
        if not alerts:
            alert_container.markdown(
                '<div class="alert-empty">No job changes detected yet.</div>',
                unsafe_allow_html=True,
            )
            return
        html = '<div class="alert-wrap">'
        for a in alerts:
            html += (
                f'<div class="alert-card">'
                f'<div class="alert-name">🚨 {a["contact"]}</div>'
                f'<div class="alert-from">{a["old_title"]} @ {a["old_company"]}</div>'
                f'<div class="alert-to"><span class="alert-arrow">→</span> '
                f'{a["new_title"]} @ {a["new_company"]}</div>'
                f'</div>'
            )
        html += '</div>'
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
            snip = event["text"][:110].replace("\n", " ")
            if len(event["text"]) > 110:
                snip += "…"
            log_lines.append(f'<div class="log-think">💭 {snip}</div>')

        elif t == "text":
            log_lines.append(f'<div class="log-text">{md_to_html(event["text"])}</div>')

        elif t == "tool_call":
            tool_step += 1
            args_html = "  ".join(
                f'<span class="tk">{k}</span>=<span class="tv">{str(v)[:35]}</span>'
                for k, v in event["input"].items()
            )
            log_lines.append(
                f'<div class="log-tool">'
                f'<span class="stp">#{tool_step}</span> '
                f'<span class="tn">{event["name"]}</span>  {args_html}'
                f'</div>'
            )

        elif t == "tool_result":
            if event["result"].get("job_change_detected"):
                log_lines.append(f'<span class="log-warn">⚡ {event["summary"]}</span>')
            elif "error" in event["result"]:
                log_lines.append(f'<span class="log-err">✗ {event["summary"]}</span>')
            else:
                log_lines.append(f'<span class="log-ok">✓ {event["summary"]}</span>')

        elif t == "alert":
            alerts.append(event)
            render_alerts()

        render_log()
        time.sleep(0.04)

    elapsed = time.time() - start_ts
    log_lines.append(
        f'<span class="log-done">✅ Completed in {elapsed:.1f}s · {tool_step} tool calls</span>'
    )
    render_log()

    st.session_state.crm = crm
    st.session_state[f"last_run_{mode}"] = datetime.datetime.now().strftime("%H:%M:%S")

    st.markdown(
        f'<div class="finish-banner">'
        f'✅ Done in <strong>{elapsed:.1f}s</strong> — '
        f'<strong>{tool_step}</strong> tool calls, '
        f'<strong>{len(alerts)}</strong> alert(s) fired.<br>'
        f'Switch to <strong>📊 Dashboard</strong> to see the updated CRM.'
        f'</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Dashboard
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    import altair as alt

    st.markdown(
        '<div class="page-hero"><h1>📊 CRM Dashboard</h1>'
        '<p>Live view of the in-memory CRM — every agent change is reflected here in real time.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    crm      = get_crm()
    summary  = crm.summary()
    contacts = sorted(crm.get_all(), key=lambda c: c.data_health_score, reverse=True)

    # ── Metrics row ───────────────────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Contacts",   summary["total"])
    m2.metric("GDPR Trackable",   summary["trackable"],
              delta=f"−{summary['stale_gdpr']} stale", delta_color="inverse")
    m3.metric("Avg Health Score", f"{summary['average_health_score']:.1f}/100")
    m4.metric("Verified (≥ 80)",  summary["verified"])
    m5.metric("Needs Attention",  summary["needs_attention"],
              delta=None if summary["needs_attention"] == 0 else "⚠️",
              delta_color="inverse")

    st.divider()

    # ── Charts ────────────────────────────────────────────────────────────────
    chart_df = pd.DataFrame([
        {
            "Name":   c.full_name,
            "Score":  c.data_health_score,
            "Status": _health_status(c.data_health_score),
        }
        for c in contacts
    ])

    status_scale = alt.Scale(
        domain=["Verified", "Partial", "Needs Attention"],
        range=[_GREEN, _YELLOW, _RED],
    )

    health_chart = _altair_cfg(
        alt.Chart(chart_df)
        .mark_bar(cornerRadiusEnd=3, height=18)
        .encode(
            x=alt.X("Score:Q", scale=alt.Scale(domain=[0, 100]),
                    axis=alt.Axis(title="Health Score", labelColor=_T3)),
            y=alt.Y("Name:N", sort="-x",
                    axis=alt.Axis(title=None, labelColor=_T2)),
            color=alt.Color("Status:N", scale=status_scale,
                            legend=alt.Legend(title="Status", orient="bottom")),
            tooltip=[
                alt.Tooltip("Name:N"),
                alt.Tooltip("Score:Q", format=".0f"),
                alt.Tooltip("Status:N"),
            ],
        )
        .properties(height=420, title="Data Health Score per Contact")
    )

    left, right = st.columns([3, 2], gap="large")

    with left:
        st.altair_chart(health_chart, use_container_width=True)

    with right:
        verified  = sum(1 for c in contacts if c.data_health_score >= 80)
        partial   = sum(1 for c in contacts if 50 <= c.data_health_score < 80)
        attention = sum(1 for c in contacts if c.data_health_score < 50)

        st.markdown('<div class="micro-header">Status Breakdown</div>',
                    unsafe_allow_html=True)
        bd_df = pd.DataFrame({
            "Status": ["Verified", "Partial", "Needs Attention"],
            "Count":  [verified, partial, attention],
        })
        st.altair_chart(
            _altair_cfg(
                alt.Chart(bd_df)
                .mark_bar(cornerRadiusEnd=3, height=18)
                .encode(
                    x=alt.X("Count:Q", axis=alt.Axis(tickMinStep=1)),
                    y=alt.Y("Status:N", sort=None,
                            axis=alt.Axis(labelColor=_T2)),
                    color=alt.Color("Status:N", scale=status_scale, legend=None),
                    tooltip=["Status:N", "Count:Q"],
                )
                .properties(height=120)
            ),
            use_container_width=True,
        )

        st.markdown('<div class="micro-header" style="margin-top:16px">GDPR Tracking Window</div>',
                    unsafe_allow_html=True)
        gdpr_df = pd.DataFrame({
            "Category": ["Trackable (≤ 24 mo)", "Stale (> 24 mo)"],
            "Count":    [summary["trackable"], summary["stale_gdpr"]],
        })
        st.altair_chart(
            _altair_cfg(
                alt.Chart(gdpr_df)
                .mark_bar(cornerRadiusEnd=3, height=18)
                .encode(
                    x=alt.X("Count:Q", axis=alt.Axis(tickMinStep=1)),
                    y=alt.Y("Category:N", sort=None,
                            axis=alt.Axis(labelColor=_T2)),
                    color=alt.condition(
                        alt.datum.Category == "Trackable (≤ 24 mo)",
                        alt.value(_GREEN), alt.value(_RED),
                    ),
                    tooltip=["Category:N", "Count:Q"],
                )
                .properties(height=100)
            ),
            use_container_width=True,
        )

    st.divider()
    st.markdown('<div class="micro-header">All Contacts</div>', unsafe_allow_html=True)

    df = pd.DataFrame([
        {
            "Name":             c.full_name,
            "Title":            c.title or "—",
            "Company":          c.company,
            "Health":           c.data_health_score,
            "Status":           _health_status(c.data_health_score),
            "GDPR":             "✓" if c.tracking_eligible else "✗",
            "Email":            "✓" if c.email_verified else "✗",
            "Title Verified":   "✓" if c.title_verified else "✗",
            "Last Interaction": c.last_interaction_date.strftime("%Y-%m-%d"),
        }
        for c in contacts
    ])

    def _style_health(val):
        if not isinstance(val, (int, float)):
            return ""
        if val >= 80: return f"background:{_G_BG};color:{_GREEN};font-weight:700"
        if val >= 50: return f"background:{_Y_BG};color:{_YELLOW};font-weight:700"
        return f"background:{_R_BG};color:{_RED};font-weight:700"

    styled = df.style.map(_style_health, subset=["Health"])
    st.dataframe(styled, use_container_width=True, height=420)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Reset CRM to original data"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Deep Clean
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧹 Deep Clean":
    last_run     = st.session_state.get("last_run_deep_clean")
    last_run_tag = (f'<span class="hero-tag">Last run {last_run}</span>' if last_run else "")
    st.markdown(
        f'<div class="page-hero">'
        f'<h1>🧹 Utopian Deep Clean {last_run_tag}</h1>'
        f'<p>One-time foundational pass — merge duplicates, fix formatting, '
        f'verify titles via LinkedIn, validate emails via ZoomInfo, '
        f'and fire job-change alerts for eligible contacts.</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    from tools.crm_tools import CRMTools as _CT
    crm          = get_crm()
    contacts_all = crm.get_all()
    dupes        = _CT(crm).find_duplicates().get("duplicate_groups_found", 0)
    bad_fmt      = sum(1 for c in contacts_all
                       if not c.email_verified or not c.title or not c.company_verified)
    with_li      = sum(1 for c in contacts_all if c.linkedin_url)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Contacts",      len(contacts_all))
    m2.metric("Duplicate Groups",    dupes,
              delta="will be merged" if dupes else None, delta_color="off")
    m3.metric("Formatting Issues",   bad_fmt,
              delta="will be fixed"  if bad_fmt else None, delta_color="off")
    m4.metric("LinkedIn Profiles",   with_li)

    st.divider()

    label = "▶️ Run Again" if last_run else "▶️ Run Deep Clean"
    if st.button(label, type="primary", use_container_width=True):
        run_agent_ui("deep_clean")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Career Tracker
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📡 Career Tracker":
    last_run     = st.session_state.get("last_run_monitor")
    last_run_tag = (f'<span class="hero-tag">Last run {last_run}</span>' if last_run else "")
    st.markdown(
        f'<div class="page-hero">'
        f'<h1>📡 Career Tracker {last_run_tag}</h1>'
        f'<p>Always-on scan of every GDPR-eligible contact — detects job changes and '
        f'sends Proactive Change Alerts to the sales team. '
        f'No automated outreach to contacts.</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    crm          = get_crm()
    summary      = crm.summary()
    contacts_all = crm.get_all()
    trackable    = [c for c in contacts_all if c.tracking_eligible]
    alert_elig   = [c for c in trackable    if c.alert_eligible]
    with_li      = sum(1 for c in trackable if c.linkedin_url)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Trackable Contacts", len(trackable),
              help="Last interaction ≤ 24 months")
    m2.metric("Alert-Eligible",     len(alert_elig),
              help="Last interaction ≤ 12 months — alerts fire on job change")
    m3.metric("LinkedIn Profiles",  with_li)
    m4.metric("Stale / Excluded",   summary["stale_gdpr"],
              delta="outside GDPR window", delta_color="off")

    st.divider()

    label = "▶️ Run Again" if last_run else "▶️ Run Career Tracker"
    if st.button(label, type="primary", use_container_width=True):
        run_agent_ui("monitor")
