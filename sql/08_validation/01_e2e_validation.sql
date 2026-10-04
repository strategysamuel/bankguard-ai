-- ==========================================================================
-- BANKGUARD AI – End-to-End Validation (M6)
-- Run this script to verify the full pipeline is healthy.
-- All assertions return PASS/FAIL with diagnostic context.
-- ==========================================================================

USE DATABASE BANKGUARD_DB;

-- --------------------------------------------------------------------------
-- 1. Schema object counts
-- --------------------------------------------------------------------------
SELECT 'SCHEMA_OBJECTS' AS TEST,
       CASE WHEN COUNT(*) = 24 THEN 'PASS' ELSE 'FAIL' END AS RESULT,
       COUNT(*) || ' objects (expected 24)' AS DETAIL
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA LIKE 'BANKGUARD_%';

-- --------------------------------------------------------------------------
-- 2. RAW data volumes
-- --------------------------------------------------------------------------
SELECT 'RAW_CUSTOMERS' AS TEST,
       CASE WHEN COUNT(*) >= 1000 THEN 'PASS' ELSE 'FAIL' END AS RESULT,
       COUNT(*) || ' rows' AS DETAIL
FROM BANKGUARD_RAW.CUSTOMERS;

SELECT 'RAW_TRANSACTIONS' AS TEST,
       CASE WHEN COUNT(*) >= 90000 THEN 'PASS' ELSE 'FAIL' END AS RESULT,
       COUNT(*) || ' rows' AS DETAIL
FROM BANKGUARD_RAW.TRANSACTIONS;

-- --------------------------------------------------------------------------
-- 3. Risk engine output
-- --------------------------------------------------------------------------
SELECT 'RISK_SIGNALS' AS TEST,
       CASE WHEN COUNT(*) >= 800 THEN 'PASS' ELSE 'FAIL' END AS RESULT,
       COUNT(*) || ' signals detected' AS DETAIL
FROM BANKGUARD_RISK.RISK_SIGNAL_EVIDENCE;

SELECT 'RISK_SCORED_CUSTOMERS' AS TEST,
       CASE WHEN COUNT(*) >= 400 THEN 'PASS' ELSE 'FAIL' END AS RESULT,
       COUNT(*) || ' customers scored' AS DETAIL
FROM BANKGUARD_RISK.CUSTOMER_RISK_SCORE;

-- --------------------------------------------------------------------------
-- 4. Hero case CUST-1042
-- --------------------------------------------------------------------------
SELECT 'HERO_RISK_SCORE' AS TEST,
       CASE WHEN RISK_SCORE >= 95 AND RISK_CLASS = 'CRITICAL' THEN 'PASS' ELSE 'FAIL' END AS RESULT,
       'Score=' || RISK_SCORE || ' Class=' || RISK_CLASS || ' Signals=' || SIGNAL_COUNT AS DETAIL
FROM BANKGUARD_RISK.CUSTOMER_RISK_SCORE
WHERE CUSTOMER_ID = 'CUST-1042';

SELECT 'HERO_SIGNAL_COUNT' AS TEST,
       CASE WHEN COUNT(*) >= 7 THEN 'PASS' ELSE 'FAIL' END AS RESULT,
       COUNT(*) || ' signals (expected >=7)' AS DETAIL
FROM BANKGUARD_RISK.RISK_SIGNAL_EVIDENCE
WHERE CUSTOMER_ID = 'CUST-1042';

SELECT 'HERO_POLICY_CHAIN' AS TEST,
       CASE WHEN COUNT(*) >= 20 THEN 'PASS' ELSE 'FAIL' END AS RESULT,
       COUNT(*) || ' policy mappings (expected >=20)' AS DETAIL
FROM BANKGUARD_REGULATORY.V_SIGNAL_POLICY_CHAIN
WHERE CUSTOMER_ID = 'CUST-1042';

-- --------------------------------------------------------------------------
-- 5. Scenario detection rates (all 9 should be 100%)
-- --------------------------------------------------------------------------
SELECT 'SCENARIO_DETECTION' AS TEST,
       CASE WHEN MIN(DETECTION_RATE_PCT) = 100 THEN 'PASS' ELSE 'FAIL' END AS RESULT,
       'Min detection=' || MIN(DETECTION_RATE_PCT) || '% across ' || COUNT(*) || ' scenarios' AS DETAIL
FROM BANKGUARD_RISK.V_RISK_SCENARIO_EVALUATION;

-- --------------------------------------------------------------------------
-- 6. Regulatory knowledge base
-- --------------------------------------------------------------------------
SELECT 'ACTIVE_POLICIES' AS TEST,
       CASE WHEN COUNT(*) >= 10 THEN 'PASS' ELSE 'FAIL' END AS RESULT,
       COUNT(*) || ' active policies' AS DETAIL
FROM BANKGUARD_REGULATORY.POLICIES
WHERE STATUS = 'ACTIVE';

SELECT 'POLICY_SECTIONS' AS TEST,
       CASE WHEN COUNT(*) >= 20 THEN 'PASS' ELSE 'FAIL' END AS RESULT,
       COUNT(*) || ' policy sections indexed' AS DETAIL
FROM BANKGUARD_REGULATORY.POLICY_SECTIONS;

SELECT 'NEGATIVE_GATE' AS TEST,
       CASE WHEN COUNT(*) >= 1 THEN 'PASS' ELSE 'FAIL' END AS RESULT,
       COUNT(*) || ' signals without policy coverage' AS DETAIL
FROM BANKGUARD_REGULATORY.V_NEGATIVE_POLICY_GATE;

-- --------------------------------------------------------------------------
-- 7. Core views are queryable
-- --------------------------------------------------------------------------
SELECT 'CORE_CUSTOMER_360' AS TEST,
       CASE WHEN COUNT(*) >= 1000 THEN 'PASS' ELSE 'FAIL' END AS RESULT,
       COUNT(*) || ' rows' AS DETAIL
FROM BANKGUARD_CORE.V_CUSTOMER_360;

SELECT 'CORE_TXN_ENRICHED' AS TEST,
       CASE WHEN COUNT(*) >= 90000 THEN 'PASS' ELSE 'FAIL' END AS RESULT,
       COUNT(*) || ' rows' AS DETAIL
FROM BANKGUARD_CORE.V_TRANSACTION_ENRICHED;

-- --------------------------------------------------------------------------
-- 8. Audit tables exist and are accessible
-- --------------------------------------------------------------------------
SELECT 'AUDIT_TABLES' AS TEST,
       CASE WHEN COUNT(*) = 2 THEN 'PASS' ELSE 'FAIL' END AS RESULT,
       COUNT(*) || ' audit tables' AS DETAIL
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'BANKGUARD_AUDIT' AND TABLE_TYPE = 'BASE TABLE';

-- --------------------------------------------------------------------------
-- 9. No future-dated transactions
-- --------------------------------------------------------------------------
SELECT 'NO_FUTURE_DATES' AS TEST,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS RESULT,
       COUNT(*) || ' future-dated transactions' AS DETAIL
FROM BANKGUARD_RAW.TRANSACTIONS
WHERE TRANSACTION_DATE > CURRENT_TIMESTAMP();

-- --------------------------------------------------------------------------
-- Summary
-- --------------------------------------------------------------------------
SELECT 'VALIDATION_COMPLETE' AS TEST, 'DONE' AS RESULT,
       '14 checks executed' AS DETAIL;
