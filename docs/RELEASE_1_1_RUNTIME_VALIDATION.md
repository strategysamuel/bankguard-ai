# Release 1.1 — Runtime Regression Validation Report

**Date:** 2026-10-06
**Branch:** main (not pushed)
**App:** streamlit/app.py (858 lines)

---

## A. Tests Performed

| # | Test | Method |
|---|---|---|
| 1 | Duplicate widget key — exhaustive | Static analysis + simulated expansion of all 27 key patterns |
| 2 | Navigation regression — 8 flows | Code trace + live Snowflake data verification for each flow |
| 3 | Session state correctness | Manual review of navigate_to(), _consume(), sidebar sync |
| 4 | Case Management — dual-tab simulation | Simulated CASE-FG-1042 in both Open and All tabs |
| 5 | Customer Investigation — data + widgets | Live query of CUST-1042 risk data + widget key analysis |
| 6 | Policy Lookup — data + widgets | Live query of policy chain + related customer/case data |
| 7 | SQL/data regression | Verified all 9 tables/views exist with expected row counts |
| 8 | Deployment config | Verified snowflake.yml against live Snowflake objects |
| 9 | Code quality | py_compile, AST parse, import check, function inventory |

## B. Tests Passed

ALL 9 TESTS PASSED. No regressions found. No fixes required.

## C. Tests Failed

None.

## D. Duplicate-Key Validation

### Static Keys (21) — ALL UNIQUE
```
_nav_radio, ov_rc, ov_rc_cust, ov_rc_go, ov_sig, ov_sig_cust, ov_sig_go,
ov_hr_cust, ov_hr_go, ci_back, ci_cust, ci_pol_select, ci_pol_go, pl_back,
pl_pol, pl_cust, pl_cust_go, pl_case_go, cm_back, open_case_select,
all_case_select
```

### Dynamic Keys (6 patterns) — ALL UNIQUE AFTER EXPANSION
| Pattern | Location | Variables | Collision Risk |
|---|---|---|---|
| `ci_sig_pol_{idx}` | Signal evidence loop | idx = RangeIndex 0-N | None — fresh query, sequential index |
| `ci_case_sel_{customer_id}` | Case selectbox | One customer per page render | None — single value per run |
| `ci_open_cm_{sel_case_id}` | Open Case button | One case selected | None — single value per run |
| `{ctx}_inv_{case_id}` | Case detail button | ctx=open/all, case_id varies | None — ctx prefix differentiates |
| `{ctx}_ev_{case_id}` | Risk evidence button | ctx=open/all, case_id varies | None — ctx prefix differentiates |
| `{ctx}_pol_{case_id}` | Policy button | ctx=open/all, case_id varies | None — ctx prefix differentiates |

### Critical Scenario: CASE-FG-1042 in Both Tabs
- Confirmed via live query: CASE-FG-1042 (ESCALATED) appears in both Open Cases and All Cases
- Open tab generates: `open_inv_CASE-FG-1042`, `open_ev_CASE-FG-1042`, `open_pol_CASE-FG-1042`
- All tab generates: `all_inv_CASE-FG-1042`, `all_ev_CASE-FG-1042`, `all_pol_CASE-FG-1042`
- **No collision. The original error `cm_inv_CASE-FG-1042` is resolved.**

### Total Unique Keys Tested: 47 (via simulated expansion)
- Zero collisions across all static + dynamic combinations.

## E. Navigation Validation

| Flow | Source → Target | Context Passed | Context Consumed | Status |
|---|---|---|---|---|
| A | Risk Overview → Customer Investigation | `customer=CUST-1042` | `_consume("nav_customer")` at line 404 | PASS |
| B | Customer Investigation → Case Management | `case=CASE-FG-1042, customer=CUST-1042` | `_consume("nav_case")` at 733, `_consume("nav_customer")` at 675 | PASS |
| C | Case Management → Customer Investigation | `customer=CUST-1042` (from case detail) | `_consume("nav_customer")` at 404 | PASS |
| D | Case Management → Risk Evidence | `customer=CUST-1042` (same target as C) | `_consume("nav_customer")` at 404 | PASS |
| E | Case Management → Policy Lookup | `policy=PC-BEN-001` (first linked policy) | `_consume("nav_policy")` at 601 | PASS |
| F | Policy Lookup → Customer Investigation | `customer=CUST-1042` | `_consume("nav_customer")` at 404 | PASS |
| G | Policy Lookup → Case Management | `case=CASE-FG-1042` | `_consume("nav_case")` at 733 | PASS |
| H | Risk Overview → drill-down → investigation | `customer=sel_cust` from selectbox | `_consume("nav_customer")` at 404 | PASS |

All 8 flows confirmed with live Snowflake data to verify the entities exist and are correctly linked.

## F. Session-State Validation

### Keys and Purposes
| Key | Purpose | Default | Set By | Consumed By |
|---|---|---|---|---|
| `nav_page` | Current/target page | `"Risk Overview"` | `navigate_to()`, sidebar radio | Sidebar radio `index=` |
| `nav_customer` | Target customer for pre-selection | `None` | `navigate_to()` | Customer Investigation, Policy Lookup back button, Case Management back button |
| `nav_case` | Target case for pre-selection | `None` | `navigate_to()` | Case Management `pre_case` |
| `nav_policy` | Target policy for pre-selection | `None` | `navigate_to()` | Policy Lookup `pre_policy` |
| `nav_risk_class` | Pre-filter Risk Overview | `None` | `navigate_to()` | Risk Overview `pre_risk` |
| `nav_signal_type` | Pre-filter Risk Overview | `None` | `navigate_to()` | Risk Overview `pre_sig` |
| `nav_from` | Source page for back button | `None` | `navigate_to()` | Customer Investigation, Policy Lookup, Case Management |
| `nav_search` | Pre-fill Policy Lookup search | `None` | `navigate_to()` | Policy Lookup `text_input` value |

### Correctness Checks
- `navigate_to()` sets ALL 8 keys on every call (unused → `None`): **PASS** — no stale leakage
- `_consume()` reads and clears atomically: **PASS** — one-time use per rerun
- Sidebar radio sync with `nav_page`: **PASS** — bidirectional sync
- `pre_case` tab guard: **PASS** — only pre-selects in tab where case exists
- `nav_search` edge case (empty string): **PASS** — `or ""` handles None/empty correctly

## G. Case Management Validation

- Open Cases tab: Queries `CASE_STATUS IN ('OPEN','IN_PROGRESS','ESCALATED')` — **PASS**
- All Cases tab: Queries all cases with LIMIT 100 — **PASS**
- CASE-FG-1042 in both tabs: Confirmed via live query, keys are `open_*` vs `all_*` — **PASS**
- Selecting another case (e.g., CASE-FG-1001): Different case_id → different keys — **PASS**
- Case detail rendering via `_show_case_detail()`: Metrics, analyst info, signal summary — **PASS**
- View Customer Investigation button: `navigate_to("Customer Investigation", customer=...)` — **PASS**
- View Risk Evidence button: `navigate_to("Customer Investigation", customer=...)` — **PASS**
- View Related Policies button: Queries first linked policy, navigates — **PASS**
- Hero default (CASE-FG-1042): `_hero_index()` defaults to "CASE-FG-1042" — **PASS**

## H. Customer Investigation Validation

- Customer selectbox: HIGH + CRITICAL customers, sorted by risk score — **PASS**
- CUST-1042 pre-selection: `cust_ids.index("CUST-1042")` succeeds (present in list) — **PASS**
- Risk score display: CUST-1042 → 100/100, CRITICAL, 8 signals — **PASS** (verified via live query)
- Risk signals loop: 8 signals, keys `ci_sig_pol_0` through `ci_sig_pol_7` — **PASS**
- Policy chain: 5+ policies linked to CUST-1042 — **PASS**
- Case detail + transactions: CASE-FG-1042 for CUST-1042 — **PASS**
- Navigate to Case Management: `navigate_to("Case Management", case=..., customer=...)` — **PASS**
- Navigate to Policy Lookup: `navigate_to("Policy Lookup", policy=..., customer=...)` — **PASS**

## I. Policy Lookup Validation

- Cortex Search integration: `SNOWFLAKE.CORTEX.SEARCH_PREVIEW` on `POLICY_SEARCH_SERVICE` — **Preserved** (not modified)
- `nav_search` pre-fill: `value=_consume("nav_search") or ""` — **PASS**
- Active policies table: Queries `BANKGUARD_REGULATORY.POLICIES WHERE STATUS='ACTIVE'` — **PASS**
- Policy detail drill-down: Selectbox + metrics + sections — **PASS**
- Related high-risk customers: Confirmed CUST-1042 linked to PC-BEN-001 — **PASS**
- Open Investigation: `navigate_to("Customer Investigation", customer=...)` — **PASS**
- Open Case: Checks for case, navigates with `case=...` — **PASS**

## J. SQL/Data Regression

### Hero Data Verified (Live Queries)
| Check | Expected | Actual | Status |
|---|---|---|---|
| CUST-1042 exists | yes | yes | PASS |
| CUST-1042 RISK_SCORE | 100 | 100.00 | PASS |
| CUST-1042 RISK_CLASS | CRITICAL | CRITICAL | PASS |
| CUST-1042 SIGNAL_COUNT | 8 | 8 | PASS |
| CASE-FG-1042 exists | yes | yes | PASS |
| CASE-FG-1042 STATUS | ESCALATED | ESCALATED | PASS |
| CASE-FG-1042 in Open Cases query | yes | yes | PASS |
| CASE-FG-1042 in All Cases query | yes | yes | PASS |

### All Tables/Views Accessible
| Object | Row Count |
|---|---|
| BANKGUARD_RAW.CUSTOMERS | 1,001 |
| BANKGUARD_RISK.CUSTOMER_RISK_SCORE | 492 |
| BANKGUARD_RISK.RISK_SIGNAL_EVIDENCE | 843 |
| BANKGUARD_RAW.INVESTIGATION_CASES | 151 |
| BANKGUARD_RAW.TRANSACTIONS | 95,607 |
| BANKGUARD_CORE.V_CUSTOMER_360 | 1,001 |
| BANKGUARD_CORE.V_TRANSACTION_ENRICHED | 95,607 |
| BANKGUARD_REGULATORY.POLICIES | 19 |
| BANKGUARD_REGULATORY.V_SIGNAL_POLICY_CHAIN | 2,261 |

No SQL query modifications were made in Release 1.1. All queries reference the same M6 tables/views.

## K. snowflake.yml Validation

| Field | Value | Verified Against |
|---|---|---|
| database | BANKGUARD_DB | Live: exists | PASS |
| schema | PUBLIC | Live: exists in BANKGUARD_DB | PASS |
| query_warehouse | COMPUTE_WH | Live: exists, STARTED | PASS |
| runtime_name | SYSTEM$ST_CONTAINER_RUNTIME_PY3_11 | Standard SiS runtime | PASS |
| compute_pool | SYSTEM_COMPUTE_POOL_CPU | Standard SiS pool | PASS |
| main_file | streamlit/app.py | File exists (858 lines) | PASS |
| artifacts | streamlit/ | Directory exists with app.py + environment.yml | PASS |

## L. Remaining Issues

1. **Cortex Agent / Cortex Analyst not integrated in UI** — listed in About page but no API calls in code. This is a pre-existing M6 condition, not a regression.
2. **SQL f-string interpolation** — not parameterized. Acceptable for synthetic-data demo; not suitable for production.
3. **Signal drill-down pre-fills search but doesn't auto-execute** — user must interact with the text input to trigger Cortex Search. Minor UX limitation.
4. **`_consume("nav_customer")` consumed by Policy Lookup back button** (line 558) means the customer context is used for back-navigation only, not for filtering the policy list. Correct behavior.

No regressions. No fixes required.

## M. Recommendation for Release 2

Release 1 stabilization is validated and safe. Release 2 can proceed with:

1. **Interactive/clickable Altair charts** — confirm `on_select="rerun"` is supported by `SYSTEM$ST_CONTAINER_RUNTIME_PY3_11` before implementing
2. **Expanded customer dropdown** — include all scored customers (LOW through CRITICAL)
3. **Cortex Agent / Cortex Analyst UI integration** — if the backend services are deployed
4. **Auto-execute Cortex Search** on navigation to Policy Lookup with a search term

**Prerequisite for Release 2:** Verify the exact Streamlit and Altair versions bundled in the `SYSTEM$ST_CONTAINER_RUNTIME_PY3_11` runtime to confirm `on_select` support before implementing interactive charts.
