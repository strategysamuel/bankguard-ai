# BANKGUARD AI – AI Governance

## Purpose

This document defines the governance principles that all AI-powered features in
BANKGUARD AI must follow. These rules apply to Cortex Agent behavior, LLM-generated
investigation reports, risk explanations, and any automated decision support.

## Core Principles

### 1. Deterministic Rules First

Risk scores and fraud signals are computed by deterministic SQL-based rules before
any LLM reasoning is invoked. AI augments analyst judgment; it does not replace
the rule engine.

### 2. Evidence-Grounded Reasoning

AI explanations must be grounded in data available within the BANKGUARD schemas.
The AI must cite specific transactions, risk scores, or policy references when
producing findings.

### 3. Policy Traceability

When a finding references a regulation or policy, the AI must identify:
- The policy name
- The policy version or effective date
- The relevant section or clause

Generic references such as "per AML regulations" without a specific citation are
not acceptable.

### 4. No Fabrication

The AI must never invent:
- Transactions that do not exist in the data
- Customers or accounts not present in the system
- Regulatory citations that cannot be verified
- Risk scores or findings not supported by evidence

If evidence is insufficient to support a conclusion, the AI must return:

> "Insufficient evidence to support this finding."

### 5. Human-in-the-Loop

The AI must not autonomously:
- Freeze or close bank accounts
- File Suspicious Activity Reports (SARs) or other regulatory reports
- Declare criminal activity
- Make any irreversible decision

All consequential actions require explicit human analyst approval.

### 6. Auditability

Every AI-generated finding must be logged to `BANKGUARD_AUDIT.AI_DECISION_LOG`
with:
- Timestamp
- Input query or trigger
- Evidence references (table, row identifiers)
- Model used
- Output text
- Confidence indicators (where applicable)

### 7. Synthetic Data Only

BANKGUARD AI operates exclusively on synthetic banking data. No real customer
information, financial transactions, or personal identifiers are used at any point.

## Implementation Checkpoints

| Phase | Governance Check                                           |
|-------|------------------------------------------------------------|
| M2    | Risk scores are deterministic and auditable                 |
| M3    | Policy references include name, version, and section        |
| M4    | Cortex Agent follows all governance rules; decisions logged  |
| M5    | Dashboard displays evidence alongside findings               |
| M6    | End-to-end audit trail validated                             |

## Escalation

If the AI cannot determine whether a finding is supported by evidence, it must:

1. State the limitation clearly.
2. Present whatever partial evidence is available.
3. Recommend human review.
4. Never present an uncertain conclusion as definitive.
