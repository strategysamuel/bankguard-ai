# BANKGUARD AI – AI Investigation Engine (M4)

## Overview

M4 connects the M2 risk engine and M3 regulatory knowledge base into an AI-powered
investigation workflow using Cortex Agent, Cortex Analyst, and Cortex Search.

## Architecture

```text
Analyst Query
      |
      v
BANKGUARD_AGENT (Cortex Agent)
      |
      +-- RiskAnalyst (Cortex Analyst)
      |     |
      |     +-- BANKGUARD_RISK_ANALYST (Semantic View)
      |           |
      |           +-- V_CUSTOMER_360
      |           +-- CUSTOMER_RISK_SCORE
      |           +-- RISK_SIGNAL_EVIDENCE
      |           +-- V_TRANSACTION_ENRICHED
      |           +-- FRAUD_ALERTS
      |           +-- INVESTIGATION_CASES
      |
      +-- PolicySearch (Cortex Search)
            |
            +-- POLICY_SEARCH_SERVICE
                  |
                  +-- V_RETRIEVAL_DOCUMENTS (23 policy sections)
```

## Components

### Cortex Search Service (`POLICY_SEARCH_SERVICE`)
- Indexes 23 active policy sections from `V_RETRIEVAL_DOCUMENTS`
- Searchable text: policy title, section text, control objectives
- Filterable attributes: POLICY_DOMAIN, RISK_TOPIC, STATUS, SOURCE_TYPE
- TARGET_LAG: 1 day

### Semantic View (`BANKGUARD_RISK_ANALYST`)
- 6 logical tables covering customers, risk scores, signals, transactions, alerts, cases
- 17 dimensions, 7 facts, 6 metrics
- Relationships linking all tables via CUSTOMER_ID
- AI SQL generation instructions encode governance rules

### Cortex Agent (`BANKGUARD_AGENT`)
- Two tools: RiskAnalyst (structured data) + PolicySearch (unstructured policy)
- Governance instructions embedded in agent specification
- Sample questions for onboarding

### Audit Tables (`BANKGUARD_AUDIT`)
- `AI_DECISION_LOG`: Logs every agent interaction with evidence refs and citations
- `INVESTIGATION_FINDINGS`: Structured findings requiring human analyst approval

## Governance

The agent instructions enforce:
1. Synthetic data disclaimer in every response
2. "Potential pattern" / "requires analyst review" language
3. Policy citations in `[PC-XXX-001 vX.X, Section X.X]` format
4. No automated account freezing or regulatory filing
5. "Insufficient evidence" when data doesn't support a conclusion
6. No fabrication of transactions, signals, or policies

## Testing

- **Cortex Search**: Verified via `DATA_AGENT_RUN` (search-only) — returns correct policy sections
- **Cortex Analyst**: Verified via `cortex analyst query` CLI — generates correct SQL
- **Hero Case**: CUST-1042 risk score (100/CRITICAL), 8 signals, 22 policy mappings all verified

## Known Limitation

`DATA_AGENT_RUN` with the combined agent (Analyst + Search) returns a warehouse resolution
error in the CoCo CLI SQL session context. Both tools work individually. The agent is fully
functional when invoked via Snowsight Agent Playground or the REST API where the user's
default warehouse is resolved directly.
