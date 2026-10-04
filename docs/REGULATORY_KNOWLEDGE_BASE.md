# BANKGUARD AI – Regulatory Knowledge Base

## IMPORTANT DISCLAIMER

**All policy content in this knowledge base is SYNTHETIC DEMONSTRATION CONTENT created
for the BANKGUARD AI hackathon project. It does not constitute actual legal, regulatory,
or compliance advice. Do not rely on this content for real banking compliance decisions.**

Every record carries `SOURCE_TYPE = 'SYNTHETIC_DEMO'`.

## Purpose

The regulatory knowledge base provides structured, versioned policy documents that connect
M2 risk signals to applicable compliance requirements. It enables the future Cortex Agent
(M4) to ground its explanations in specific policy citations rather than generic statements.

## Data Model

### BANKGUARD_REGULATORY Schema

| Object | Type | Purpose |
|---|---|---|
| `POLICIES` | Table | Policy versions with status, dates, ownership |
| `POLICY_SECTIONS` | Table | Chunked policy content with risk topics |
| `RISK_TOPIC_TAXONOMY` | Table | Controlled vocabulary for risk topics |
| `POLICY_RISK_MAPPING` | Table | Signal → policy section mappings |
| `POLICY_EVIDENCE_REQUIREMENTS` | Table | Evidence checklist per section |
| `V_RETRIEVAL_DOCUMENTS` | View | Search-ready documents for future Cortex Search |
| `V_SIGNAL_POLICY_CHAIN` | View | End-to-end signal → policy → evidence chain |
| `V_NEGATIVE_POLICY_GATE` | View | Validates that unmapped topics return NO_APPLICABLE_POLICY_FOUND |

## Policy Versioning

- Each policy has a `POLICY_ID` (e.g., `PC-STRUCT-001`) and `POLICY_VERSION` (e.g., `2.1`)
- Only one version per policy may be `ACTIVE` at a time
- Previous versions are `SUPERSEDED` with a `SUPERSEDED_DATE`
- All queries and mappings reference active versions only

## Risk Topic Taxonomy

12 controlled topics: VELOCITY, STRUCTURING, BENEFICIARY, GEOGRAPHY, DORMANCY,
TRANSACTION_VALUE, CHANNEL, NETWORK, MULTI_SIGNAL, KYC, INVESTIGATION, REGULATORY_REPORTING.

## Signal-to-Policy Mapping

Every M2 risk signal maps to at least one active policy section with a relevance classification:

| Relevance | Meaning |
|---|---|
| PRIMARY | Directly governs this signal type |
| SUPPORTING | Provides additional procedural guidance |
| CONTEXTUAL | Background context (e.g., KYC, reporting) |

## Negative Policy Gate

The `V_NEGATIVE_POLICY_GATE` view tests whether all detected signal types have policy
coverage. For unmapped topics (e.g., `CRYPTOCURRENCY`), it returns:

> `NO_APPLICABLE_POLICY_FOUND` — No policy covers this risk topic. Do not fabricate a policy connection.

This prevents the future AI from inventing policy citations.

## Evidence Requirements

Each policy section specifies what evidence an investigator should examine, including
the source table in BANKGUARD where that evidence resides. This creates a traceable chain:

```
CUSTOMER → RISK SIGNAL → POLICY SECTION → EVIDENCE REQUIREMENT → SOURCE TABLE
```

## Retrieval Representation

`V_RETRIEVAL_DOCUMENTS` provides search-ready documents with a `SEARCH_TEXT` field combining
policy title, section title, section text, control objective, and required action. This is
designed for future Cortex Search indexing.

## Limitations

- All content is synthetic and for demonstration only
- Policy language is inspired by common banking compliance themes but is not legally authoritative
- The knowledge base covers the 10 policy domains required for the hackathon demo
- Real deployment would require integration with the institution's actual policy management system
