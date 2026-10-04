-- BANKGUARD AI – M2 Signal 1: Transaction Velocity Anomaly
-- Compares recent 7-day transaction count vs historical daily rate.
-- Thresholds read from RISK_THRESHOLDS.

USE DATABASE BANKGUARD_DB;

INSERT INTO BANKGUARD_RISK.RISK_SIGNAL_EVIDENCE
WITH params AS (
    SELECT MAX(CASE WHEN PARAM_NAME='OBSERVATION_DAYS' THEN PARAM_VALUE END) AS obs_d,
           MAX(CASE WHEN PARAM_NAME='BASELINE_DAYS' THEN PARAM_VALUE END) AS base_d,
           MAX(CASE WHEN PARAM_NAME='MIN_BASELINE_TXNS' THEN PARAM_VALUE END) AS min_txns,
           MAX(CASE WHEN PARAM_NAME='LOW_RATIO' THEN PARAM_VALUE END) AS low_r,
           MAX(CASE WHEN PARAM_NAME='CRITICAL_RATIO' THEN PARAM_VALUE END) AS crit_r,
           MAX(CASE WHEN PARAM_NAME='HIGH_RATIO' THEN PARAM_VALUE END) AS high_r,
           MAX(CASE WHEN PARAM_NAME='MEDIUM_RATIO' THEN PARAM_VALUE END) AS med_r
    FROM BANKGUARD_RISK.RISK_THRESHOLDS WHERE SIGNAL_TYPE='VELOCITY'
),
baseline AS (
    SELECT t.CUSTOMER_ID, COUNT(*) AS base_txn_count,
           COUNT(*) / GREATEST(DATEDIFF('day',
               DATEADD('day', -(SELECT base_d FROM params)::INT, CURRENT_DATE()),
               DATEADD('day', -(SELECT obs_d FROM params)::INT, CURRENT_DATE())), 1.0)
           * (SELECT obs_d FROM params) AS expected_in_obs
    FROM BANKGUARD_RAW.TRANSACTIONS t
    WHERE t.TRANSACTION_DATE >= DATEADD('day', -(SELECT base_d FROM params)::INT, CURRENT_DATE())
      AND t.TRANSACTION_DATE < DATEADD('day', -(SELECT obs_d FROM params)::INT, CURRENT_DATE())
    GROUP BY t.CUSTOMER_ID
    HAVING COUNT(*) >= (SELECT min_txns FROM params)
),
observation AS (
    SELECT CUSTOMER_ID, COUNT(*) AS obs_count
    FROM BANKGUARD_RAW.TRANSACTIONS
    WHERE TRANSACTION_DATE >= DATEADD('day', -(SELECT obs_d FROM params)::INT, CURRENT_DATE())
    GROUP BY CUSTOMER_ID
),
detected AS (
    SELECT o.CUSTOMER_ID, b.base_txn_count, ROUND(b.expected_in_obs, 2) AS expected_count,
           o.obs_count, ROUND(o.obs_count / GREATEST(b.expected_in_obs, 0.1), 2) AS deviation_ratio,
           CASE
               WHEN o.obs_count / GREATEST(b.expected_in_obs, 0.1) >= (SELECT crit_r FROM params) THEN 'CRITICAL'
               WHEN o.obs_count / GREATEST(b.expected_in_obs, 0.1) >= (SELECT high_r FROM params) THEN 'HIGH'
               WHEN o.obs_count / GREATEST(b.expected_in_obs, 0.1) >= (SELECT med_r FROM params) THEN 'MEDIUM'
               ELSE 'LOW'
           END AS severity
    FROM observation o JOIN baseline b ON o.CUSTOMER_ID = b.CUSTOMER_ID
    WHERE o.obs_count / GREATEST(b.expected_in_obs, 0.1) >= (SELECT low_r FROM params)
)
SELECT 'SIG-VEL-' || CUSTOMER_ID, CUSTOMER_ID, NULL, 'VELOCITY', CURRENT_TIMESTAMP(),
    DATEADD('day', -(SELECT obs_d FROM params)::INT, CURRENT_DATE()), CURRENT_DATE(),
    severity,
    CASE severity WHEN 'CRITICAL' THEN 100 WHEN 'HIGH' THEN 80 WHEN 'MEDIUM' THEN 55 ELSE 30 END,
    'Transaction velocity anomaly: ' || obs_count || ' transactions in last ' ||
        (SELECT obs_d FROM params)::INT || ' days vs expected ' || expected_count ||
        ' (' || deviation_ratio || 'x deviation). Requires analyst review.',
    OBJECT_CONSTRUCT('baseline_txn_count', base_txn_count, 'expected_in_window', expected_count,
        'observed_count', obs_count, 'deviation_ratio', deviation_ratio),
    'BANKGUARD_RAW.TRANSACTIONS', 'M2-RISK-V1.0'
FROM detected;
