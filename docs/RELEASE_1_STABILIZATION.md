# Release 1 — BANKGUARD AI Stabilization

## Root Cause: StreamlitDuplicateElementKey `cm_inv_CASE-FG-1042`

The original M6 Case Management page had two tabs (Open Cases, All Cases) rendering
simple dataframes, plus a standalone "Featured Case: CASE-FG-1042" section outside
the tabs. During development of the cross-page navigation system, `_show_case_detail()`
was introduced to render case details with interactive buttons inside each tab. When
both tabs displayed the same case (CASE-FG-1042 appears in Open Cases AND All Cases),
buttons sharing a common prefix (e.g. `cm_inv_CASE-FG-1042`) were rendered twice in
the same Streamlit script run — Streamlit tabs render all content on every run, not
lazily.

### Fix

`_show_case_detail()` accepts a `ctx` parameter: `"open"` for the Open Cases tab,
`"all"` for the All Cases tab. All dynamically generated button keys use the pattern
`{ctx}_{action}_{case_id}`, producing distinct keys like `open_inv_CASE-FG-1042` and
`all_inv_CASE-FG-1042`. The standalone hero section was removed in favor of the
per-tab selectbox with `_hero_index()` defaulting to CASE-FG-1042.

## Navigation-State Stabilization

Added a complete cross-page navigation system (not present in original M6):

- **Session state keys**: `nav_page`, `nav_customer`, `nav_case`, `nav_policy`,
  `nav_risk_class`, `nav_signal_type`, `nav_from`, `nav_search`
- **`navigate_to()`**: Sets all state keys (unused default to `None`), preventing
  stale values from leaking across transitions. Calls `st.rerun()`.
- **`_consume(key)`**: Reads a nav value once and clears it, ensuring one-time use.
- **Sidebar radio**: Synced with `nav_page` session state via `index=` parameter.
- **Back buttons**: On Customer Investigation, Policy Lookup, Case Management —
  preserve customer context where appropriate.
- **`pre_case` guard**: In Case Management, `pre_case` from `_consume("nav_case")`
  only pre-selects in the tab where the target case actually exists.

## Changes from M6

- Added CSS theme (banking-grade blue palette)
- Added PAGES constant and sidebar radio with session-state sync
- Added navigate_to(), _consume(), and 8 session state keys
- Replaced Customer Investigation text input with HIGH/CRITICAL customer selectbox
- Added Risk Overview selectbox drill-downs (filter by risk class, signal type)
- Added Customer Investigation signal-to-policy drill-down buttons
- Added Customer Investigation case detail section with transactions
- Added Policy Lookup back button, policy detail drill-down, related customers
- Added Case Management _show_case_detail with ctx-prefixed keys
- Added Case Management selectbox-based case selection per tab
- Removed standalone Featured Case section (replaced by per-tab hero default)

## What Was NOT Changed

- Snowflake data model (all schemas, tables, views unchanged)
- Deterministic risk engine (M2-RISK-V1.0)
- Cortex Search integration (POLICY_SEARCH_SERVICE)
- SQL queries (same tables, same columns, same logic)
- Synthetic-data disclaimer and governance controls
- About page content
- environment.yml dependencies

## Reverted from Previous Session

- Interactive/clickable Altair charts (on_select="rerun", selection_point) — reverted
  to static charts for SiS runtime compatibility
- "All scored customers" dropdown — reverted to HIGH/CRITICAL only

## Validation Performed

1. Python compile check: `py_compile` — PASS
2. AST parse and import verification — PASS (5 imports, 12 functions)
3. Widget key audit: 21 static keys + 6 dynamic key patterns — all unique
4. Navigation flow trace: 8 cross-page flows verified
5. SQL query inventory: 22 queries, all referencing original M6 tables/views
6. git diff review against committed M6

## Known Limitations

- No interactive/clickable charts yet (deferred to Release 2)
- Signal-type drill-down from Customer Investigation pre-fills Policy Lookup search
  but does not auto-execute the Cortex Search query (user must press Enter)
- Cortex Agent and Cortex Analyst are listed in About but not integrated in the UI
- SQL uses f-string interpolation (acceptable for synthetic-data demo)
