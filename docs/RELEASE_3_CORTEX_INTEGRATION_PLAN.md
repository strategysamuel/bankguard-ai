# Release 3 — Cortex AI Integration Plan

## Existing Cortex Objects

| Object | FQN | Type | Status |
|---|---|---|---|
| Cortex Agent | `BANKGUARD_DB.BANKGUARD_CORE.BANKGUARD_AGENT` | Agent | ACTIVE |
| Semantic View | `BANKGUARD_DB.BANKGUARD_CORE.BANKGUARD_RISK_ANALYST` | Semantic View | ACTIVE |
| Cortex Search | `BANKGUARD_DB.BANKGUARD_REGULATORY.POLICY_SEARCH_SERVICE` | Search Service | ACTIVE |

## Agent Configuration

- **Model**: auto (Snowflake-selected)
- **Tools**: RiskAnalyst (cortex_analyst_text_to_sql), PolicySearch (cortex_search)
- **Budget**: 60 seconds, 32000 tokens
- **Governance**: "Never declare fraud. Use potential pattern or requires analyst review."

## Semantic View Tables

| Alias | Base Table | Purpose |
|---|---|---|
| CUSTOMERS | V_CUSTOMER_360 | Customer profiles |
| RISK_SCORES | CUSTOMER_RISK_SCORE | Composite risk scores 0-100 |
| RISK_SIGNALS | RISK_SIGNAL_EVIDENCE | Individual signal evidence |
| TRANSACTIONS | V_TRANSACTION_ENRICHED | Enriched transactions |
| CASES | INVESTIGATION_CASES | Cases with status/priority |
| ALERTS | FRAUD_ALERTS | Fraud/AML alerts |

## Integration Approach

### API Call Pattern (SiS-native)
```python
import _snowflake
resp = _snowflake.send_snow_api_request(
    "POST",
    "/api/v2/databases/BANKGUARD_DB/schemas/BANKGUARD_CORE/agents/BANKGUARD_AGENT:run",
    {}, {},
    json.dumps({"messages": [...], "stream": False}),
    {}, 30000
)
```

Uses `_snowflake` module (available in SiS container runtime) — no external auth needed.

### Performance Control
- AI calls only on explicit button press (not on rerun)
- Results cached in `st.session_state` per customer/case
- No automatic Cortex calls on dropdown changes

### Error Handling
- try/except around all `_snowflake.send_snow_api_request` calls
- Graceful fallback: "AI investigation service is temporarily unavailable."
- Existing dashboard functionality continues regardless of AI status

### SiS Constraints
- `_snowflake` module only available inside SiS runtime
- Non-streaming responses (stream: False) for simpler parsing
- 30-second timeout per agent call
