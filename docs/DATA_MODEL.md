# BANKGUARD AI – Data Model

## Overview

All data is synthetic. No real customer, transaction, or regulatory data is used.
Database: `BANKGUARD_DB` | Warehouse: `COMPUTE_WH` | 24 objects across 5 schemas.

## Schema Layout

### BANKGUARD_RAW – Source Tables (M1)

| Table                  | Rows    | Description                                    |
|------------------------|---------|------------------------------------------------|
| `CUSTOMERS`            | 1,001   | Synthetic customer profiles                    |
| `ACCOUNTS`             | 1,558   | Bank accounts linked to customers              |
| `BENEFICIARIES`        | 2,564   | Transaction beneficiary records                |
| `TRANSACTIONS`         | 95,607  | Financial transactions with metadata           |
| `FRAUD_ALERTS`         | 296     | System-generated fraud/AML alerts              |
| `INVESTIGATION_CASES`  | 151     | Investigation case records                     |
| `SCENARIO_METADATA`    | 9       | Risk scenario definitions for evaluation       |

### BANKGUARD_CORE – Enriched Models (M1–M2)

| Object                     | Type | Description                                    |
|----------------------------|------|------------------------------------------------|
| `V_CUSTOMER_360`           | View | Unified customer view with account summaries   |
| `V_TRANSACTION_ENRICHED`   | View | Transactions joined with customer/account data |

### BANKGUARD_RISK – Analytics (M2)

| Object                     | Type  | Rows | Description                                    |
|----------------------------|-------|------|------------------------------------------------|
| `RISK_THRESHOLDS`          | Table | 48   | Configurable detection thresholds (9 signal types) |
| `RISK_SIGNAL_WEIGHTS`      | Table | 9    | Composite score weights per signal type        |
| `RISK_SIGNAL_EVIDENCE`     | Table | 843  | Individual signal detections with evidence     |
| `CUSTOMER_RISK_SCORE`      | Table | 492  | Per-customer composite risk scores (0–100)     |
| `V_RISK_SCENARIO_EVALUATION` | View | — | Ground-truth detection rates by scenario       |

### BANKGUARD_REGULATORY – Knowledge Base (M3)

| Object                       | Type  | Rows | Description                                  |
|------------------------------|-------|------|----------------------------------------------|
| `POLICIES`                   | Table | 19   | Policy headers with versioning (ACTIVE/SUPERSEDED) |
| `POLICY_SECTIONS`            | Table | 23   | Policy section text for Cortex Search        |
| `POLICY_RISK_MAPPING`        | Table | 24   | Signal-type to policy-section linkage        |
| `POLICY_EVIDENCE_REQUIREMENTS` | Table | 27 | Required evidence per policy section         |
| `RISK_TOPIC_TAXONOMY`        | Table | 12   | Risk topic hierarchy                         |
| `V_RETRIEVAL_DOCUMENTS`      | View  | —    | Search-ready document view (23 sections)     |
| `V_SIGNAL_POLICY_CHAIN`      | View  | —    | Customer signal → policy section mapping     |
| `V_NEGATIVE_POLICY_GATE`     | View  | —    | Signals missing policy coverage              |

### BANKGUARD_AUDIT – Findings & Trail (M4)

| Object                     | Type  | Description                                    |
|----------------------------|-------|------------------------------------------------|
| `AI_DECISION_LOG`          | Table | Every AI interaction with evidence references  |
| `INVESTIGATION_FINDINGS`   | Table | Structured findings requiring analyst approval |

### Cortex AI Objects

| Object                     | Type           | Schema             | Description                          |
|----------------------------|----------------|--------------------|--------------------------------------|
| `POLICY_SEARCH_SERVICE`    | Cortex Search  | BANKGUARD_REGULATORY | Semantic search over 23 policy sections |
| `BANKGUARD_RISK_ANALYST`   | Semantic View  | BANKGUARD_CORE     | Text-to-SQL over 6 logical tables    |
| `BANKGUARD_AGENT`          | Cortex Agent   | BANKGUARD_CORE     | Orchestrator: Analyst + Search tools |

## Key Relationships

```text
CUSTOMERS ─1:N─ ACCOUNTS ─1:N─ TRANSACTIONS
     │                              │
     ├──── BENEFICIARIES ◄─────────┘
     │
     ├──── FRAUD_ALERTS
     │
     └──── INVESTIGATION_CASES
```

## Data Lineage

```text
RAW.CUSTOMERS ──────┐
RAW.ACCOUNTS ───────┤──► CORE.V_CUSTOMER_360
RAW.BENEFICIARIES ──┤
RAW.TRANSACTIONS ───┤──► CORE.V_TRANSACTION_ENRICHED
                    │
                    ▼
             RISK.RISK_SIGNAL_EVIDENCE  (9 signal detectors)
                    │
                    ▼
             RISK.CUSTOMER_RISK_SCORE   (composite 0-100)
                    │
                    ├──► REGULATORY.V_SIGNAL_POLICY_CHAIN
                    │
                    ▼
             AUDIT.AI_DECISION_LOG
             AUDIT.INVESTIGATION_FINDINGS
```

## Notes

- All tables use synthetic data only.
- Timestamps use `TIMESTAMP_NTZ` in UTC.
- Currency amounts use `NUMBER(18,2)`.
- 9 risk signal types: VELOCITY, STRUCTURING, BENEFICIARY_BURST, GEO_ANOMALY, DORMANT_ACTIVATION, VALUE_SPIKE, CHANNEL_ANOMALY, NETWORK_PATTERN, MULTI_SIGNAL.
