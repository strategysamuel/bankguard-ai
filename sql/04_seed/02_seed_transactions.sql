-- BANKGUARD AI – M1 Seed: Transactions (Normal + Scenarios)
-- Generates ~95K normal transactions and ~600 scenario transactions.
-- Uses HASH-based deterministic pseudo-randomness.
-- Idempotent approach: run DDL first to get clean tables.
--
-- Transaction type distribution:
--   UPI 22%, POS 20%, Domestic Transfer 12%, ATM 12%,
--   Utility 10%, Salary 8%, EMI 7%, Rent 6%, International 3%
--
-- Scenario transactions (targeted inserts for risk patterns):
--   A: Velocity spike (CUST-0901..0905)
--   B: Structuring below threshold (CUST-0911..0915)
--   C: New beneficiary burst (CUST-0921..0925)
--   D: Geographic anomaly (CUST-0931..0935)
--   E: Dormant account activation (CUST-0941..0945)
--   F: Sudden value increase (CUST-0951..0955)
--   G: Channel anomaly (CUST-0961..0965)
--   H: Network/common beneficiary (CUST-0971..0975)

USE DATABASE BANKGUARD_DB;
USE SCHEMA BANKGUARD_RAW;

-- ============================================================
-- NORMAL TRANSACTIONS (~95K)
-- ============================================================
INSERT INTO TRANSACTIONS
WITH accts AS (
    SELECT a.ACCOUNT_ID, a.CUSTOMER_ID, a.ACCOUNT_TYPE, a.CURRENCY, c.CUSTOMER_SEGMENT,
           ROW_NUMBER() OVER (ORDER BY a.ACCOUNT_ID) AS aidx,
           COUNT(*) OVER () AS total_accts
    FROM ACCOUNTS a
    JOIN CUSTOMERS c ON a.CUSTOMER_ID = c.CUSTOMER_ID
    WHERE a.ACCOUNT_TYPE IN ('SAVINGS','CURRENT','SALARY')
      AND a.ACCOUNT_STATUS = 'ACTIVE'
      AND c.CUSTOMER_ID NOT IN ('CUST-1042')
),
raw_rows AS (
    SELECT ROW_NUMBER() OVER (ORDER BY SEQ4()) AS rn FROM TABLE(GENERATOR(ROWCOUNT => 95000))
),
merchants AS (
    SELECT column1 AS mname, column2 AS midx FROM VALUES
    ('Amazon India',0),('Flipkart',1),('BigBasket',2),('Swiggy',3),('Zomato',4),
    ('Reliance Retail',5),('DMart',6),('Myntra',7),('BookMyShow',8),('MakeMyTrip',9),
    ('PhonePe Merchant',10),('Google Pay Merchant',11),('Petrol Pump',12),('Medical Store',13),
    ('Croma Electronics',14),('Lifestyle',15),('PVR Cinemas',16),('Uber',17),('Ola',18),('Jio Mart',19)
),
assigned AS (
    SELECT r.rn, a.ACCOUNT_ID, a.CUSTOMER_ID, a.CURRENCY, a.CUSTOMER_SEGMENT,
           MOD(ABS(HASH(r.rn*41+7)),100) AS type_rnd,
           MOD(ABS(HASH(r.rn*53+11)),365) AS day_offset,
           MOD(ABS(HASH(r.rn*59+13)),24) AS hr,
           MOD(ABS(HASH(r.rn*61+17)),60) AS mn
    FROM raw_rows r
    JOIN accts a ON a.aidx = MOD(ABS(HASH(r.rn*47+3)),a.total_accts)+1
)
SELECT
    'TXN-' || LPAD(a.rn::VARCHAR, 7, '0'),
    a.ACCOUNT_ID, a.CUSTOMER_ID,
    DATEADD('minute', a.hr*60+a.mn, DATEADD('day', -a.day_offset, CURRENT_DATE())::TIMESTAMP_NTZ),
    -- Transaction type
    CASE
        WHEN a.type_rnd < 8  THEN 'SALARY_CREDIT'
        WHEN a.type_rnd < 20 THEN 'ATM_WITHDRAWAL'
        WHEN a.type_rnd < 40 THEN 'POS_PURCHASE'
        WHEN a.type_rnd < 62 THEN 'UPI_PAYMENT'
        WHEN a.type_rnd < 72 THEN 'UTILITY_PAYMENT'
        WHEN a.type_rnd < 78 THEN 'RENT_PAYMENT'
        WHEN a.type_rnd < 85 THEN 'EMI_PAYMENT'
        WHEN a.type_rnd < 97 THEN 'DOMESTIC_TRANSFER'
        ELSE 'INTERNATIONAL_TRANSFER'
    END,
    -- Amount (varies by type and segment)
    CASE
        WHEN a.type_rnd < 8  THEN CASE a.CUSTOMER_SEGMENT
            WHEN 'RETAIL' THEN 25000+MOD(ABS(HASH(a.rn*67)),50000)
            WHEN 'AFFLUENT' THEN 100000+MOD(ABS(HASH(a.rn*67)),300000)
            WHEN 'SME' THEN 150000+MOD(ABS(HASH(a.rn*67)),500000)
            ELSE 500000+MOD(ABS(HASH(a.rn*67)),2000000) END
        WHEN a.type_rnd < 20 THEN 500+MOD(ABS(HASH(a.rn*71)),19500)
        WHEN a.type_rnd < 40 THEN 100+MOD(ABS(HASH(a.rn*73)),25000)
        WHEN a.type_rnd < 62 THEN 50+MOD(ABS(HASH(a.rn*79)),15000)
        WHEN a.type_rnd < 72 THEN 500+MOD(ABS(HASH(a.rn*83)),9500)
        WHEN a.type_rnd < 78 THEN 5000+MOD(ABS(HASH(a.rn*89)),45000)
        WHEN a.type_rnd < 85 THEN 2000+MOD(ABS(HASH(a.rn*97)),48000)
        WHEN a.type_rnd < 97 THEN 1000+MOD(ABS(HASH(a.rn*101)),200000)
        ELSE 10000+MOD(ABS(HASH(a.rn*103)),500000)
    END,
    a.CURRENCY,
    -- Channel
    CASE
        WHEN a.type_rnd < 8  THEN 'ONLINE'
        WHEN a.type_rnd < 20 THEN 'ATM'
        WHEN a.type_rnd < 40 THEN 'POS'
        WHEN a.type_rnd < 62 THEN 'MOBILE'
        WHEN a.type_rnd < 85 THEN 'ONLINE'
        WHEN a.type_rnd < 97 THEN CASE MOD(ABS(HASH(a.rn*107)),3)
            WHEN 0 THEN 'ONLINE' WHEN 1 THEN 'MOBILE' ELSE 'BRANCH' END
        ELSE 'ONLINE'
    END,
    -- Merchant
    CASE WHEN a.type_rnd >= 20 AND a.type_rnd < 62 THEN m.mname ELSE NULL END,
    NULL, -- BENEFICIARY_ID
    -- Country
    CASE WHEN a.type_rnd >= 97 THEN
        CASE MOD(ABS(HASH(a.rn*109)),5)
            WHEN 0 THEN 'UAE' WHEN 1 THEN 'Singapore' WHEN 2 THEN 'USA' WHEN 3 THEN 'UK' ELSE 'Hong Kong' END
    ELSE 'India' END,
    'DEV-' || LPAD(MOD(ABS(HASH(a.CUSTOMER_ID||'dev')),500)::VARCHAR, 4, '0'),
    '10.'||MOD(ABS(HASH(a.rn*113)),256)||'.'||MOD(ABS(HASH(a.rn*127)),256)||'.'||MOD(ABS(HASH(a.rn*131)),256),
    'COMPLETED', CURRENT_TIMESTAMP()
FROM assigned a
LEFT JOIN merchants m ON MOD(ABS(HASH(a.rn*137)),20) = m.midx;

-- Fix any future-dated transactions
UPDATE TRANSACTIONS SET TRANSACTION_DATE = DATEADD('hour', -1, CURRENT_TIMESTAMP())
WHERE TRANSACTION_DATE > CURRENT_TIMESTAMP();

-- ============================================================
-- SCENARIO TRANSACTIONS (see 03_seed_hero_case.sql for hero)
-- ============================================================

-- Scenario A: Velocity spike (40 txns each, CUST-0901..0905)
-- Scenario B: Structuring (8 txns each just below 10L, CUST-0911..0915)
-- Scenario C: New beneficiary burst (txns to new bens, CUST-0921..0925)
-- Scenario D: Geographic anomaly (intl to unusual countries, CUST-0931..0935)
-- Scenario E: Dormant activation (20 txns after dormancy, CUST-0941..0945)
-- Scenario F: Sudden value increase (5 large txns each, CUST-0951..0955)
-- Scenario G: Channel anomaly (8 branch txns each, CUST-0961..0965)
-- Scenario H: Network/common beneficiary (shared UAE beneficiary, CUST-0971..0975)
-- See individual INSERT statements in the executed seed session.
