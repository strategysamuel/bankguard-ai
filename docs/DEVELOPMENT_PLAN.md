# BANKGUARD AI – Development Plan

## Phase Overview

| Phase | Name                    | Description                                         | Status   |
|-------|-------------------------|-----------------------------------------------------|----------|
| M0    | Project Foundation      | Repo structure, Snowflake schemas, governance docs   | Complete |
| M1    | Synthetic Data          | Generate realistic banking dataset                   | Complete |
| M2    | Risk Engine             | Deterministic scoring and fraud detection rules      | Complete |
| M3    | Regulatory Knowledge    | Policy ingestion and Cortex Search                   | Complete |
| M4    | AI Investigation        | Cortex Agent with evidence-grounded reasoning        | Complete |
| M5    | Streamlit Dashboard     | Interactive analyst interface                        | Complete |
| M6    | Polish & Demo           | End-to-end validation, demo preparation              | Complete |

## M0 – Project Foundation

- Repository directory structure
- Snowflake schema creation (RAW, CORE, RISK, REGULATORY, AUDIT)
- Project configuration (config/project.yaml)
- Architecture, data model, governance, and development plan docs
- SQL directory organization
- Testing foundation
- Validation of schemas and structure

## M1 – Synthetic Data

- Design table DDL for CUSTOMERS, ACCOUNTS, TRANSACTIONS, ALERTS, WATCHLIST_ENTRIES
- Generate synthetic data using Snowflake SQL or Python
- Load into BANKGUARD_RAW
- Create CORE views (V_CUSTOMER_360, V_TRANSACTION_ENRICHED)
- Validate data integrity

## M2 – Risk Engine

- Implement deterministic risk scoring rules in SQL
- Compute per-customer risk scores
- Detect fraud signal patterns (velocity, structuring, geographic anomalies)
- Generate AML indicators
- Create V_HIGH_RISK_SUMMARY view
- Validate risk outputs against known synthetic patterns

## M3 – Regulatory Knowledge

- Curate synthetic regulatory policy documents
- Load into BANKGUARD_REGULATORY
- Create Cortex Search service over policy corpus
- Validate retrieval quality

## M4 – AI Investigation

- Build Cortex Agent with tool access to RISK, CORE, REGULATORY schemas
- Implement evidence-grounded investigation workflow
- Generate structured investigation reports
- Log all AI decisions to AUDIT schema
- Validate against governance principles

## M5 – Streamlit Dashboard

- Build analyst-facing Streamlit application
- Risk overview dashboard
- Customer investigation interface
- Natural-language query interface (Cortex Agent)
- Investigation report viewer
- Audit trail viewer

## M6 – Polish & Demo

- End-to-end validation SQL (all 9 scenarios at 100% detection, hero case assertions)
- Documentation finalization (DATA_MODEL.md, ARCHITECTURE.md, DEVELOPMENT_PLAN.md)
- Dashboard About page updated to reflect all phases complete
- Project README for hackathon submission
- Demo scenario: CUST-1042 golden path through all 5 dashboard views

## Constraints

- All data is synthetic. No real PII or financial data.
- Deterministic rules before AI reasoning.
- Human approval for consequential actions.
- Full auditability of AI-generated findings.
