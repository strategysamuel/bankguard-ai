# BANKGUARD AI

**Risk, Fraud & Regulatory Intelligence Copilot**

> From suspicious signal to evidence-backed, policy-grounded, audit-ready decision.

Built for the **Snowflake CoCo CLI Hackathon – GCC Edition** (hack2skill).

---

## What It Does

BANKGUARD AI is an AI-powered copilot that helps banking compliance officers, fraud analysts, and risk managers investigate suspicious activity. It connects:

**Signal → Evidence → Finding → Policy Context → Recommended Action**

All data is **synthetic**. No real customer information or financial transactions are used.

## Architecture

```text
┌─────────────────────────────────────────────────────┐
│               Streamlit Dashboard (M5)               │
│    Risk Overview · Investigation · Policy · Cases    │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Cortex Agent (M4)                        │
│   Cortex Analyst (text-to-SQL) + Cortex Search       │
└──────┬──────────┬──────────┬───────────┬────────────┘
       │          │          │           │
┌──────▼───┐ ┌───▼────┐ ┌──▼────────┐ ┌▼───────────┐
│  RISK    │ │ CORE   │ │REGULATORY │ │   AUDIT    │
│ 9 signal │ │ 360°   │ │ 10 active │ │ Decision   │
│ detectors│ │ views  │ │ policies  │ │ log        │
└──────────┘ └────────┘ └───────────┘ └────────────┘
       │          │
┌──────▼──────────▼────────────────────────────────────┐
│               RAW Schema (M1)                         │
│  1,001 customers · 95,607 transactions · synthetic    │
└──────────────────────────────────────────────────────┘
```

## Key Features

| Feature | Implementation |
|---------|---------------|
| **Deterministic Risk Scoring** | 9 SQL signal detectors with configurable thresholds, weighted composite scoring (0–100) |
| **Regulatory Policy Grounding** | 10 active policies, 23 sections indexed in Cortex Search, signal-to-policy traceability |
| **AI Investigation** | Cortex Agent orchestrates structured data queries (Analyst) and policy retrieval (Search) |
| **Interactive Dashboard** | 5-view Streamlit-in-Snowflake app: Risk Overview, Customer Investigation, Policy Lookup, Case Management, About |
| **Evidence-First Governance** | No fabrication, human-in-the-loop, policy citations required, full audit trail |

## Risk Signal Types

| # | Signal | Description |
|---|--------|-------------|
| 1 | VELOCITY | Abnormal transaction frequency |
| 2 | STRUCTURING | Amounts clustered below reporting thresholds |
| 3 | BENEFICIARY_BURST | Spike in new beneficiary additions |
| 4 | GEO_ANOMALY | Transactions to new/high-risk countries |
| 5 | DORMANT_ACTIVATION | Sudden activity on previously dormant accounts |
| 6 | VALUE_SPIKE | Transaction amounts far above historical norm |
| 7 | CHANNEL_ANOMALY | Unusual shift in transaction channel usage |
| 8 | NETWORK_PATTERN | Shared destination patterns across customers |
| 9 | MULTI_SIGNAL | Concentration of multiple concurrent signals |

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Database | Snowflake (`BANKGUARD_DB`, 5 schemas, 24 objects) |
| Risk Engine | Snowflake SQL (deterministic rules) |
| Policy Search | Cortex Search Service |
| Text-to-SQL | Cortex Analyst + Semantic View |
| AI Orchestration | Cortex Agent |
| Dashboard | Streamlit in Snowflake |
| Build Tool | Snowflake CoCo CLI |

## Demo: Hero Case CUST-1042

The end-to-end demonstration scenario:

1. **Risk Overview** → CUST-1042 appears in the CRITICAL customers table (score: 100/100)
2. **Customer Investigation** → Enter `CUST-1042` to see 8 detected signals with evidence
3. **Policy Lookup** → Search "transaction structuring threshold" to see applicable regulatory sections
4. **Case Management** → CASE-FG-1042 shows as CRITICAL priority, assigned to an analyst

## Deployment

### Prerequisites
- Snowflake account with `ACCOUNTADMIN` role
- Snowflake CoCo CLI or SnowSQL
- `COMPUTE_WH` warehouse

### Setup

Run the SQL scripts in order:

```
sql/01_setup/create_schemas.sql        -- Create BANKGUARD_DB and 5 schemas
sql/02_tables/01_raw_tables.sql        -- Create 7 RAW tables
sql/03_views/01_core_views.sql         -- Create CORE views
sql/04_seed/01_seed_customers_accounts.sql  -- Generate customers, accounts, beneficiaries
sql/04_seed/02_seed_transactions.sql        -- Generate 95K transactions
sql/04_seed/03_seed_hero_case.sql           -- Create CUST-1042 hero case data
sql/04_seed/04_seed_alerts_cases.sql        -- Generate alerts and cases
sql/05_risk_analytics/01_risk_parameters.sql -- Load thresholds and weights
sql/05_risk_analytics/02_evidence_tables.sql -- Create risk signal tables
sql/05_risk_analytics/03_velocity.sql        -- Signal 1: velocity detector
sql/05_risk_analytics/04_structuring.sql     -- Signal 2: structuring detector
sql/05_risk_analytics/05_remaining_signals.sql -- Signals 3-9
sql/05_risk_analytics/11_customer_risk_score.sql -- Composite scoring
sql/06_regulatory/01_policy_tables.sql       -- Regulatory tables
sql/06_regulatory/02_policy_seed_data.sql    -- Load 10 policies, 23 sections
sql/06_regulatory/07_retrieval_views.sql     -- Search and chain views
sql/06_regulatory/10_cortex_search_service.sql -- Create Cortex Search Service
sql/07_audit_reporting/01_audit_tables.sql   -- Audit tables
sql/07_audit_reporting/02_cortex_agent.sql   -- Create Cortex Agent
```

### Deploy Dashboard

```bash
snow streamlit deploy --replace
```

### Validate

```
sql/08_validation/01_e2e_validation.sql  -- 14 assertions: all should return PASS
```

## Project Structure

```
bankguard-ai/
├── PROJECT_BIBLE.md           # Authoritative project specification
├── README.md                  # This file
├── snowflake.yml              # SiS deployment manifest
├── config/project.yaml        # Project configuration
├── docs/
│   ├── ARCHITECTURE.md        # System architecture
│   ├── DATA_MODEL.md          # Data model (24 objects)
│   ├── DEVELOPMENT_PLAN.md    # M0–M6 phase plan
│   ├── AI_GOVERNANCE.md       # AI governance principles
│   ├── AI_INVESTIGATION_ENGINE.md  # M4 component docs
│   └── REGULATORY_KNOWLEDGE_BASE.md  # M3 policy docs
├── sql/
│   ├── 01_setup/              # Schema creation
│   ├── 02_tables/             # Table DDL
│   ├── 03_views/              # Core views
│   ├── 04_seed/               # Synthetic data generation
│   ├── 05_risk_analytics/     # Risk engine (9 detectors + scoring)
│   ├── 06_regulatory/         # Policy KB + Cortex Search
│   ├── 07_audit_reporting/    # Audit tables + Cortex Agent
│   └── 08_validation/         # E2E validation
├── streamlit/
│   ├── app.py                 # Dashboard (418 lines, 5 views)
│   └── environment.yml        # SiS dependencies
└── tests/                     # Validation scripts
```

## Governance Principles

1. **Deterministic rules first** — Risk scores are computed by SQL rules before any LLM reasoning
2. **Evidence-grounded** — Every finding cites specific transactions, signals, and policies
3. **Human-in-the-loop** — No automated account freezing, regulatory filing, or irreversible actions
4. **Auditable** — Every AI interaction logged with evidence references
5. **No fabrication** — If evidence is insufficient: "Insufficient evidence to support this finding"
6. **Synthetic data only** — No real customer data at any point

## Known Limitations

- The combined Cortex Agent (Analyst + Search) has a warehouse resolution issue in CoCo CLI SQL sessions (error 391920). Both tools work individually. The agent is fully functional in Snowsight or via REST API.
- All data is synthetic and for demonstration purposes only.

## Development Phases

| Phase | Description | Commit |
|-------|-------------|--------|
| M0 | Project Foundation | `0151342` |
| M2 | Deterministic Risk Engine | `4a81d70` |
| M4 | AI Investigation Engine | `5299ce6` |
| M5 | Streamlit Dashboard | `7fa5d4e` |
| M6 | Polish & Demo | Current |

---

Built entirely with [Snowflake CoCo CLI](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code).
