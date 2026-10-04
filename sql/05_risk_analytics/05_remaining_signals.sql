-- BANKGUARD AI – M2 Signals 3-9 (remaining signal detectors)
-- Each signal follows the same pattern: baseline, observation, deviation, evidence.
-- See individual signal SQL in the executed M2 session for full CTEs.

-- Signal 3: BENEFICIARY_BURST – 2+ new beneficiaries in 30 days
-- Signal 4: GEO_ANOMALY – new countries (esp. high-risk) in recent transactions
-- Signal 5: DORMANT_ACTIVATION – dormant accounts suddenly active
-- Signal 6: VALUE_SPIKE – recent avg amount >> historical avg (3x+ deviation)
-- Signal 7: CHANNEL_ANOMALY – significant channel share shift (25%+)
-- Signal 8: NETWORK_PATTERN – shared bank+country destination across 3+ customers
-- Signal 9: MULTI_SIGNAL – 2+ concurrent primary signals on same customer

-- High-risk jurisdictions for GEO_ANOMALY: UAE, Nigeria, Panama, Cayman Islands, Hong Kong

-- All signals use:
--   SIGNAL_ID pattern: SIG-{TYPE_PREFIX}-{CUSTOMER_ID}
--   Severity: LOW (30pts) / MEDIUM (55pts) / HIGH (80pts) / CRITICAL (100pts)
--   Evidence: OBJECT_CONSTRUCT JSON with full metrics
--   Source: BANKGUARD_RAW.{source_table}
--   Rule version: M2-RISK-V1.0
