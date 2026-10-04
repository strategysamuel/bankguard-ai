-- BANKGUARD AI – M2 Composite Customer Risk Score
-- Aggregates all signal evidence into a single customer risk score.
-- Uses configurable weights from RISK_SIGNAL_WEIGHTS and signal concentration amplifier.
--
-- Scoring approach:
--   1. Each signal contributes: weight * severity_pct
--   2. Raw score = sum of all signal contributions (0-100 scale)
--   3. Signal Concentration Amplifier: when 3+ primary signals fire at HIGH/CRITICAL,
--      the raw score is multiplied by a configurable amplifier (1.05x/1.15x/1.25x)
--      reflecting that correlated signals are disproportionately more concerning
--   4. Final score capped at 100
--
-- Classification: 0-24 LOW, 25-49 MEDIUM, 50-74 HIGH, 75-100 CRITICAL

USE DATABASE BANKGUARD_DB;
USE SCHEMA BANKGUARD_RISK;

TRUNCATE TABLE CUSTOMER_RISK_SCORE;

INSERT INTO CUSTOMER_RISK_SCORE
WITH sig_weighted AS (
    SELECT e.CUSTOMER_ID, e.SIGNAL_TYPE, e.SEVERITY,
           w.WEIGHT * CASE e.SEVERITY
               WHEN 'CRITICAL' THEN w.SEVERITY_CRIT_PCT
               WHEN 'HIGH'     THEN w.SEVERITY_HIGH_PCT
               WHEN 'MEDIUM'   THEN w.SEVERITY_MED_PCT
               WHEN 'LOW'      THEN w.SEVERITY_LOW_PCT
               ELSE 0 END AS wc
    FROM RISK_SIGNAL_EVIDENCE e
    JOIN RISK_SIGNAL_WEIGHTS w ON e.SIGNAL_TYPE = w.SIGNAL_TYPE
),
top_signal AS (
    SELECT CUSTOMER_ID, SIGNAL_TYPE AS top_signal
    FROM sig_weighted WHERE SIGNAL_TYPE != 'MULTI_SIGNAL'
    QUALIFY ROW_NUMBER() OVER (PARTITION BY CUSTOMER_ID ORDER BY wc DESC) = 1
),
cust_labels AS (
    SELECT CUSTOMER_ID,
           LISTAGG(DISTINCT SIGNAL_TYPE || '(' || SEVERITY || ')', ', ')
               WITHIN GROUP (ORDER BY SIGNAL_TYPE || '(' || SEVERITY || ')') AS sig_summary
    FROM sig_weighted GROUP BY CUSTOMER_ID
),
cust_raw AS (
    SELECT CUSTOMER_ID,
           ROUND(SUM(wc), 2) AS raw_score,
           COUNT(DISTINCT SIGNAL_TYPE) AS signal_count,
           SUM(CASE WHEN SEVERITY IN ('HIGH','CRITICAL') AND SIGNAL_TYPE != 'MULTI_SIGNAL'
                    THEN 1 ELSE 0 END) AS hc_count
    FROM sig_weighted GROUP BY CUSTOMER_ID
),
amp AS (
    SELECT MAX(CASE WHEN PARAM_NAME='AMP_3_SIGNALS' THEN PARAM_VALUE END) AS a3,
           MAX(CASE WHEN PARAM_NAME='AMP_4_SIGNALS' THEN PARAM_VALUE END) AS a4,
           MAX(CASE WHEN PARAM_NAME='AMP_5_SIGNALS' THEN PARAM_VALUE END) AS a5
    FROM RISK_THRESHOLDS WHERE SIGNAL_TYPE='COMPOSITE'
),
scored AS (
    SELECT cr.CUSTOMER_ID, cr.raw_score, cr.signal_count, cr.hc_count,
           LEAST(100, ROUND(cr.raw_score * CASE
               WHEN cr.hc_count >= 5 THEN a.a5
               WHEN cr.hc_count >= 4 THEN a.a4
               WHEN cr.hc_count >= 3 THEN a.a3
               ELSE 1.0 END, 2)) AS final_score
    FROM cust_raw cr, amp a
)
SELECT s.CUSTOMER_ID, CURRENT_DATE(), s.final_score,
    CASE WHEN s.final_score >= 75 THEN 'CRITICAL'
         WHEN s.final_score >= 50 THEN 'HIGH'
         WHEN s.final_score >= 25 THEN 'MEDIUM'
         ELSE 'LOW' END,
    s.signal_count, ts.top_signal, cl.sig_summary, 'M2-RISK-V1.0'
FROM scored s
LEFT JOIN top_signal ts ON s.CUSTOMER_ID = ts.CUSTOMER_ID
LEFT JOIN cust_labels cl ON s.CUSTOMER_ID = cl.CUSTOMER_ID;
