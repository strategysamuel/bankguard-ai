"""
BANKGUARD AI - Risk, Fraud & Regulatory Intelligence Command Center
Streamlit-in-Snowflake Dashboard (M5)

All data is SYNTHETIC DEMONSTRATION DATA.
This application does not constitute legal, regulatory, or compliance advice.
"""

import streamlit as st
import pandas as pd
import json
import altair as alt

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="BANKGUARD AI", layout="wide", initial_sidebar_state="expanded")

# ---------------------------------------------------------------------------
# Theme — professional banking-grade blue
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ── Sidebar: deep navy ── */
section[data-testid="stSidebar"] {
    background-color: #0A1628 !important;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stRadio label span {
    color: #CBD5E1 !important;
}
section[data-testid="stSidebar"] h1 {
    color: #FFFFFF !important;
    letter-spacing: 0.08em;
    font-size: 1.6rem !important;
    border-bottom: 2px solid #1A73E8;
    padding-bottom: 0.35rem;
}
section[data-testid="stSidebar"] .stRadio > label {
    color: #7B8FA3 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label {
    padding: 0.45rem 0.7rem;
    border-radius: 6px;
    margin-bottom: 2px;
    transition: background-color 0.15s;
}
section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:hover {
    background-color: rgba(26,115,232,0.15);
}
section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label[data-checked="true"],
section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:has(input:checked) {
    background-color: #1A73E8 !important;
}
section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label[data-checked="true"] span,
section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:has(input:checked) span {
    color: #FFFFFF !important;
    font-weight: 600;
}
section[data-testid="stSidebar"] hr {
    border-color: #1C2E45 !important;
}
/* Sidebar caption */
section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {
    color: #5A7A9A !important;
}
/* Sidebar warning — keep highly visible */
section[data-testid="stSidebar"] .stAlert {
    background-color: #FF8F00 !important;
    color: #1A1A1A !important;
    border: none !important;
    border-radius: 6px;
    font-weight: 600;
}
section[data-testid="stSidebar"] .stAlert p,
section[data-testid="stSidebar"] .stAlert span {
    color: #1A1A1A !important;
}

/* ── Main content headers ── */
.main h1, .main [data-testid="stHeader"] { color: #0D2137 !important; }
.main h2 { color: #1B4F72 !important; }
.main h3 { color: #2471A3 !important; }

/* ── KPI metric cards ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #EBF5FB 0%, #D4E6F1 100%);
    border: 1px solid #AED6F1;
    border-radius: 8px;
    padding: 14px 16px 10px 16px;
}
[data-testid="stMetric"] label {
    color: #1B4F72 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #0D2137 !important;
    font-weight: 700;
}

/* ── Selectboxes — blue accent border ── */
[data-testid="stSelectbox"] label {
    color: #1B4F72 !important;
    font-weight: 600;
}
div[data-baseweb="select"] > div {
    border-color: #2471A3 !important;
    border-radius: 6px;
}
div[data-baseweb="select"] > div:focus-within {
    border-color: #1A73E8 !important;
    box-shadow: 0 0 0 1px #1A73E8;
}

/* ── Tabs — blue active indicator ── */
.stTabs [data-baseweb="tab-list"] button {
    color: #5A7A9A;
    font-weight: 500;
}
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    color: #1A73E8 !important;
    border-bottom-color: #1A73E8 !important;
    font-weight: 700;
}

/* ── Expanders ── */
[data-testid="stExpander"] summary span {
    color: #1B4F72 !important;
    font-weight: 600;
}

/* ── Text input — blue focus ── */
[data-testid="stTextInput"] label { color: #1B4F72 !important; font-weight: 600; }
[data-testid="stTextInput"] input:focus { border-color: #1A73E8 !important; box-shadow: 0 0 0 1px #1A73E8; }

/* ── Dividers ── */
.main hr { border-color: #D4E6F1 !important; }

/* ── Info/success/warning/error alerts in main area ── */
.main .stAlert[data-baseweb="notification"] { border-radius: 6px; }

/* ── Dataframe container ── */
[data-testid="stDataFrame"] { border: 1px solid #D4E6F1; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Snowflake connection (SiS native or local fallback)
# ---------------------------------------------------------------------------
@st.cache_resource
def _get_session():
    from snowflake.snowpark.context import get_active_session
    return get_active_session()

session = _get_session()

def run_query(sql: str) -> pd.DataFrame:
    return session.sql(sql).to_pandas()


# ---------------------------------------------------------------------------
# Cortex AI helpers — isolated, error-tolerant
# ---------------------------------------------------------------------------
def _call_agent(question: str, history: list = None) -> str:
    """Call BANKGUARD Agent via SiS-native _snowflake API. Returns text or error."""
    try:
        import _snowflake
        messages = []
        if history:
            for h in history:
                messages.append({"role": h["role"], "content": [{"type": "text", "text": h["text"]}]})
        messages.append({"role": "user", "content": [{"type": "text", "text": question}]})
        payload = json.dumps({"messages": messages, "stream": False})
        resp = _snowflake.send_snow_api_request(
            "POST",
            "/api/v2/databases/BANKGUARD_DB/schemas/BANKGUARD_CORE/agents/BANKGUARD_AGENT:run",
            {}, {}, payload, {}, 60000,
        )
        status = resp.get("status", 0) if isinstance(resp, dict) else 0
        body = resp.get("content", "{}") if isinstance(resp, dict) else str(resp)
        if status < 200 or status >= 300:
            return f"Agent returned status {status}."
        data = json.loads(body) if isinstance(body, str) else body
        for msg in data.get("messages", []):
            if msg.get("role") == "assistant":
                parts = msg.get("content", [])
                texts = [p.get("text", "") for p in parts if p.get("type") == "text"]
                if texts:
                    return "\n\n".join(texts)
        return data.get("text", str(data))
    except ImportError:
        return "AI investigation requires Streamlit-in-Snowflake runtime."
    except Exception as e:
        return f"AI investigation service is temporarily unavailable.\n\nExisting risk and evidence data remain available.\n\nError: {type(e).__name__}"


AI_DISCLAIMER = (
    "**SYNTHETIC DATA** — This AI analysis is based on synthetic demonstration data. "
    "All findings require analyst review. The AI does not make enforcement decisions."
)

_AI_SECTIONS = [
    "EXECUTIVE SUMMARY", "RISK ASSESSMENT", "OBSERVED EVIDENCE",
    "RISK SIGNALS", "APPLICABLE POLICIES", "POLICY REFERENCES",
    "AI ANALYSIS", "INVESTIGATION CONSIDERATIONS",
    "RECOMMENDED NEXT STEPS", "RECOMMENDATIONS",
    "LIMITATIONS", "DISCLAIMERS",
]
_SECTION_ICONS = {
    "EXECUTIVE SUMMARY": "📋", "RISK ASSESSMENT": "⚠️",
    "OBSERVED EVIDENCE": "🔍", "RISK SIGNALS": "🚩",
    "APPLICABLE POLICIES": "📜", "POLICY REFERENCES": "📜",
    "AI ANALYSIS": "🤖", "INVESTIGATION CONSIDERATIONS": "💡",
    "RECOMMENDED NEXT STEPS": "➡️", "RECOMMENDATIONS": "➡️",
    "LIMITATIONS": "ℹ️", "DISCLAIMERS": "ℹ️",
}
_SECTION_LABELS = {
    "OBSERVED EVIDENCE": "FACT / OBSERVED EVIDENCE",
    "RISK SIGNALS": "FACT / RISK SIGNALS",
    "APPLICABLE POLICIES": "POLICY / REGULATION",
    "POLICY REFERENCES": "POLICY / REGULATION",
    "AI ANALYSIS": "AI ANALYSIS (requires review)",
    "INVESTIGATION CONSIDERATIONS": "AI ANALYSIS (requires review)",
    "RECOMMENDED NEXT STEPS": "INVESTIGATION RECOMMENDATION",
    "RECOMMENDATIONS": "INVESTIGATION RECOMMENDATION",
}


def _render_ai_response(text: str):
    """Render agent output with structured section parsing and fact/analysis separation."""
    import re
    sections = []
    pattern = re.compile(
        r"(?:^|\n)#+\s*\d*\.?\s*(" + "|".join(re.escape(s) for s in _AI_SECTIONS) + r")\b[:\s]*",
        re.IGNORECASE,
    )
    matches = list(pattern.finditer(text))
    if len(matches) >= 2:
        for i, m in enumerate(matches):
            name = m.group(1).upper().strip()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            if body:
                sections.append((name, body))
    if sections:
        for name, body in sections:
            icon = _SECTION_ICONS.get(name, "")
            label = _SECTION_LABELS.get(name, name.title())
            st.markdown(f"**{icon} {label}**")
            st.markdown(body)
            st.markdown("")
    else:
        st.markdown(text)
    st.caption("AI-generated analysis — requires analyst review before any action")


def _log_ai_call(customer_id: str, case_id: str, query_text: str,
                 response_text: str, status: str = "COMPLETED"):
    """Write audit record to AI_DECISION_LOG. Failures are silent."""
    try:
        import re
        citations = re.findall(r"PC-[A-Z]+-\d+", response_text or "")
        citations_json = json.dumps(list(set(citations))) if citations else "[]"
        safe_q = query_text.replace("'", "''")[:4000]
        safe_r = (response_text or "")[:16000].replace("'", "''")
        session.sql(f"""
            INSERT INTO {DB}.BANKGUARD_AUDIT.AI_DECISION_LOG
                (CUSTOMER_ID, CASE_ID, QUERY_TEXT, RESPONSE_TEXT,
                 POLICY_CITATIONS, RESPONSE_STATUS)
            VALUES ('{customer_id}', {("'" + case_id + "'") if case_id else 'NULL'},
                    '{safe_q}', '{safe_r}',
                    PARSE_JSON('{citations_json}'), '{status}')
        """).collect()
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DB = "BANKGUARD_DB"
RISK_COLORS = {"LOW": "#4CAF50", "MEDIUM": "#FF9800", "HIGH": "#F44336", "CRITICAL": "#9C27B0"}
SEVERITY_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
PAGES = ["Risk Overview", "Customer Investigation", "Policy Lookup", "Case Management", "About"]

# ---------------------------------------------------------------------------
# Session state — cross-page navigation
# ---------------------------------------------------------------------------
for _key, _default in [
    ("nav_page", "Risk Overview"),
    ("nav_customer", None),
    ("nav_case", None),
    ("nav_policy", None),
    ("nav_risk_class", None),
    ("nav_signal_type", None),
    ("nav_from", None),
    ("nav_search", None),
]:
    if _key not in st.session_state:
        st.session_state[_key] = _default


def navigate_to(page, customer=None, case=None, policy=None,
                risk_class=None, signal_type=None, search=None):
    st.session_state["nav_from"] = st.session_state["nav_page"]
    st.session_state["nav_page"] = page
    st.session_state["nav_customer"] = customer
    st.session_state["nav_case"] = case
    st.session_state["nav_policy"] = policy
    st.session_state["nav_risk_class"] = risk_class
    st.session_state["nav_signal_type"] = signal_type
    st.session_state["nav_search"] = search
    st.session_state["_nav_pending"] = True
    st.rerun()


def _consume(key):
    val = st.session_state.get(key)
    if val is not None:
        st.session_state[key] = None
    return val

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.title("BANKGUARD AI")
st.sidebar.caption("Risk, Fraud & Regulatory Intelligence Copilot")
st.sidebar.divider()

# Resolve programmatic navigation BEFORE the radio widget renders.
# When navigate_to() is called, it sets _nav_pending=True and nav_page to
# the target. We must write that target into the radio widget's own key
# so that Streamlit's internal widget state agrees with nav_page.
if st.session_state.get("_nav_pending"):
    st.session_state["_nav_radio"] = st.session_state["nav_page"]
    st.session_state["_nav_pending"] = False

page = st.sidebar.radio(
    "Navigation",
    PAGES,
    index=PAGES.index(st.session_state["nav_page"]),
    key="_nav_radio",
)
st.session_state["nav_page"] = page

st.sidebar.divider()
st.sidebar.warning("SYNTHETIC DEMONSTRATION DATA ONLY. Not real banking data.")
st.sidebar.caption("Rule Version: M2-RISK-V1.0")


# ===================================================================
# PAGE: Risk Overview
# ===================================================================
def page_risk_overview():
    st.header("Risk Command Center")
    st.caption("Deterministic risk engine output - all data is synthetic")

    # KPIs row
    kpi = run_query(f"""
        SELECT
            (SELECT COUNT(*) FROM {DB}.BANKGUARD_RAW.CUSTOMERS) AS TOTAL_CUSTOMERS,
            (SELECT COUNT(*) FROM {DB}.BANKGUARD_RISK.CUSTOMER_RISK_SCORE) AS SCORED_CUSTOMERS,
            (SELECT COUNT(*) FROM {DB}.BANKGUARD_RISK.RISK_SIGNAL_EVIDENCE) AS TOTAL_SIGNALS,
            (SELECT COUNT(*) FROM {DB}.BANKGUARD_RISK.CUSTOMER_RISK_SCORE WHERE RISK_CLASS='CRITICAL') AS CRITICAL_CUSTOMERS,
            (SELECT COUNT(*) FROM {DB}.BANKGUARD_RAW.INVESTIGATION_CASES WHERE CASE_STATUS IN ('OPEN','IN_PROGRESS','ESCALATED')) AS OPEN_CASES,
            (SELECT COUNT(*) FROM {DB}.BANKGUARD_RAW.TRANSACTIONS) AS TOTAL_TRANSACTIONS
    """)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Customers", f"{kpi['TOTAL_CUSTOMERS'].iloc[0]:,}")
    c2.metric("Scored Customers", f"{kpi['SCORED_CUSTOMERS'].iloc[0]:,}")
    c3.metric("Risk Signals", f"{kpi['TOTAL_SIGNALS'].iloc[0]:,}")
    c4.metric("CRITICAL Customers", kpi['CRITICAL_CUSTOMERS'].iloc[0])
    c5.metric("Open Cases", kpi['OPEN_CASES'].iloc[0])
    c6.metric("Transactions", f"{kpi['TOTAL_TRANSACTIONS'].iloc[0]:,}")

    st.divider()
    col_left, col_right = st.columns(2)

    # ------ Risk Classification Distribution + drill-down ------
    with col_left:
        st.subheader("Risk Classification Distribution")
        dist = run_query(f"""
            SELECT RISK_CLASS, COUNT(*) AS CUSTOMER_COUNT
            FROM {DB}.BANKGUARD_RISK.CUSTOMER_RISK_SCORE
            GROUP BY RISK_CLASS
        """)
        chart_rc = None
        if not dist.empty:
            dist["RISK_CLASS"] = pd.Categorical(dist["RISK_CLASS"], categories=SEVERITY_ORDER, ordered=True)
            dist = dist.sort_values("RISK_CLASS")

            rc_sel = alt.selection_point(name="rc_sel", fields=["RISK_CLASS"])
            chart = alt.Chart(dist).mark_bar(cursor="pointer").encode(
                x=alt.X("RISK_CLASS:N", sort=SEVERITY_ORDER, title="Risk Class"),
                y=alt.Y("CUSTOMER_COUNT:Q", title="Customers"),
                color=alt.Color("RISK_CLASS:N", scale=alt.Scale(
                    domain=SEVERITY_ORDER,
                    range=[RISK_COLORS[k] for k in SEVERITY_ORDER]
                ), legend=None),
                opacity=alt.condition(rc_sel, alt.value(1.0), alt.value(0.35)),
            ).properties(height=300).add_params(rc_sel)
            rc_event = st.altair_chart(chart, use_container_width=True,
                                       on_select="rerun", key="ov_rc_chart")

            # Extract chart click
            try:
                pts = rc_event.get("selection", {}).get("rc_sel", [])
                if pts and isinstance(pts, list) and len(pts) > 0:
                    chart_rc = pts[0].get("RISK_CLASS")
            except Exception:
                pass

        pre_risk = _consume("nav_risk_class")
        rc_options = ["All"] + SEVERITY_ORDER
        effective_rc = chart_rc or pre_risk
        rc_idx = rc_options.index(effective_rc) if effective_rc in rc_options else 0
        selected_rc = st.selectbox("Filter by Risk Class", rc_options, index=rc_idx, key="ov_rc")

        if selected_rc != "All":
            rc_custs = run_query(f"""
                SELECT rs.CUSTOMER_ID, rs.RISK_SCORE, rs.RISK_CLASS, rs.SIGNAL_COUNT,
                       rs.TOP_SIGNAL, rs.SIGNAL_SUMMARY
                FROM {DB}.BANKGUARD_RISK.CUSTOMER_RISK_SCORE rs
                WHERE rs.RISK_CLASS = '{selected_rc}'
                ORDER BY rs.RISK_SCORE DESC, rs.SIGNAL_COUNT DESC, rs.CUSTOMER_ID
            """)
            if not rc_custs.empty:
                st.dataframe(rc_custs, use_container_width=True, hide_index=True)
                rc_cust_opts = rc_custs["CUSTOMER_ID"].tolist()
                sel_cust = st.selectbox("Select customer to investigate", rc_cust_opts, key="ov_rc_cust")
                if st.button("Open Investigation", key="ov_rc_go", type="primary"):
                    navigate_to("Customer Investigation", customer=sel_cust)
            else:
                st.info(f"No {selected_rc} customers found.")

    # ------ Signal Type Distribution + drill-down ------
    with col_right:
        st.subheader("Signal Type Distribution")
        sig_dist = run_query(f"""
            SELECT SIGNAL_TYPE, COUNT(*) AS SIGNAL_COUNT
            FROM {DB}.BANKGUARD_RISK.RISK_SIGNAL_EVIDENCE
            WHERE SIGNAL_TYPE != 'MULTI_SIGNAL'
            GROUP BY SIGNAL_TYPE ORDER BY SIGNAL_COUNT DESC
        """)
        chart_sig = None
        if not sig_dist.empty:
            sig_sel = alt.selection_point(name="sig_sel", fields=["SIGNAL_TYPE"])
            chart2 = alt.Chart(sig_dist).mark_bar(color="#1E88E5", cursor="pointer").encode(
                x=alt.X("SIGNAL_COUNT:Q", title="Detections"),
                y=alt.Y("SIGNAL_TYPE:N", sort="-x", title="Signal Type"),
                opacity=alt.condition(sig_sel, alt.value(1.0), alt.value(0.35)),
            ).properties(height=300).add_params(sig_sel)
            sig_event = st.altair_chart(chart2, use_container_width=True,
                                        on_select="rerun", key="ov_sig_chart")

            try:
                pts = sig_event.get("selection", {}).get("sig_sel", [])
                if pts and isinstance(pts, list) and len(pts) > 0:
                    chart_sig = pts[0].get("SIGNAL_TYPE")
            except Exception:
                pass

        pre_sig = _consume("nav_signal_type")
        sig_options = ["All"] + sig_dist["SIGNAL_TYPE"].tolist() if not sig_dist.empty else ["All"]
        effective_sig = chart_sig or pre_sig
        sig_idx = sig_options.index(effective_sig) if effective_sig in sig_options else 0
        selected_sig = st.selectbox("Filter by Signal Type", sig_options, index=sig_idx, key="ov_sig")

        if selected_sig != "All":
            sig_custs = run_query(f"""
                SELECT DISTINCT rse.CUSTOMER_ID,
                       rs.RISK_SCORE, rs.RISK_CLASS, rs.SIGNAL_COUNT, rs.TOP_SIGNAL
                FROM {DB}.BANKGUARD_RISK.RISK_SIGNAL_EVIDENCE rse
                JOIN {DB}.BANKGUARD_RISK.CUSTOMER_RISK_SCORE rs ON rse.CUSTOMER_ID = rs.CUSTOMER_ID
                WHERE rse.SIGNAL_TYPE = '{selected_sig}'
                ORDER BY rs.RISK_SCORE DESC, rs.SIGNAL_COUNT DESC, rse.CUSTOMER_ID
            """)
            if not sig_custs.empty:
                st.dataframe(sig_custs, use_container_width=True, hide_index=True)
                sig_cust_opts = sig_custs["CUSTOMER_ID"].tolist()
                sel_cust2 = st.selectbox("Select customer to investigate", sig_cust_opts, key="ov_sig_cust")
                if st.button("Open Investigation", key="ov_sig_go", type="primary"):
                    navigate_to("Customer Investigation", customer=sel_cust2)
            else:
                st.info(f"No customers found for {selected_sig}.")

    # ------ High-Risk Customers table ------
    st.divider()
    st.subheader("High-Risk Customers (HIGH + CRITICAL)")
    high_risk = run_query(f"""
        SELECT rs.CUSTOMER_ID, rs.RISK_SCORE, rs.RISK_CLASS, rs.SIGNAL_COUNT,
               rs.TOP_SIGNAL, rs.SIGNAL_SUMMARY,
               c.CUSTOMER_SEGMENT, c.CITY
        FROM {DB}.BANKGUARD_RISK.CUSTOMER_RISK_SCORE rs
        JOIN {DB}.BANKGUARD_CORE.V_CUSTOMER_360 c ON rs.CUSTOMER_ID = c.CUSTOMER_ID
        WHERE rs.RISK_CLASS IN ('HIGH','CRITICAL')
        ORDER BY rs.RISK_SCORE DESC
        LIMIT 20
    """)
    if not high_risk.empty:
        st.dataframe(
            high_risk,
            column_config={
                "RISK_SCORE": st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=100, format="%d"),
            },
            use_container_width=True,
            hide_index=True,
        )
        hr_opts = high_risk["CUSTOMER_ID"].tolist()
        sel_hr = st.selectbox("Select high-risk customer to investigate", hr_opts, key="ov_hr_cust")
        if st.button("Open Investigation", key="ov_hr_go", type="primary"):
            navigate_to("Customer Investigation", customer=sel_hr)
    else:
        st.info("No HIGH or CRITICAL risk customers found.")


# ===================================================================
# PAGE: Customer Investigation
# ===================================================================
def page_customer_investigation():
    st.header("Customer Investigation")
    st.caption("Evidence-backed risk analysis - requires analyst review for all findings")

    # Back button if arrived via navigation
    nav_from = _consume("nav_from")
    if nav_from and nav_from != "Customer Investigation":
        if st.button(f"← Back to {nav_from}", key="ci_back"):
            navigate_to(nav_from)

    # Load all scored customers for selectbox (highest risk first)
    risky = run_query(f"""
        SELECT CUSTOMER_ID, RISK_SCORE, RISK_CLASS, SIGNAL_COUNT
        FROM {DB}.BANKGUARD_RISK.CUSTOMER_RISK_SCORE
        ORDER BY
            CASE RISK_CLASS WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2
                 WHEN 'MEDIUM' THEN 3 ELSE 4 END,
            RISK_SCORE DESC, CUSTOMER_ID
    """)

    if risky.empty:
        st.info("No scored customers found.")
        return

    options = [
        f"{row['CUSTOMER_ID']} — {row['RISK_CLASS']} — Risk Score {row['RISK_SCORE']:.0f} — {int(row['SIGNAL_COUNT'])} Signals"
        for _, row in risky.iterrows()
    ]
    cust_ids = risky["CUSTOMER_ID"].tolist()

    # Pre-select from navigation or default to first (CUST-1042)
    pre_cust = _consume("nav_customer")
    default_idx = cust_ids.index(pre_cust) if pre_cust in cust_ids else 0

    selection = st.selectbox("Select Risky Customer", options, index=default_idx, key="ci_cust")
    customer_id = selection.split(" — ")[0]

    # Customer profile
    profile = run_query(f"""
        SELECT * FROM {DB}.BANKGUARD_CORE.V_CUSTOMER_360
        WHERE CUSTOMER_ID = '{customer_id}'
    """)
    if profile.empty:
        st.error(f"Customer {customer_id} not found.")
        return

    p = profile.iloc[0]
    st.subheader(f"Customer Profile: {customer_id}")
    pc1, pc2, pc3, pc4, pc5 = st.columns(5)
    pc1.metric("Segment", p.get("CUSTOMER_SEGMENT", "N/A"))
    pc2.metric("Risk Rating", p.get("CUSTOMER_RISK_RATING", "N/A"))
    pc3.metric("KYC Status", p.get("KYC_STATUS", "N/A"))
    pc4.metric("Accounts", int(p.get("ACCOUNT_COUNT", 0)))
    pc5.metric("City", p.get("CITY", "N/A"))

    # Risk score
    risk = run_query(f"""
        SELECT RISK_SCORE, RISK_CLASS, SIGNAL_COUNT, TOP_SIGNAL, SIGNAL_SUMMARY
        FROM {DB}.BANKGUARD_RISK.CUSTOMER_RISK_SCORE
        WHERE CUSTOMER_ID = '{customer_id}'
    """)
    if not risk.empty:
        r = risk.iloc[0]
        st.divider()
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("Composite Risk Score", f"{r['RISK_SCORE']:.0f} / 100")
        rc2.metric("Risk Classification", r["RISK_CLASS"])
        rc3.metric("Active Signals", int(r["SIGNAL_COUNT"]))
        st.info(f"**Signal Summary:** {r['SIGNAL_SUMMARY']}")
    else:
        st.success(f"No risk signals detected for {customer_id}.")

    # Risk signals with evidence
    signals = run_query(f"""
        SELECT SIGNAL_TYPE, SEVERITY, SIGNAL_SCORE, EVIDENCE_SUMMARY, OBSERVATION_START, OBSERVATION_END
        FROM {DB}.BANKGUARD_RISK.RISK_SIGNAL_EVIDENCE
        WHERE CUSTOMER_ID = '{customer_id}'
        ORDER BY SIGNAL_SCORE DESC
    """)
    if not signals.empty:
        st.divider()
        st.subheader("Risk Signal Evidence")
        for idx, sig in signals.iterrows():
            severity = sig["SEVERITY"]
            with st.expander(f"{sig['SIGNAL_TYPE']} - {severity} (Score: {sig['SIGNAL_SCORE']:.0f})", expanded=(severity == "CRITICAL")):
                st.markdown(f"**Severity:** :{severity.lower()}[{severity}]" if severity in ("HIGH", "CRITICAL") else f"**Severity:** {severity}")
                st.markdown(f"**Evidence:** {sig['EVIDENCE_SUMMARY']}")
                st.caption(f"Observation period: {sig['OBSERVATION_START']} to {sig['OBSERVATION_END']}")
                # Drill-down: view policies for this signal type
                if st.button(f"View Policies for {sig['SIGNAL_TYPE']}", key=f"ci_sig_pol_{idx}"):
                    navigate_to("Policy Lookup", customer=customer_id, search=sig["SIGNAL_TYPE"])

    # Policy chain
    policies = run_query(f"""
        SELECT SIGNAL_TYPE, POLICY_ID, POLICY_VERSION, SECTION_ID, SECTION_TITLE,
               RELEVANCE, EVIDENCE_REQUIREMENT, POLICY_STATUS
        FROM {DB}.BANKGUARD_REGULATORY.V_SIGNAL_POLICY_CHAIN
        WHERE CUSTOMER_ID = '{customer_id}'
        ORDER BY SIGNAL_TYPE, RELEVANCE
    """)
    if not policies.empty:
        st.divider()
        st.subheader("Applicable Policy Sections")
        st.caption("Policy citations for each detected risk signal")
        st.dataframe(
            policies[["SIGNAL_TYPE", "POLICY_ID", "POLICY_VERSION", "SECTION_TITLE", "RELEVANCE"]],
            use_container_width=True, hide_index=True,
        )
        # Drill to Policy Lookup
        unique_policies = policies["POLICY_ID"].unique().tolist()
        sel_pol = st.selectbox("Select policy to view details", unique_policies, key="ci_pol_select")
        if st.button("Open in Policy Lookup", key="ci_pol_go", type="primary"):
            navigate_to("Policy Lookup", policy=sel_pol, customer=customer_id)

    # Associated cases — selectbox + detail + transactions + nav
    cases = run_query(f"""
        SELECT ic.CASE_ID, ic.CUSTOMER_ID, ic.CASE_STATUS, ic.CASE_PRIORITY,
               ic.ANALYST, ic.OPEN_DATE,
               rs.RISK_SCORE, rs.RISK_CLASS, rs.SIGNAL_COUNT, rs.SIGNAL_SUMMARY
        FROM {DB}.BANKGUARD_RAW.INVESTIGATION_CASES ic
        LEFT JOIN {DB}.BANKGUARD_RISK.CUSTOMER_RISK_SCORE rs ON ic.CUSTOMER_ID = rs.CUSTOMER_ID
        WHERE ic.CUSTOMER_ID = '{customer_id}'
        ORDER BY rs.RISK_SCORE DESC NULLS LAST, ic.CASE_ID
    """)
    if not cases.empty:
        st.divider()
        st.subheader("Associated Investigation Cases")
        case_opts = [
            f"{r['CASE_ID']} — {r['CASE_STATUS']} — {r['CASE_PRIORITY']}"
            for _, r in cases.iterrows()
        ]
        sel_case_label = st.selectbox(
            "Select investigation case", case_opts,
            key=f"ci_case_sel_{customer_id}",
        )
        sel_case_id = sel_case_label.split(" — ")[0]
        sel_case_row = cases[cases["CASE_ID"] == sel_case_id].iloc[0]

        # Case detail
        st.markdown(f"#### Case Detail: {sel_case_id}")
        cd1, cd2, cd3, cd4 = st.columns(4)
        cd_score = sel_case_row["RISK_SCORE"]
        cd1.metric("Risk Score", f"{cd_score:.0f} / 100" if pd.notna(cd_score) else "N/A")
        cd2.metric("Classification", sel_case_row.get("RISK_CLASS") or "N/A")
        cd_signals = sel_case_row.get("SIGNAL_COUNT")
        cd3.metric("Active Signals", int(cd_signals) if pd.notna(cd_signals) else "N/A")
        cd4.metric("Priority", sel_case_row["CASE_PRIORITY"])
        st.info(f"**Assigned Analyst:** {sel_case_row['ANALYST']} | **Status:** {sel_case_row['CASE_STATUS']} | **Opened:** {sel_case_row['OPEN_DATE']}")
        cd_summary = sel_case_row.get("SIGNAL_SUMMARY")
        if pd.notna(cd_summary):
            st.markdown(f"**Signal Summary:** {cd_summary}")

        # Case transactions
        st.markdown("**Case Transactions**")
        case_txns = run_query(f"""
            SELECT TRANSACTION_ID, TRANSACTION_DATE, TRANSACTION_TYPE, AMOUNT, CHANNEL,
                   TRANSACTION_COUNTRY, BENEFICIARY_ID, TRANSACTION_STATUS
            FROM {DB}.BANKGUARD_CORE.V_TRANSACTION_ENRICHED
            WHERE CUSTOMER_ID = '{customer_id}'
            ORDER BY TRANSACTION_DATE DESC
            LIMIT 50
        """)
        if not case_txns.empty:
            st.dataframe(
                case_txns,
                column_config={"AMOUNT": st.column_config.NumberColumn("Amount (INR)", format="%.2f")},
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("No transactions found for this customer.")

        # Navigate to Case Management
        if st.button("Open Case Management", key=f"ci_open_cm_{sel_case_id}", type="primary"):
            navigate_to("Case Management", case=sel_case_id, customer=customer_id)

    # ----- AI Investigation Copilot -----
    st.divider()
    st.subheader("AI Investigation Copilot")
    st.caption(AI_DISCLAIMER)

    # Reset conversation when customer changes
    if st.session_state.get("ai_chat_cust") != customer_id:
        st.session_state["ai_chat_cust"] = customer_id
        st.session_state["ai_chat_history"] = []

    chat_history = st.session_state.get("ai_chat_history", [])

    risk_row = risk.iloc[0] if not risk.empty else None
    score_label = f"{risk_row['RISK_SCORE']:.0f}" if risk_row is not None else "N/A"
    class_label = risk_row["RISK_CLASS"] if risk_row is not None else "N/A"
    st.markdown(f"**{customer_id}** | {class_label} | Risk Score {score_label}")

    btn_col1, btn_col2, btn_col3 = st.columns(3)
    if btn_col1.button("Generate Investigation Summary", key="ci_ai_summary", type="primary"):
        prompt = (
            f"Provide a structured investigation summary for customer {customer_id}. "
            f"Use these exact section headers: "
            f"EXECUTIVE SUMMARY, OBSERVED EVIDENCE, APPLICABLE POLICIES, "
            f"AI ANALYSIS, RECOMMENDED NEXT STEPS. "
            f"Under OBSERVED EVIDENCE list only facts from risk signals and transactions. "
            f"Under APPLICABLE POLICIES cite policy IDs and sections. "
            f"Under AI ANALYSIS clearly state this is AI inference requiring review. "
            f"Do not declare fraud."
        )
        with st.spinner("AI investigating..."):
            resp = _call_agent(prompt, history=chat_history)
        chat_history.append({"role": "user", "text": prompt})
        chat_history.append({"role": "assistant", "text": resp})
        st.session_state["ai_chat_history"] = chat_history
        _log_ai_call(customer_id, None, prompt, resp)
        st.rerun()

    ai_question = st.text_input(
        "Ask an investigation question",
        placeholder=f"e.g. What policies apply to the signals for {customer_id}?",
        key="ci_ai_question",
    )
    if btn_col2.button("Ask AI", key="ci_ai_ask") and ai_question:
        full_q = f"Regarding customer {customer_id}: {ai_question}"
        with st.spinner("AI analyzing..."):
            resp = _call_agent(full_q, history=chat_history)
        chat_history.append({"role": "user", "text": full_q})
        chat_history.append({"role": "assistant", "text": resp})
        st.session_state["ai_chat_history"] = chat_history
        _log_ai_call(customer_id, None, full_q, resp)
        st.rerun()

    if chat_history and btn_col3.button("Clear Conversation", key="ci_ai_clear"):
        st.session_state["ai_chat_history"] = []
        st.rerun()

    # Display conversation
    for i in range(0, len(chat_history), 2):
        if i + 1 < len(chat_history):
            user_msg = chat_history[i]["text"]
            ai_msg = chat_history[i + 1]["text"]
            with st.expander(f"Q: {user_msg[:80]}{'...' if len(user_msg) > 80 else ''}", expanded=(i >= len(chat_history) - 2)):
                _render_ai_response(ai_msg)


# ===================================================================
# PAGE: Policy Lookup
# ===================================================================
def page_policy_lookup():
    st.header("Regulatory Policy Lookup")
    st.caption("SYNTHETIC DEMONSTRATION POLICIES - not actual legal or regulatory advice")

    # Back button if arrived via navigation
    nav_from = _consume("nav_from")
    nav_cust_ctx = _consume("nav_customer")
    if nav_from and nav_from != "Policy Lookup":
        if st.button(f"← Back to {nav_from}", key="pl_back"):
            navigate_to(nav_from, customer=nav_cust_ctx)

    query = st.text_input("Search policies", value=_consume("nav_search") or "", placeholder="e.g. transaction structuring threshold")

    if query:
        results = run_query(f"""
            SELECT PARSE_JSON(
                SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                    '{DB}.BANKGUARD_REGULATORY.POLICY_SEARCH_SERVICE',
                    '{{"query": "{query.replace("'", "''")}",
                      "columns": ["DOCUMENT_ID","TITLE","CONTENT","POLICY_ID","POLICY_VERSION","RISK_TOPIC","POLICY_DOMAIN"],
                      "limit": 5}}'
                )
            )['results'] AS results
        """)
        if not results.empty and results.iloc[0]["RESULTS"]:
            items = json.loads(results.iloc[0]["RESULTS"])
            for i, item in enumerate(items):
                with st.expander(f"{item.get('TITLE', 'Untitled')} [{item.get('POLICY_ID', '')} v{item.get('POLICY_VERSION', '')}]", expanded=(i == 0)):
                    st.markdown(f"**Domain:** {item.get('POLICY_DOMAIN', 'N/A')} | **Topic:** {item.get('RISK_TOPIC', 'N/A')}")
                    st.markdown(item.get("CONTENT", ""))
                    st.caption(f"Citation: [{item.get('POLICY_ID', '')} v{item.get('POLICY_VERSION', '')}, {item.get('TITLE', '')}]")
        else:
            st.info("No matching policy sections found.")

    st.divider()
    st.subheader("Active Policies")
    active = run_query(f"""
        SELECT POLICY_ID, POLICY_VERSION, POLICY_TITLE, POLICY_DOMAIN, EFFECTIVE_DATE,
               OWNER_FUNCTION, REVIEW_FREQUENCY
        FROM {DB}.BANKGUARD_REGULATORY.POLICIES
        WHERE STATUS = 'ACTIVE'
        ORDER BY POLICY_ID
    """)
    if active.empty:
        return

    st.dataframe(active, use_container_width=True, hide_index=True)

    # --- Policy detail drill-down ---
    pre_policy = _consume("nav_policy")
    pol_ids = active["POLICY_ID"].tolist()
    pol_labels = [f"{r['POLICY_ID']} — {r['POLICY_TITLE']}" for _, r in active.iterrows()]
    pol_default = pol_ids.index(pre_policy) if pre_policy in pol_ids else 0

    selected_pol_label = st.selectbox("Select Policy for Details", pol_labels, index=pol_default, key="pl_pol")
    selected_pol_id = selected_pol_label.split(" — ")[0]

    # Policy detail
    pol_row = active[active["POLICY_ID"] == selected_pol_id].iloc[0]
    st.divider()
    st.subheader(f"Policy Detail: {selected_pol_id}")
    pd1, pd2, pd3 = st.columns(3)
    pd1.metric("Policy ID", pol_row["POLICY_ID"])
    pd2.metric("Version", str(pol_row["POLICY_VERSION"]))
    pd3.metric("Domain", pol_row["POLICY_DOMAIN"])
    pe1, pe2, pe3 = st.columns(3)
    pe1.metric("Effective Date", str(pol_row["EFFECTIVE_DATE"]).strip('"'))
    pe2.metric("Owner", pol_row["OWNER_FUNCTION"])
    pe3.metric("Review Frequency", pol_row["REVIEW_FREQUENCY"])

    # Sections and signal types
    chain = run_query(f"""
        SELECT DISTINCT SECTION_ID, SECTION_TITLE, SIGNAL_TYPE, RELEVANCE, EVIDENCE_REQUIREMENT
        FROM {DB}.BANKGUARD_REGULATORY.V_SIGNAL_POLICY_CHAIN
        WHERE POLICY_ID = '{selected_pol_id}'
        ORDER BY SECTION_ID
    """)
    if not chain.empty:
        st.markdown("**Applicable Sections & Signal Types**")
        st.dataframe(
            chain[["SECTION_ID", "SECTION_TITLE", "SIGNAL_TYPE", "RELEVANCE"]],
            use_container_width=True, hide_index=True,
        )

    # Related customers
    rel_custs = run_query(f"""
        SELECT DISTINCT vpc.CUSTOMER_ID, rs.RISK_SCORE, rs.RISK_CLASS
        FROM {DB}.BANKGUARD_REGULATORY.V_SIGNAL_POLICY_CHAIN vpc
        JOIN {DB}.BANKGUARD_RISK.CUSTOMER_RISK_SCORE rs ON vpc.CUSTOMER_ID = rs.CUSTOMER_ID
        WHERE vpc.POLICY_ID = '{selected_pol_id}'
          AND rs.RISK_CLASS IN ('HIGH', 'CRITICAL')
        ORDER BY rs.RISK_SCORE DESC
    """)
    if not rel_custs.empty:
        st.divider()
        st.markdown("**High-Risk Customers Linked to This Policy**")
        st.dataframe(rel_custs, use_container_width=True, hide_index=True)
        rc_opts = [f"{r['CUSTOMER_ID']} — {r['RISK_CLASS']} — Score {r['RISK_SCORE']:.0f}"
                   for _, r in rel_custs.iterrows()]
        rc_sel = st.selectbox("Select customer", rc_opts, key="pl_cust")
        c1, c2 = st.columns(2)
        cust_id = rc_sel.split(" — ")[0]
        if c1.button("Open Investigation", key="pl_cust_go", type="primary"):
            navigate_to("Customer Investigation", customer=cust_id)
        # Check if customer has a case
        cust_case = run_query(f"""
            SELECT CASE_ID FROM {DB}.BANKGUARD_RAW.INVESTIGATION_CASES
            WHERE CUSTOMER_ID = '{cust_id}' LIMIT 1
        """)
        if not cust_case.empty:
            if c2.button(f"Open Case {cust_case.iloc[0]['CASE_ID']}", key="pl_case_go", type="primary"):
                navigate_to("Case Management", case=cust_case.iloc[0]["CASE_ID"])


# ===================================================================
# PAGE: Case Management
# ===================================================================
def page_case_management():
    st.header("Investigation Case Management")
    st.caption("Human analyst review required for all dispositions")

    # Back button if arrived via navigation
    nav_from = _consume("nav_from")
    nav_cust_ctx = _consume("nav_customer")
    if nav_from and nav_from != "Case Management":
        if st.button(f"← Back to {nav_from}", key="cm_back"):
            navigate_to(nav_from, customer=nav_cust_ctx)

    def _case_options(df):
        opts = []
        for _, row in df.iterrows():
            risk_class = row.get("RISK_CLASS") or "N/A"
            risk_score = f"Risk Score {row['RISK_SCORE']:.0f}" if pd.notna(row.get("RISK_SCORE")) else "No Score"
            opts.append(f"{row['CASE_ID']} — {row['CUSTOMER_ID']} — {risk_class} — {risk_score} — {row['CASE_STATUS']}")
        return opts

    def _hero_index(opts, target=None):
        search = target or "CASE-FG-1042"
        for i, o in enumerate(opts):
            if o.startswith(search):
                return i
        return 0

    def _show_case_detail(df, case_id, ctx):
        row = df[df["CASE_ID"] == case_id]
        if row.empty:
            return
        h = row.iloc[0]
        st.divider()
        st.subheader(f"Case Detail: {case_id}")
        hc1, hc2, hc3, hc4 = st.columns(4)
        risk_score = h["RISK_SCORE"]
        hc1.metric("Risk Score", f"{risk_score:.0f} / 100" if pd.notna(risk_score) else "N/A")
        hc2.metric("Classification", h.get("RISK_CLASS") or "N/A")
        signal_count = h.get("SIGNAL_COUNT")
        hc3.metric("Active Signals", int(signal_count) if pd.notna(signal_count) else "N/A")
        hc4.metric("Priority", h["CASE_PRIORITY"])
        st.info(f"**Assigned Analyst:** {h['ANALYST']} | **Status:** {h['CASE_STATUS']} | **Opened:** {h['OPEN_DATE']}")
        summary = h.get("SIGNAL_SUMMARY")
        if pd.notna(summary):
            st.markdown(f"**Signal Summary:** {summary}")

        # Drill-down navigation buttons — ctx prefix ensures unique keys per tab
        customer_id = h["CUSTOMER_ID"]
        st.markdown("---")
        b1, b2, b3 = st.columns(3)
        if b1.button("View Customer Investigation", key=f"{ctx}_inv_{case_id}", type="primary"):
            navigate_to("Customer Investigation", customer=customer_id)
        if b2.button("View Risk Evidence", key=f"{ctx}_ev_{case_id}", type="primary"):
            navigate_to("Customer Investigation", customer=customer_id)
        if b3.button("View Related Policies", key=f"{ctx}_pol_{case_id}", type="primary"):
            # Find the first policy linked to this customer
            cust_policies = run_query(f"""
                SELECT DISTINCT POLICY_ID
                FROM {DB}.BANKGUARD_REGULATORY.V_SIGNAL_POLICY_CHAIN
                WHERE CUSTOMER_ID = '{customer_id}'
                ORDER BY POLICY_ID LIMIT 1
            """)
            first_policy = cust_policies.iloc[0]["POLICY_ID"] if not cust_policies.empty else None
            navigate_to("Policy Lookup", policy=first_policy)

        # AI Case Investigation
        st.markdown("---")
        st.caption(AI_DISCLAIMER)
        if st.button("AI Investigate Case", key=f"{ctx}_ai_{case_id}", type="secondary"):
            with st.spinner("AI investigating case..."):
                risk_class = h.get("RISK_CLASS") or "N/A"
                risk_score_val = h["RISK_SCORE"]
                score_text = f"{risk_score_val:.0f}" if pd.notna(risk_score_val) else "N/A"
                prompt = (
                    f"Investigate case {case_id} for customer {customer_id}. "
                    f"Risk score: {score_text}, classification: {risk_class}. "
                    f"Use these exact section headers: "
                    f"EXECUTIVE SUMMARY, OBSERVED EVIDENCE, APPLICABLE POLICIES, "
                    f"AI ANALYSIS, RECOMMENDED NEXT STEPS. "
                    f"Under OBSERVED EVIDENCE list only facts from risk signals and transactions. "
                    f"Under APPLICABLE POLICIES cite policy IDs and sections. "
                    f"Under AI ANALYSIS clearly state this is AI inference requiring review. "
                    f"Do not declare fraud."
                )
                resp = _call_agent(prompt)
                st.session_state[f"ai_case_{ctx}_{case_id}"] = resp
                _log_ai_call(customer_id, case_id, prompt, resp)

        cached_case_ai = st.session_state.get(f"ai_case_{ctx}_{case_id}")
        if cached_case_ai:
            st.markdown("#### AI Case Analysis")
            _render_ai_response(cached_case_ai)

    pre_case = _consume("nav_case")

    tab_open, tab_all = st.tabs(["Open Cases", "All Cases"])

    with tab_open:
        open_cases = run_query(f"""
            SELECT ic.CASE_ID, ic.CUSTOMER_ID, ic.CASE_STATUS, ic.CASE_PRIORITY,
                   ic.ANALYST, ic.OPEN_DATE,
                   rs.RISK_SCORE, rs.RISK_CLASS, rs.SIGNAL_COUNT, rs.SIGNAL_SUMMARY
            FROM {DB}.BANKGUARD_RAW.INVESTIGATION_CASES ic
            LEFT JOIN {DB}.BANKGUARD_RISK.CUSTOMER_RISK_SCORE rs ON ic.CUSTOMER_ID = rs.CUSTOMER_ID
            WHERE ic.CASE_STATUS IN ('OPEN', 'IN_PROGRESS', 'ESCALATED')
            ORDER BY rs.RISK_SCORE DESC NULLS LAST,
                     CASE ic.CASE_PRIORITY WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2
                         WHEN 'MEDIUM' THEN 3 ELSE 4 END,
                     ic.CASE_ID
        """)
        if not open_cases.empty:
            st.metric("Open Cases", len(open_cases))
            options = _case_options(open_cases)
            # Only pre-select in this tab if the case exists here
            open_pre = pre_case if pre_case and any(o.startswith(pre_case) for o in options) else None
            selection = st.selectbox(
                "Select Investigation Case", options,
                index=_hero_index(options, open_pre),
                key="open_case_select",
            )
            _show_case_detail(open_cases, selection.split(" — ")[0], ctx="open")
            st.divider()
            st.subheader("All Open Cases")
            st.dataframe(
                open_cases,
                column_config={
                    "RISK_SCORE": st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=100, format="%d"),
                },
                use_container_width=True, hide_index=True,
            )
        else:
            st.success("No open investigation cases.")

    with tab_all:
        all_cases = run_query(f"""
            SELECT ic.CASE_ID, ic.CUSTOMER_ID, ic.CASE_STATUS, ic.CASE_PRIORITY,
                   ic.ANALYST, ic.OPEN_DATE, ic.CLOSE_DATE, ic.CLOSURE_REASON,
                   rs.RISK_SCORE, rs.RISK_CLASS, rs.SIGNAL_COUNT, rs.SIGNAL_SUMMARY
            FROM {DB}.BANKGUARD_RAW.INVESTIGATION_CASES ic
            LEFT JOIN {DB}.BANKGUARD_RISK.CUSTOMER_RISK_SCORE rs ON ic.CUSTOMER_ID = rs.CUSTOMER_ID
            ORDER BY rs.RISK_SCORE DESC NULLS LAST,
                     CASE ic.CASE_PRIORITY WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2
                         WHEN 'MEDIUM' THEN 3 ELSE 4 END,
                     ic.CASE_ID
            LIMIT 100
        """)
        if not all_cases.empty:
            options = _case_options(all_cases)
            # Only pre-select in this tab if the case exists here
            all_pre = pre_case if pre_case and any(o.startswith(pre_case) for o in options) else None
            selection = st.selectbox(
                "Select Investigation Case", options,
                index=_hero_index(options, all_pre),
                key="all_case_select",
            )
            _show_case_detail(all_cases, selection.split(" — ")[0], ctx="all")
            st.divider()
            st.subheader("All Cases")
            st.dataframe(all_cases, use_container_width=True, hide_index=True)


# ===================================================================
# PAGE: About
# ===================================================================
def page_about():
    st.header("About BANKGUARD AI")
    st.markdown("""
**BANKGUARD AI** is a Risk, Fraud & Regulatory Intelligence Copilot built for the
Snowflake CoCo CLI Hackathon - GCC Edition.

### Workflow
**Signal** &rarr; **Evidence** &rarr; **Finding** &rarr; **Policy Context** &rarr; **Recommended Action**

### Architecture
| Component | Technology |
|---|---|
| Data Storage | Snowflake (BANKGUARD_DB) |
| Risk Engine | Deterministic SQL (M2-RISK-V1.0) |
| Policy Search | Cortex Search |
| AI Reasoning | Cortex Agent + Cortex Analyst |
| Dashboard | Streamlit in Snowflake |

### Governance Principles
1. **Deterministic rules first** - Risk scores computed by SQL rules before any LLM reasoning
2. **Evidence-grounded** - Every finding cites specific transactions, signals, and policies
3. **Human-in-the-loop** - No automated account freezing, regulatory filing, or irreversible actions
4. **Auditable** - Every AI interaction logged with evidence references
5. **No fabrication** - If evidence is insufficient: "Insufficient evidence to support this finding"

### Data Policy
All data is **synthetic**. No real customer information, financial transactions, or
personal identifiers are used at any point.

### Development Phases
| Phase | Status |
|---|---|
| M0 - Project Foundation | Complete |
| M1 - Synthetic Data | Complete |
| M2 - Risk Engine | Complete |
| M3 - Regulatory Knowledge | Complete |
| M4 - AI Investigation | Complete |
| M5 - Streamlit Dashboard | Complete |
| M6 - Polish & Demo | Complete |
""")


# ===================================================================
# Router
# ===================================================================
if page == "Risk Overview":
    page_risk_overview()
elif page == "Customer Investigation":
    page_customer_investigation()
elif page == "Policy Lookup":
    page_policy_lookup()
elif page == "Case Management":
    page_case_management()
elif page == "About":
    page_about()
