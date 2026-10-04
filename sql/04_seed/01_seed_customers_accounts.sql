-- BANKGUARD AI – M1 Seed: Customers, Accounts, Beneficiaries
-- Generates ~1000 customers, ~1500 accounts, ~2500 beneficiaries.
-- Uses HASH-based deterministic pseudo-randomness.
-- Idempotent approach: run DDL (01_raw_tables.sql) first to get clean tables.
--
-- Customer distribution:
--   Segment: Retail ~56%, Affluent ~20%, SME ~14%, Corporate ~10%
--   Risk: Low ~68%, Medium ~18%, High ~14%
--   Scenario customers: CUST-0901..0975 (assigned HIGH risk)

USE DATABASE BANKGUARD_DB;
USE SCHEMA BANKGUARD_RAW;

-- ============================================================
-- CUSTOMERS (~1000 normal)
-- ============================================================
INSERT INTO CUSTOMERS
WITH cities AS (
    SELECT column1 AS city FROM VALUES
    ('Mumbai'),('Delhi'),('Bangalore'),('Chennai'),('Hyderabad'),('Pune'),('Kolkata'),
    ('Ahmedabad'),('Jaipur'),('Lucknow'),('Kochi'),('Chandigarh'),('Indore'),('Nagpur'),
    ('Coimbatore'),('Vadodara'),('Surat'),('Visakhapatnam'),('Bhopal'),('Thiruvananthapuram')
),
city_list AS (
    SELECT city, ROW_NUMBER() OVER (ORDER BY city) - 1 AS cidx FROM cities
),
base AS (
    SELECT ROW_NUMBER() OVER (ORDER BY SEQ4()) AS rn FROM TABLE(GENERATOR(ROWCOUNT => 1000))
)
SELECT
    'CUST-' || LPAD(rn::VARCHAR, 4, '0'),
    CASE WHEN MOD(ABS(HASH(rn * 7 + 1)), 100) < 80 THEN 'INDIVIDUAL' ELSE 'BUSINESS' END,
    CASE
        WHEN rn BETWEEN 971 AND 980 THEN 'CORPORATE'
        WHEN MOD(ABS(HASH(rn * 13 + 3)), 100) < 55 THEN 'RETAIL'
        WHEN MOD(ABS(HASH(rn * 13 + 3)), 100) < 75 THEN 'AFFLUENT'
        WHEN MOD(ABS(HASH(rn * 13 + 3)), 100) < 90 THEN 'SME'
        ELSE 'CORPORATE'
    END,
    CASE
        WHEN rn BETWEEN 901 AND 975 THEN 'HIGH'
        WHEN MOD(ABS(HASH(rn * 17 + 5)), 100) < 70 THEN 'LOW'
        WHEN MOD(ABS(HASH(rn * 17 + 5)), 100) < 92 THEN 'MEDIUM'
        ELSE 'HIGH'
    END,
    CASE WHEN MOD(ABS(HASH(rn * 19 + 7)), 100) < 88 THEN 'VERIFIED'
         WHEN MOD(ABS(HASH(rn * 19 + 7)), 100) < 96 THEN 'PENDING' ELSE 'EXPIRED' END,
    DATEADD('day', -MOD(ABS(HASH(rn * 23 + 11)), 2500), CURRENT_DATE()),
    CASE
        WHEN MOD(ABS(HASH(rn * 13 + 3)), 100) < 55 THEN 300000 + MOD(ABS(HASH(rn * 29)), 700000)
        WHEN MOD(ABS(HASH(rn * 13 + 3)), 100) < 75 THEN 1500000 + MOD(ABS(HASH(rn * 31)), 3500000)
        WHEN MOD(ABS(HASH(rn * 13 + 3)), 100) < 90 THEN 2000000 + MOD(ABS(HASH(rn * 37)), 8000000)
        ELSE 10000000 + MOD(ABS(HASH(rn * 41)), 40000000)
    END,
    'India',
    cl.city,
    CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
FROM base b
JOIN city_list cl ON MOD(ABS(HASH(b.rn * 43)), 20) = cl.cidx;

-- ============================================================
-- ACCOUNTS (~1500: 1-3 per customer)
-- ============================================================
INSERT INTO ACCOUNTS
WITH cust AS (
    SELECT CUSTOMER_ID, CUSTOMER_SEGMENT, CUSTOMER_SINCE,
           ABS(HASH(CUSTOMER_ID || 'acct')) AS h
    FROM CUSTOMERS
),
expanded AS (
    SELECT CUSTOMER_ID, CUSTOMER_SEGMENT, CUSTOMER_SINCE, h, 1 AS acct_seq FROM cust
    UNION ALL SELECT CUSTOMER_ID, CUSTOMER_SEGMENT, CUSTOMER_SINCE, h, 2 FROM cust WHERE MOD(h, 100) < 45
    UNION ALL SELECT CUSTOMER_ID, CUSTOMER_SEGMENT, CUSTOMER_SINCE, h, 3 FROM cust WHERE MOD(h, 100) < 8
),
numbered AS (
    SELECT *, ROW_NUMBER() OVER (ORDER BY CUSTOMER_ID, acct_seq) AS rn FROM expanded
)
SELECT
    'ACCT-' || LPAD(rn::VARCHAR, 5, '0'),
    CUSTOMER_ID,
    CASE acct_seq
        WHEN 1 THEN CASE CUSTOMER_SEGMENT
            WHEN 'RETAIL' THEN 'SAVINGS' WHEN 'AFFLUENT' THEN 'SAVINGS'
            WHEN 'SME' THEN 'CURRENT' ELSE 'CURRENT' END
        WHEN 2 THEN CASE WHEN MOD(h,3)=0 THEN 'FD' WHEN MOD(h,3)=1 THEN 'SALARY' ELSE 'CURRENT' END
        ELSE 'LOAN'
    END,
    DATEADD('day', acct_seq * 30, CUSTOMER_SINCE),
    CASE CUSTOMER_SEGMENT
        WHEN 'RETAIL' THEN 10000+MOD(ABS(HASH(CUSTOMER_ID||acct_seq)),200000)
        WHEN 'AFFLUENT' THEN 100000+MOD(ABS(HASH(CUSTOMER_ID||acct_seq)),2000000)
        WHEN 'SME' THEN 200000+MOD(ABS(HASH(CUSTOMER_ID||acct_seq)),5000000)
        ELSE 1000000+MOD(ABS(HASH(CUSTOMER_ID||acct_seq)),20000000)
    END,
    CASE WHEN CUSTOMER_ID IN ('CUST-0941','CUST-0942','CUST-0943','CUST-0944','CUST-0945') AND acct_seq=1
         THEN 'DORMANT' ELSE 'ACTIVE' END,
    'INR', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
FROM numbered;

-- ============================================================
-- BENEFICIARIES (~2500: 1-5 per customer)
-- ============================================================
INSERT INTO BENEFICIARIES
WITH cust AS (
    SELECT CUSTOMER_ID, ABS(HASH(CUSTOMER_ID || 'ben')) AS h FROM CUSTOMERS
),
expanded AS (
    SELECT CUSTOMER_ID, h, 1 AS bseq FROM cust
    UNION ALL SELECT CUSTOMER_ID, h, 2 FROM cust WHERE MOD(h, 100) < 70
    UNION ALL SELECT CUSTOMER_ID, h, 3 FROM cust WHERE MOD(h, 100) < 40
    UNION ALL SELECT CUSTOMER_ID, h, 4 FROM cust WHERE MOD(h, 100) < 15
    UNION ALL SELECT CUSTOMER_ID, h, 5 FROM cust WHERE MOD(h, 100) < 5
),
countries AS (
    SELECT column1 AS cty, column2 AS cidx FROM VALUES
    ('India',0),('India',1),('India',2),('India',3),('India',4),('India',5),
    ('India',6),('India',7),('India',8),('India',9),('India',10),('India',11),
    ('India',12),('India',13),('India',14),('UAE',15),('Singapore',16),
    ('USA',17),('UK',18),('Hong Kong',19)
),
banks AS (
    SELECT column1 AS bk, column2 AS bidx FROM VALUES
    ('State Bank of India',0),('HDFC Bank',1),('ICICI Bank',2),('Axis Bank',3),
    ('Kotak Mahindra Bank',4),('Punjab National Bank',5),('Bank of Baroda',6),
    ('Yes Bank',7),('IndusInd Bank',8),('Federal Bank',9),
    ('Emirates NBD',10),('DBS Bank',11),('Citibank',12),('HSBC',13),
    ('Standard Chartered',14),('Barclays',15),('JPMorgan Chase',16),
    ('Bank of China',17),('Mashreq Bank',18),('RBL Bank',19)
),
numbered AS (
    SELECT e.*, ROW_NUMBER() OVER (ORDER BY e.CUSTOMER_ID, e.bseq) AS rn FROM expanded e
)
SELECT
    'BEN-' || LPAD(n.rn::VARCHAR, 5, '0'),
    n.CUSTOMER_ID,
    DATEADD('day', -MOD(ABS(HASH(n.rn * 31 + 7)), 365), CURRENT_DATE()),
    c.cty, b.bk,
    CASE MOD(ABS(HASH(n.rn*47)),4) WHEN 0 THEN 'SAVINGS' WHEN 1 THEN 'CURRENT' WHEN 2 THEN 'SAVINGS' ELSE 'NRE' END,
    'ACTIVE', CURRENT_TIMESTAMP()
FROM numbered n
JOIN countries c ON MOD(ABS(HASH(n.rn * 53 + 3)), 20) = c.cidx
JOIN banks b ON MOD(ABS(HASH(n.rn * 59 + 11)), 20) = b.bidx;
