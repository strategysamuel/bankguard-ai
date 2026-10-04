# BANKGUARD AI – Data Model

## Overview

All data is synthetic. No real customer, transaction, or regulatory data is used.

## Schema Layout

### BANKGUARD_RAW – Source Tables (M1)

| Table                | Description                                    |
|----------------------|------------------------------------------------|
| `CUSTOMERS`          | Synthetic customer profiles                    |
| `ACCOUNTS`           | Bank accounts linked to customers              |
| `TRANSACTIONS`       | Financial transactions with metadata           |
| `ALERTS`             | System-generated fraud/AML alerts              |
| `WATCHLIST_ENTRIES`   | Sanctions and PEP watchlist entries            |

### BANKGUARD_CORE – Enriched Models (M1–M2)

| Object               | Description                                   |
|-----------------------|-----------------------------------------------|
| `V_CUSTOMER_360`     | Unified customer view with account summaries   |
| `V_TRANSACTION_ENRICHED` | Transactions joined with customer/account context |

### BANKGUARD_RISK – Analytics (M2)

| Object               | Description                                   |
|-----------------------|-----------------------------------------------|
| `RISK_SCORES`        | Per-customer composite risk scores             |
| `FRAUD_SIGNALS`      | Detected fraud patterns and signals            |
| `AML_INDICATORS`     | AML-specific indicators (structuring, velocity)|
| `V_HIGH_RISK_SUMMARY`| View of customers above risk threshold         |

### BANKGUARD_REGULATORY – Knowledge Base (M3)

| Object               | Description                                   |
|-----------------------|-----------------------------------------------|
| `POLICIES`           | Regulatory policy documents (text chunks)      |
| `POLICY_METADATA`    | Policy name, version, effective date, category |

### BANKGUARD_AUDIT – Findings & Trail (M4–M5)

| Object               | Description                                   |
|-----------------------|-----------------------------------------------|
| `INVESTIGATION_FINDINGS` | AI-generated investigation reports          |
| `AI_DECISION_LOG`    | Every AI inference with input/output/evidence  |
| `ANALYST_ACTIONS`    | Human analyst decisions and overrides          |

## Key Relationships

```text
CUSTOMERS ─1:N─ ACCOUNTS ─1:N─ TRANSACTIONS
     │                              │
     └──── ALERTS ◄────────────────┘
     │
     └──── WATCHLIST_ENTRIES
```

## Data Lineage

```text
RAW.CUSTOMERS ──┐
RAW.ACCOUNTS ───┤──► CORE.V_CUSTOMER_360
RAW.TRANSACTIONS┤──► CORE.V_TRANSACTION_ENRICHED
                │         │
                │         ▼
                └──► RISK.RISK_SCORES
                     RISK.FRAUD_SIGNALS
                     RISK.AML_INDICATORS
                              │
                              ▼
                     AUDIT.INVESTIGATION_FINDINGS
                     AUDIT.AI_DECISION_LOG
```

## Notes

- Exact column definitions will be finalized during M1 (Synthetic Data).
- All tables use synthetic data only.
- Timestamps use `TIMESTAMP_NTZ` in UTC.
- Currency amounts use `NUMBER(18,2)`.
