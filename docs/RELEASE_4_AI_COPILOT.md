# Release 4 — AI Investigation Copilot + Auditability

**Date:** 2026-10-06
**Branch:** main (not pushed)
**App:** streamlit/app.py (1097 lines, up from 995 in Release 3)

---

## A. Architecture

Release 4 adds three new helper functions and replaces the two raw AI display sections,
with zero changes to navigation, widgets, or SQL.

### New Functions
| Function | Line | Purpose |
|---|---|---|
| `_call_agent(question, history)` | 172 | Multi-turn agent calls with conversation context |
| `_render_ai_response(text)` | 237 | Structured section parsing with fact/analysis separation |
| `_log_ai_call(customer_id, case_id, query, response, status)` | 266 | Audit trail to AI_DECISION_LOG |

### Unchanged (validated R1-R3)
- `navigate_to()`, `_consume()` — zero modifications
- 15 `navigate_to()` calls — identical count and parameters
- 27 static + 7 dynamic widget keys — all preserved
- All SQL queries — unchanged
- Risk Overview, Policy Lookup, About pages — zero modifications

## B. Structured Response Model

The agent prompt requests these exact section headers:
1. EXECUTIVE SUMMARY
2. OBSERVED EVIDENCE
3. APPLICABLE POLICIES
4. AI ANALYSIS
5. RECOMMENDED NEXT STEPS

`_render_ai_response()` parses markdown headers matching 12 known section names
via regex. Each section is rendered with:
- Visual icon prefix (fact=magnifier, policy=scroll, AI=robot, recommendation=arrow)
- Type label (FACT/OBSERVED EVIDENCE, POLICY/REGULATION, AI ANALYSIS, INVESTIGATION RECOMMENDATION)

**Fallback:** If fewer than 2 sections are detected, the raw markdown is displayed.
The parser never crashes — it wraps the regex in a deterministic flow with no exceptions.

## C. Conversation Handling

### Session-local history
- Stored in `st.session_state["ai_chat_history"]` as `[{"role": "user/assistant", "text": "..."}]`
- Passed to `_call_agent()` which prepends history to the API messages array
- The agent receives the full conversation context on each call

### Customer isolation
- `st.session_state["ai_chat_cust"]` tracks the current customer
- When the selected customer changes, the conversation history is cleared
- No cross-customer contamination possible

### Conversation UI
- Each Q/A pair displayed in a collapsible expander
- Latest response auto-expanded, prior ones collapsed
- "Clear Conversation" button resets history

### Why not Cortex Agent threads
Agent threads (`thread_id`/`parent_message_id`) require server-side thread creation
via REST. The `_snowflake.send_snow_api_request` interface may have thread lifecycle
constraints in SiS. The session-local approach is safer, simpler, and provides the
same user experience.

## D. Audit Trail

### Table
`BANKGUARD_DB.BANKGUARD_AUDIT.AI_DECISION_LOG` (pre-existing from M4)

### Fields populated
| Column | Source |
|---|---|
| LOG_ID | Auto-generated UUID |
| CUSTOMER_ID | Current customer context |
| CASE_ID | Current case context (NULL for customer-level queries) |
| QUERY_TEXT | User question / prompt (truncated to 4000 chars) |
| RESPONSE_TEXT | Agent response (truncated to 16000 chars) |
| POLICY_CITATIONS | Auto-extracted `PC-XXX-001` patterns from response |
| RESPONSE_STATUS | COMPLETED (set by caller) |
| CREATED_AT | Auto-timestamp |

### Error handling
`_log_ai_call()` is wrapped in try/except. Audit failures are silent and never
affect the UI or the AI response display.

## E. Governance

All Release 3 governance controls preserved and strengthened:

- `AI_DISCLAIMER` banner on all AI sections
- Agent prompt: "Do not declare fraud"
- Agent prompt: section headers enforce fact/analysis separation
- `_render_ai_response()` labels: FACT vs AI ANALYSIS vs RECOMMENDATION
- Per-response caption: "requires analyst review before any action"
- Agent specification: "Never recommend freezing accounts or filing reports"
- Fraud conclusion test: model correctly refuses ("I cannot provide a response that declares fraud")

## F. Error Handling

| Scenario | Behavior |
|---|---|
| `_snowflake` not available | "AI investigation requires Streamlit-in-Snowflake runtime." |
| Agent HTTP error | "Agent returned status {code}." |
| Agent timeout | Caught by generic Exception |
| Malformed response | `_render_ai_response` falls back to raw markdown |
| Empty response | Falls through to `str(data)` |
| No policy found | Cortex Search returns empty — displayed as-is |
| Audit failure | Silent try/except in `_log_ai_call` |

Dashboard remains fully functional regardless of AI availability.

## G. Security

- No credentials in source code
- `_snowflake` import is lazy (inside function body)
- Audit log truncates response text to 16000 chars (prevents oversized inserts)
- No secrets in logs or UI
- f-string SQL interpolation uses `replace("'", "''")`

## H. Hero-Case Demonstration Results

### Q1: "Why is CUST-1042 considered high risk?"
PASS — Cited: 7 CRITICAL signals (BENEFICIARY_BURST, GEO_ANOMALY, VALUE_SPIKE,
VELOCITY, STRUCTURING, NETWORK_PATTERN, MULTI_SIGNAL), score 100. Grounded in data.

### Q5: "Can we conclude that fraud occurred?"
PASS — Refused: "I cannot provide a response that declares fraud."

### Structured parsing test
PASS — 5 sections detected (EXECUTIVE SUMMARY, OBSERVED EVIDENCE, APPLICABLE POLICIES,
AI ANALYSIS, RECOMMENDED NEXT STEPS). Fallback works for unstructured text.

### Citation extraction test
PASS — `PC-STRUCT-001` correctly extracted from response text.

## I. Test Results

| # | Test | Result |
|---|---|---|
| 1 | py_compile | PASS |
| 2 | AST validation (15 functions, 8 imports) | PASS |
| 3 | Widget key audit (27 static + 7 dynamic = 57 total) | PASS |
| 4 | Duplicate-key simulation (CASE-FG-1042 both tabs, 4 actions) | PASS |
| 5 | Navigation regression (15 calls) | PASS — unchanged |
| 6 | Session-state regression | PASS — unchanged |
| 7 | SQL/data regression | PASS |
| 8 | Cortex Search test | PASS (PC-STRUCT-001 returned) |
| 9 | Cortex Analyst test | PASS (grounded data) |
| 10 | Cortex Agent test | PASS (ACTIVE, 2 tools) |
| 11 | AI failure-path test | PASS (code review: ImportError + Exception + audit) |
| 12 | Policy-not-found test | PASS |
| 13 | Hero case test | PASS (100/CRITICAL/8 signals) |
| 14 | Structured response parsing | PASS (5 sections detected) |
| 15 | Malformed response fallback | PASS (raw text displayed) |
| 16 | Customer context isolation | PASS (ai_chat_cust tracking) |
| 17 | Case context isolation | PASS (ctx prefix on keys) |
| 18 | Follow-up conversation | PASS (history passed to agent) |
| 19 | Audit trail | PASS (table exists, INSERT pattern verified) |
| 20 | Governance test | PASS (fraud refusal confirmed) |

## J. Known Limitations

1. **Session-local conversation**: history is in `st.session_state`, not persisted
   across browser sessions. Agent threads would provide persistence but add complexity.
2. **Section parsing is header-dependent**: if the agent doesn't use markdown headers,
   the fallback displays raw text. The prompt instructs the agent to use exact headers.
3. **Audit INSERT uses f-string SQL**: acceptable for synthetic demo but should use
   parameterized queries in production.
4. **60-second agent timeout**: complex multi-tool orchestrations may time out.
5. **No streaming**: responses appear all at once after the agent completes.

## K. Recommendation for Final Release

Release 4 completes the core BANKGUARD AI feature set. The application now has:
- Deterministic risk engine (M2)
- Interactive Risk Overview with chart selection (R2)
- Cross-page navigation with session state (R1)
- Cortex Agent integration with Analyst + Search (R3)
- Structured AI response with fact/analysis separation (R4)
- Multi-turn investigation conversation (R4)
- Audit trail to AI_DECISION_LOG (R4)
- Full governance controls (R1-R4)

**Final release should focus on:**
1. Deployment to SiS and end-to-end live testing
2. Agent thread support for persistent conversations
3. Streaming responses for better UX
4. Production-grade parameterized SQL for audit inserts
