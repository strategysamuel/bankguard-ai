-- BANKGUARD AI – M2 Signal 2: Transaction Structuring
-- Detects multiple transactions within a 48hr window at 80-100% of illustrative threshold.
-- IMPORTANT: This is synthetic demonstration logic, not a regulatory statement.

USE DATABASE BANKGUARD_DB;

INSERT INTO BANKGUARD_RISK.RISK_SIGNAL_EVIDENCE
WITH params AS (
    SELECT MAX(CASE WHEN PARAM_NAME='AMOUNT_THRESHOLD' THEN PARAM_VALUE END) AS threshold,
           MAX(CASE WHEN PARAM_NAME='PROXIMITY_LOW_PCT' THEN PARAM_VALUE END) AS prox_low,
           MAX(CASE WHEN PARAM_NAME='WINDOW_HOURS' THEN PARAM_VALUE END) AS win_hrs,
           MAX(CASE WHEN PARAM_NAME='LOW_COUNT' THEN PARAM_VALUE END) AS low_c,
           MAX(CASE WHEN PARAM_NAME='MEDIUM_COUNT' THEN PARAM_VALUE END) AS med_c,
           MAX(CASE WHEN PARAM_NAME='HIGH_COUNT' THEN PARAM_VALUE END) AS high_c,
           MAX(CASE WHEN PARAM_NAME='CRITICAL_AGGREGATE_RATIO' THEN PARAM_VALUE END) AS crit_agg
    FROM BANKGUARD_RISK.RISK_THRESHOLDS WHERE SIGNAL_TYPE='STRUCTURING'
),
struct_txns AS (
    SELECT t.CUSTOMER_ID, t.TRANSACTION_ID, t.AMOUNT, t.TRANSACTION_DATE
    FROM BANKGUARD_RAW.TRANSACTIONS t, params p
    WHERE t.AMOUNT >= p.threshold * p.prox_low AND t.AMOUNT < p.threshold
      AND t.TRANSACTION_TYPE IN ('DOMESTIC_TRANSFER','INTERNATIONAL_TRANSFER','ATM_WITHDRAWAL')
      AND t.TRANSACTION_DATE >= DATEADD('hour', -p.win_hrs::INT, CURRENT_TIMESTAMP())
),
cust_agg AS (
    SELECT CUSTOMER_ID, COUNT(*) AS struct_count, SUM(AMOUNT) AS agg_amount,
           ARRAY_AGG(TRANSACTION_ID) AS txn_ids,
           MIN(TRANSACTION_DATE) AS first_txn, MAX(TRANSACTION_DATE) AS last_txn
    FROM struct_txns GROUP BY CUSTOMER_ID
    HAVING COUNT(*) >= (SELECT low_c FROM params)
),
detected AS (
    SELECT c.*, p.threshold,
           CASE WHEN c.struct_count >= p.high_c AND c.agg_amount >= p.threshold * p.crit_agg THEN 'CRITICAL'
                WHEN c.struct_count >= p.high_c THEN 'HIGH'
                WHEN c.struct_count >= p.med_c THEN 'MEDIUM' ELSE 'LOW' END AS severity
    FROM cust_agg c, params p
)
SELECT 'SIG-STR-' || CUSTOMER_ID, CUSTOMER_ID, NULL, 'STRUCTURING', CURRENT_TIMESTAMP(),
    first_txn::DATE, last_txn::DATE, severity,
    CASE severity WHEN 'CRITICAL' THEN 100 WHEN 'HIGH' THEN 80 WHEN 'MEDIUM' THEN 55 ELSE 30 END,
    'Potential structuring pattern detected: ' || struct_count || ' transactions between INR ' ||
        ROUND(threshold * 0.80) || ' and INR ' || threshold::INT || ' within ' ||
        DATEDIFF('hour', first_txn, last_txn) || ' hours. Requires analyst review.',
    OBJECT_CONSTRUCT('illustrative_threshold', threshold, 'struct_txn_count', struct_count,
        'aggregate_amount', agg_amount, 'transaction_ids', txn_ids),
    'BANKGUARD_RAW.TRANSACTIONS', 'M2-RISK-V1.0'
FROM detected;
