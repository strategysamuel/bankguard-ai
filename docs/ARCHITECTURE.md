# BANKGUARD AI – Architecture

## Overview

BANKGUARD AI is a Snowflake-first banking risk intelligence application. All data
storage, transformation, risk analytics, regulatory knowledge, and AI reasoning
run inside Snowflake. The analyst interface is a Streamlit-in-Snowflake application.

## High-Level Architecture

```text
┌─────────────────────────────────────────────────────┐
│                   Streamlit Dashboard                │
│          (Analyst / Compliance / Audit UI)           │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               Cortex Agent (M4)                      │
│   Evidence-grounded reasoning · Policy lookup        │
│   Investigation reports · Natural-language queries    │
└──────┬──────────┬──────────┬───────────┬────────────┘
       │          │          │           │
┌──────▼───┐ ┌───▼────┐ ┌──▼────────┐ ┌▼───────────┐
│  RISK    │ │ CORE   │ │REGULATORY │ │   AUDIT    │
│ Scoring  │ │ Models │ │ Knowledge │ │   Trail    │
│ Fraud    │ │ Clean  │ │ Policies  │ │ Findings   │
│ AML      │ │ Enrich │ │ Search    │ │ Decisions  │
└──────┬───┘ └───┬────┘ └──────────┘ └────────────┘
       │         │
┌──────▼─────────▼────────────────────────────────────┐
│                    RAW Schema                        │
│   Synthetic transactions · Accounts · Customers      │
│   Alerts · Watchlists                                │
└─────────────────────────────────────────────────────┘
```

## Snowflake Objects

| Schema               | Purpose                                          |
|----------------------|--------------------------------------------------|
| `BANKGUARD_RAW`      | Ingested synthetic data (transactions, accounts)  |
| `BANKGUARD_CORE`     | Cleansed, enriched, joined data models            |
| `BANKGUARD_RISK`     | Risk scores, fraud signals, AML analytics         |
| `BANKGUARD_REGULATORY` | Policies, regulations, Cortex Search service    |
| `BANKGUARD_AUDIT`    | Investigation findings, AI decision log, reports  |

**Database:** `BANKGUARD_DB`  
**Warehouse:** `COMPUTE_WH`

## Data Flow

1. **RAW** – Synthetic data is generated and loaded into raw tables.
2. **CORE** – Views and tables cleanse, enrich, and join raw data.
3. **RISK** – Deterministic rules compute risk scores and fraud signals.
4. **REGULATORY** – Policy documents are ingested for Cortex Search.
5. **AUDIT** – AI findings, analyst decisions, and audit trails are recorded.

## AI Architecture

- **Deterministic rules first:** Risk scores and fraud flags are computed by
  SQL-based rules before any LLM is involved.
- **Cortex Search:** Regulatory policies are indexed for retrieval-augmented
  generation.
- **Cortex Agent:** Accepts analyst queries, retrieves evidence from RISK/CORE
  schemas, grounds responses in policy via Cortex Search, and produces
  structured investigation reports.
- **Human-in-the-loop:** Consequential actions require analyst confirmation.

## Technology Stack

| Component         | Technology                        |
|-------------------|-----------------------------------|
| Data storage      | Snowflake (BANKGUARD_DB)          |
| Compute           | COMPUTE_WH                        |
| Risk engine       | Snowflake SQL (9 signal detectors)|
| Regulatory search | Cortex Search Service             |
| Text-to-SQL       | Cortex Analyst + Semantic View    |
| AI orchestration  | Cortex Agent (Analyst + Search)   |
| Dashboard         | Streamlit in Snowflake            |
| Orchestration     | Snowflake CoCo CLI                |

## Data Volumes

| Category            | Count   |
|---------------------|---------|
| Customers           | 1,001   |
| Accounts            | 1,558   |
| Beneficiaries       | 2,564   |
| Transactions        | 95,607  |
| Risk signals        | 843     |
| Scored customers    | 492     |
| Policy sections     | 23      |
| Investigation cases | 151     |
