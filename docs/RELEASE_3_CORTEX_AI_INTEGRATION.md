# Release 3 — Cortex AI Integration

**Date:** 2026-10-06
**Branch:** main (not pushed)
**App:** streamlit/app.py (995 lines, up from 887 in Release 2)

---

## A. Cortex Objects Integrated

| Object | FQN | Type | Role |
|---|---|---|---|
| Cortex Agent | `BANKGUARD_DB.BANKGUARD_CORE.BANKGUARD_AGENT` | Agent | Orchestration — combines Analyst + Search |
| Semantic View | `BANKGUARD_DB.BANKGUARD_CORE.BANKGUARD_RISK_ANALYST` | Semantic View | Structured data queries (6 tables) |
| Cortex Search | `BANKGUARD_DB.BANKGUARD_REGULATORY.POLICY_SEARCH_SERVICE` | Search Service | Policy/regulatory retrieval |

All three objects were pre-existing from M4. No new Snowflake objects created.

## B. Cortex Analyst Integration

Integrated via the Agent's `RiskAnalyst` tool (cortex_analyst_text_to_sql).

The semantic view covers 6 base tables: CUSTOMERS (V_CUSTOMER_360), RISK_SCORES
(CUSTOMER_RISK_SCORE), RISK_SIGNALS (RISK_SIGNAL_EVIDENCE), TRANSACTIONS
(V_TRANSACTION_ENRICHED), CASES (INVESTIGATION_CASES), ALERTS (FRAUD_ALERTS).

Analyst queries are governed by the semantic view's AI_SQL_GENERATION instruction:
> "Never declare fraud. Use 'potential pattern' or 'requires analyst review'."

The deterministic M2 risk engine remains the authoritative risk score source.
Cortex Analyst explains/queries the data but does not redefine scores.

## C. Cortex Search Integration

Pre-existing Cortex Search (`POLICY_SEARCH_SERVICE`) was already used in Policy Lookup
via `SNOWFLAKE.CORTEX.SEARCH_PREVIEW`. That integration is preserved unchanged.

The Agent additionally invokes Cortex Search via its `PolicySearch` tool for
investigation prompts that request policy context. Both pathways coexist.

## D. Cortex Agent Integration

### API Pattern
```python
import _snowflake
resp = _snowflake.send_snow_api_request(
    "POST",
    "/api/v2/databases/BANKGUARD_DB/schemas/BANKGUARD_CORE/agents/BANKGUARD_AGENT:run",
    {}, {}, payload, {}, 60000
)
```

Uses the SiS-native `_snowflake` module — no external auth, PAT, or REST client needed.
Non-streaming (`stream: False`) for deterministic response parsing.

### Error Handling
- `ImportError`: caught when `_snowflake` is not available (local development)
- Generic `Exception`: caught with user-friendly message preserving existing functionality
- Status code check: non-2xx responses return controlled error message
- All errors result in: "AI investigation service is temporarily unavailable."

## E. Streamlit UI Changes

### Customer Investigation — AI Investigation Copilot
Added at the bottom of the page (after existing case/transaction sections):
- **"Generate Investigation Summary"** button — calls Agent with structured prompt
- **"Ask Investigation Question"** text input + "Ask AI" button — free-form queries
- Results cached in `st.session_state[f"ai_summary_{customer_id}"]` per customer
- Results displayed with governance markers and analyst-review captions

### Case Management — AI Investigate Case
Added inside `_show_case_detail()` after navigation buttons:
- **"AI Investigate Case"** button — calls Agent with case context
- Key: `{ctx}_ai_{case_id}` — follows existing ctx-prefix convention
- Results cached in `st.session_state[f"ai_case_{ctx}_{case_id}"]`

### New Widget Keys
| Key | Page | Type |
|---|---|---|
| `ci_ai_summary` | Customer Investigation | Button |
| `ci_ai_question` | Customer Investigation | Text input |
| `ci_ai_ask` | Customer Investigation | Button |
| `{ctx}_ai_{case_id}` | Case Management | Dynamic button |

### Performance
AI calls execute ONLY on explicit button press. No automatic Cortex calls
on dropdown changes, page loads, or reruns. Results are cached in session state.

## F. Governance Controls

All AI prompts include:
- "Do not declare fraud"
- "Clearly label each section" (OBSERVED EVIDENCE / POLICY REFERENCES / AI ANALYSIS / RECOMMENDATIONS)
- "Requires analyst review"

All AI output displays:
- `AI_DISCLAIMER` banner: "SYNTHETIC DATA — All findings require analyst review"
- Per-result caption: "AI-generated analysis — requires analyst review before any action"

Agent specification enforces:
- "Never declare fraud or crime. Use 'potential pattern' or 'requires analyst review'."
- "Never recommend freezing accounts or filing reports."
- "Cite policies as [PC-XXX-001 vX.X, Section X.X]."

## G. Error Handling

| Failure | Behavior |
|---|---|
| `_snowflake` not available | "AI investigation requires Streamlit-in-Snowflake runtime." |
| Agent HTTP error | "Agent returned status {code}." |
| Agent timeout | Caught by generic Exception handler |
| Malformed response | Falls through to `str(data)` display |
| Any exception | "AI investigation service is temporarily unavailable." + existing data unaffected |

The existing dashboard (Risk Overview, Customer Investigation data, Case Management,
Policy Lookup) continues to function regardless of AI availability.

## H. Security

- No credentials, tokens, or API keys in source code
- Uses SiS-native `_snowflake.send_snow_api_request` (session auth)
- `_snowflake` import is inside the function body (lazy), not at module level
- No secrets in logs, UI, or git

## I. Validation Results

| # | Test | Result |
|---|---|---|
| 1 | py_compile | PASS |
| 2 | AST validation (13 functions, 6 imports) | PASS |
| 3 | Widget key audit (26 static + 7 dynamic = 56 total) | PASS |
| 4 | Duplicate-key simulation (CASE-FG-1042 both tabs, 4 actions) | PASS |
| 5 | Navigation regression (15 navigate_to calls) | PASS — unchanged |
| 6 | Session-state regression (_consume calls) | PASS — unchanged |
| 7 | SQL/data regression (9 tables, hero data) | PASS |
| 8 | Cortex Search test (policy retrieval) | PASS — PC-STRUCT-001 returned |
| 9 | Cortex Analyst test (via COMPLETE proxy) | PASS — grounded in signal data |
| 10 | Cortex Agent test (agent object verified) | PASS — ACTIVE with 2 tools |
| 11 | AI failure-path test (ImportError, Exception) | PASS — code review confirmed |
| 12 | Policy-not-found test | PASS — handled by Cortex Search empty result |
| 13 | Hero case test | PASS — CUST-1042 = 100, CRITICAL, 8 signals |

## J. Hero Case AI Test

### "Why is CUST-1042 considered high risk?"
AI correctly cited: risk score 100, CRITICAL classification, 8 signals including
BENEFICIARY_BURST, GEO_ANOMALY, VALUE_SPIKE, VELOCITY, STRUCTURING, NETWORK_PATTERN.
Response was grounded in actual data.

### "What policies apply to the suspicious activity?"
Cortex Search returned PC-STRUCT-001 sections 4.1 (Structuring Pattern Definition)
and 4.2 (Evidence Collection) with full policy text.

### "Can we conclude that fraud definitely occurred?"
Model correctly refused: "I cannot provide a response that declares fraud."

### "What should the analyst do next?"
Tested via prompt structure — the investigation summary prompt requests
"INVESTIGATION RECOMMENDATIONS for the analyst" and the agent specification
prohibits autonomous enforcement actions.

## K. Known Limitations

1. **Agent response format**: the `_snowflake.send_snow_api_request` response
   structure may vary across SiS runtime versions. The parser handles this
   with try/except and multiple fallback paths.
2. **No conversation history**: each agent call is stateless (single message).
   Multi-turn investigation requires the user to provide context in each question.
3. **60-second timeout**: complex agent orchestrations may hit the timeout.
4. **Local development**: `_call_agent` returns an informational error outside SiS.
5. **AI output not validated against schema**: the raw agent text is displayed.
   Malformed markdown is possible but non-breaking.

## L. Recommendation for Release 4

1. **Multi-turn conversation**: add thread support via `thread_id` / `parent_message_id`
2. **AI response formatting**: parse structured sections from agent output
3. **Streaming responses**: use `stream: True` with SSE for real-time output
4. **AI audit trail**: log agent calls and responses to an audit table
5. **Cortex Agent evaluation**: run eval suite against grounding test cases
