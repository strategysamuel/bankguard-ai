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
# Constants
# ---------------------------------------------------------------------------
DB = "BANKGUARD_DB"
RISK_COLORS = {"LOW": "#4CAF50", "MEDIUM": "#FF9800", "HIGH": "#F44336", "CRITICAL": "#9C27B0"}
SEVERITY_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.title("BANKGUARD AI")
st.sidebar.caption("Risk, Fraud & Regulatory Intelligence Copilot")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    ["Risk Overview", "Customer Investigation", "Policy Lookup", "Case Management", "About"],
)

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

    with col_left:
        st.subheader("Risk Classification Distribution")
        dist = run_query(f"""
            SELECT RISK_CLASS, COUNT(*) AS CUSTOMER_COUNT
            FROM {DB}.BANKGUARD_RISK.CUSTOMER_RISK_SCORE
            GROUP BY RISK_CLASS
        """)
        if not dist.empty:
            dist["RISK_CLASS"] = pd.Categorical(dist["RISK_CLASS"], categories=SEVERITY_ORDER, ordered=True)
            dist = dist.sort_values("RISK_CLASS")
            chart = alt.Chart(dist).mark_bar().encode(
                x=alt.X("RISK_CLASS:N", sort=SEVERITY_ORDER, title="Risk Class"),
                y=alt.Y("CUSTOMER_COUNT:Q", title="Customers"),
                color=alt.Color("RISK_CLASS:N", scale=alt.Scale(
                    domain=SEVERITY_ORDER,
                    range=[RISK_COLORS[k] for k in SEVERITY_ORDER]
                ), legend=None),
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)

    with col_right:
        st.subheader("Signal Type Distribution")
        sig_dist = run_query(f"""
            SELECT SIGNAL_TYPE, COUNT(*) AS SIGNAL_COUNT
            FROM {DB}.BANKGUARD_RISK.RISK_SIGNAL_EVIDENCE
            WHERE SIGNAL_TYPE != 'MULTI_SIGNAL'
            GROUP BY SIGNAL_TYPE ORDER BY SIGNAL_COUNT DESC
        """)
        if not sig_dist.empty:
            chart2 = alt.Chart(sig_dist).mark_bar(color="#1E88E5").encode(
                x=alt.X("SIGNAL_COUNT:Q", title="Detections"),
                y=alt.Y("SIGNAL_TYPE:N", sort="-x", title="Signal Type"),
            ).properties(height=300)
            st.altair_chart(chart2, use_container_width=True)

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
    else:
        st.info("No HIGH or CRITICAL risk customers found.")


# ===================================================================
# PAGE: Customer Investigation
# ===================================================================
def page_customer_investigation():
    st.header("Customer Investigation")
    st.caption("Evidence-backed risk analysis - requires analyst review for all findings")

    col_search, col_quick = st.columns([2, 1])
    with col_search:
        customer_id = st.text_input("Customer ID", value="CUST-1042", placeholder="e.g. CUST-1042")
    with col_quick:
        st.caption("Quick Links")
        if st.button("Hero Case: CUST-1042"):
            customer_id = "CUST-1042"

    if not customer_id:
        st.info("Enter a Customer ID to begin investigation.")
        return

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
        for _, sig in signals.iterrows():
            severity = sig["SEVERITY"]
            color = RISK_COLORS.get(severity, "#666")
            with st.expander(f"{sig['SIGNAL_TYPE']} - {severity} (Score: {sig['SIGNAL_SCORE']:.0f})", expanded=(severity == "CRITICAL")):
                st.markdown(f"**Severity:** :{severity.lower()}[{severity}]" if severity in ("HIGH","CRITICAL") else f"**Severity:** {severity}")
                st.markdown(f"**Evidence:** {sig['EVIDENCE_SUMMARY']}")
                st.caption(f"Observation period: {sig['OBSERVATION_START']} to {sig['OBSERVATION_END']}")

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

    # Recent transactions
    st.divider()
    st.subheader("Recent Transactions")
    txns = run_query(f"""
        SELECT TRANSACTION_ID, TRANSACTION_DATE, TRANSACTION_TYPE, AMOUNT, CHANNEL,
               TRANSACTION_COUNTRY, BENEFICIARY_ID, TRANSACTION_STATUS
        FROM {DB}.BANKGUARD_CORE.V_TRANSACTION_ENRICHED
        WHERE CUSTOMER_ID = '{customer_id}'
        ORDER BY TRANSACTION_DATE DESC
        LIMIT 50
    """)
    if not txns.empty:
        st.dataframe(
            txns,
            column_config={"AMOUNT": st.column_config.NumberColumn("Amount (INR)", format="%.2f")},
            use_container_width=True, hide_index=True,
        )


# ===================================================================
# PAGE: Policy Lookup
# ===================================================================
def page_policy_lookup():
    st.header("Regulatory Policy Lookup")
    st.caption("SYNTHETIC DEMONSTRATION POLICIES - not actual legal or regulatory advice")

    query = st.text_input("Search policies", placeholder="e.g. transaction structuring threshold")

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
    if not active.empty:
        st.dataframe(active, use_container_width=True, hide_index=True)


# ===================================================================
# PAGE: Case Management
# ===================================================================
def page_case_management():
    st.header("Investigation Case Management")
    st.caption("Human analyst review required for all dispositions")

    tab_open, tab_all = st.tabs(["Open Cases", "All Cases"])

    with tab_open:
        open_cases = run_query(f"""
            SELECT ic.CASE_ID, ic.CUSTOMER_ID, ic.CASE_STATUS, ic.CASE_PRIORITY,
                   ic.ANALYST, ic.OPEN_DATE,
                   rs.RISK_SCORE, rs.RISK_CLASS, rs.SIGNAL_COUNT
            FROM {DB}.BANKGUARD_RAW.INVESTIGATION_CASES ic
            LEFT JOIN {DB}.BANKGUARD_RISK.CUSTOMER_RISK_SCORE rs ON ic.CUSTOMER_ID = rs.CUSTOMER_ID
            WHERE ic.CASE_STATUS IN ('OPEN', 'IN_PROGRESS', 'ESCALATED')
            ORDER BY CASE ic.CASE_PRIORITY
                WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2
                WHEN 'MEDIUM' THEN 3 ELSE 4 END, ic.OPEN_DATE
        """)
        if not open_cases.empty:
            st.metric("Open Cases", len(open_cases))
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
            SELECT CASE_ID, CUSTOMER_ID, CASE_STATUS, CASE_PRIORITY,
                   ANALYST, OPEN_DATE, CLOSE_DATE, CLOSURE_REASON
            FROM {DB}.BANKGUARD_RAW.INVESTIGATION_CASES
            ORDER BY OPEN_DATE DESC
            LIMIT 100
        """)
        if not all_cases.empty:
            st.dataframe(all_cases, use_container_width=True, hide_index=True)

    # Hero case highlight
    st.divider()
    st.subheader("Featured Case: CASE-FG-1042")
    hero = run_query(f"""
        SELECT ic.CASE_ID, ic.CUSTOMER_ID, ic.CASE_STATUS, ic.CASE_PRIORITY,
               ic.ANALYST, ic.OPEN_DATE,
               rs.RISK_SCORE, rs.RISK_CLASS, rs.SIGNAL_COUNT, rs.SIGNAL_SUMMARY
        FROM {DB}.BANKGUARD_RAW.INVESTIGATION_CASES ic
        JOIN {DB}.BANKGUARD_RISK.CUSTOMER_RISK_SCORE rs ON ic.CUSTOMER_ID = rs.CUSTOMER_ID
        WHERE ic.CASE_ID = 'CASE-FG-1042'
    """)
    if not hero.empty:
        h = hero.iloc[0]
        hc1, hc2, hc3, hc4 = st.columns(4)
        hc1.metric("Risk Score", f"{h['RISK_SCORE']:.0f} / 100")
        hc2.metric("Classification", h["RISK_CLASS"])
        hc3.metric("Active Signals", int(h["SIGNAL_COUNT"]))
        hc4.metric("Priority", h["CASE_PRIORITY"])
        st.info(f"**Assigned Analyst:** {h['ANALYST']} | **Status:** {h['CASE_STATUS']}")
        st.markdown(f"**Signal Summary:** {h['SIGNAL_SUMMARY']}")


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
