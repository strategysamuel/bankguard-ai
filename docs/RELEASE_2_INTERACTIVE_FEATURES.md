# Release 2 — Interactive Features

**Date:** 2026-10-06
**Branch:** main (not pushed)
**App:** streamlit/app.py (887 lines, up from 858 in Release 1)

---

## A. Runtime Capability Findings

| Aspect | Finding |
|---|---|
| Runtime | `SYSTEM$ST_CONTAINER_RUNTIME_PY3_11` (container runtime) |
| Streamlit version | 1.50+ (any version supported, including nightly) |
| Altair version | 5.x (bundled with Streamlit 1.50+) |
| `st.altair_chart(on_select="rerun")` | **AVAILABLE** — introduced in Streamlit 1.36 |
| `alt.selection_point(name=..., fields=[...])` | **AVAILABLE** — Altair 5.x API |
| Chart selection events | **AVAILABLE** — standard Streamlit event system |

**Source:** Snowflake documentation — "Manage dependencies for your Streamlit app":
container runtimes support Streamlit 1.50+ with any later version via artifact repository.

## B. Interactive Approach Selected

**Dual-mode chart interaction:**
1. **Altair chart with `on_select="rerun"`** — clicking a bar highlights it (opacity
   dims unselected bars) and syncs the selectbox filter below
2. **Selectbox fallback** — always works, synchronized with chart click state

Selection parameters are explicitly named (`name="rc_sel"`, `name="sig_sel"`) to
avoid fragile auto-generated parameter names. Event parsing is wrapped in try/except
for graceful degradation if the Altair event format changes between versions.

**Priority order:** chart click > navigation state > default ("All")

## C. Files Changed

| File | Change | Lines |
|---|---|---|
| `streamlit/app.py` | Interactive charts + expanded customer selector | 887 (was 858) |
| `docs/RELEASE_2_INTERACTIVE_FEATURES.md` | This document | New |

No other files modified. `snowflake.yml`, `environment.yml`, navigation functions,
Case Management, Policy Lookup — all unchanged.

## D. Customer Selector Changes

**Before (Release 1):** Selectbox showed HIGH + CRITICAL customers only.

**After (Release 2):** Selectbox shows ALL scored customers, sorted:
CRITICAL (highest risk first) → HIGH → MEDIUM → LOW

Format: `CUST-1042 — CRITICAL — Risk Score 100 — 8 Signals`

Navigation pre-selection still works: if a customer navigated from another page
exists in the list, it's pre-selected. Otherwise defaults to first (CUST-1042).

## E. Risk-Level Interaction

### Risk Classification Chart (left column)
- Static bar chart replaced with interactive `selection_point` chart
- Clicking a bar highlights it (opacity 1.0 vs 0.35 for unselected)
- Selection syncs to the selectbox below
- Selectbox filters to customers in that risk class
- Each customer row has "Open Investigation" button → Customer Investigation

### Signal Type Chart (right column)
- Same interactive pattern with `selection_point`
- Clicking a signal type bar highlights it and syncs the selectbox
- Customers with that signal type are displayed
- "Open Investigation" button navigates with correct customer ID

### Fallback
If `on_select` event parsing fails (e.g., unexpected format), the try/except
silently falls through and the selectbox operates independently. The chart
renders but is not interactive — no crash, no error.

## F. Navigation Preservation

### Functions — UNCHANGED
- `navigate_to()`: Same signature, same 8 session-state keys, same `st.rerun()`
- `_consume()`: Same read-once-and-clear pattern
- Session state initialization: Same 8 keys with same defaults

### Flows — ALL PRESERVED (15 navigate_to calls)
| # | Flow | Status |
|---|---|---|
| 1 | Risk Overview → Customer Investigation (3 paths) | Preserved |
| 2 | Customer Investigation → Policy Lookup (signal drill) | Preserved |
| 3 | Customer Investigation → Policy Lookup (policy drill) | Preserved |
| 4 | Customer Investigation → Case Management | Preserved |
| 5 | Policy Lookup → Customer Investigation | Preserved |
| 6 | Policy Lookup → Case Management | Preserved |
| 7 | Case Management → Customer Investigation | Preserved |
| 8 | Case Management → Risk Evidence | Preserved |
| 9 | Case Management → Policy Lookup | Preserved |
| 10 | Back buttons (3 pages) | Preserved |

## G. Widget-Key Validation

| Category | Count | Status |
|---|---|---|
| Static keys | 23 (+2 from chart keys) | ALL UNIQUE |
| Dynamic key patterns | 6 | ALL UNIQUE after expansion |
| Total keys tested (simulated) | 49 | ZERO COLLISIONS |

New keys added: `ov_rc_chart`, `ov_sig_chart` — both unique, no conflicts.

Case Management dual-tab simulation: CASE-FG-1042 tested in both tabs —
`open_inv_CASE-FG-1042` and `all_inv_CASE-FG-1042` remain distinct.

## H. Regression Results

| Test | Result |
|---|---|
| py_compile | PASS |
| AST parse (12 functions, 5 imports) | PASS |
| Widget key audit (49 keys) | PASS — zero duplicates |
| Case Management dual-tab simulation | PASS |
| Customer Investigation signal loop | PASS |
| navigate_to() inventory (15 calls) | PASS — unchanged |
| _consume() inventory (12 calls) | PASS — unchanged |
| Hero data: CUST-1042, score=100, CRITICAL, 8 signals | PASS |
| Hero case: CASE-FG-1042, ESCALATED, CRITICAL | PASS |
| All 9 tables/views accessible | PASS |
| snowflake.yml configuration | PASS — unchanged from Release 1 |

## I. Known Limitations

1. **Chart → selectbox sync is one-directional**: clicking the chart syncs the
   selectbox, but changing the selectbox doesn't deselect the chart highlight.
   Functionally correct; minor visual inconsistency.
2. **Signal drill-down pre-fills search but doesn't auto-execute**: user must
   interact with the Policy Lookup text input to trigger Cortex Search.
3. **Cortex Agent/Analyst not integrated** — deferred to Release 3.
4. **SQL f-string interpolation** — acceptable for synthetic-data demo.
5. **`on_select` event format**: uses named selection params to avoid fragile
   auto-generated names, but the exact dict structure may vary between Streamlit
   versions. The try/except ensures graceful degradation.

## J. Recommended Next Release

**Release 3 — Cortex AI Integration:**
1. Cortex Agent integration for natural-language investigation queries
2. Cortex Analyst integration for analytical queries over risk data
3. Isolated behind feature flags or separate page section
4. Should not touch navigation architecture or widget keys
