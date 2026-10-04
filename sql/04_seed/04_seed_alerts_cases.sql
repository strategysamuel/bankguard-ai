-- BANKGUARD AI – M1 Seed: Fraud Alerts, Investigation Cases, Scenario Metadata
-- Generates ~290 alerts, ~150 cases, and 9 scenario metadata records.
-- See 03_seed_hero_case.sql for hero-specific alerts/cases.

USE DATABASE BANKGUARD_DB;
USE SCHEMA BANKGUARD_RAW;

-- ============================================================
-- SCENARIO METADATA (ground truth for evaluation)
-- ============================================================
INSERT INTO SCENARIO_METADATA VALUES
    ('SCN-A', 'VELOCITY_SPIKE',     'CUST-0901', NULL, DATEADD('day',-3,CURRENT_DATE()), CURRENT_DATE(), 'HIGH_FREQUENCY,SHORT_WINDOW', 'HIGH', 'Sudden burst of 40 transactions per customer in 48 hours; CUST-0901 to CUST-0905'),
    ('SCN-B', 'STRUCTURING',        'CUST-0911', NULL, DATEADD('day',-2,CURRENT_DATE()), CURRENT_DATE(), 'BELOW_THRESHOLD,MULTIPLE_TXNS,SHORT_WINDOW', 'HIGH', 'Multiple transfers just below INR 10L threshold within 24 hours; CUST-0911 to CUST-0915'),
    ('SCN-C', 'BENEFICIARY_BURST',  'CUST-0921', NULL, DATEADD('day',-30,CURRENT_DATE()), CURRENT_DATE(), 'NEW_BENEFICIARIES,RAPID_CREATION,IMMEDIATE_TRANSFERS', 'HIGH', '8 new beneficiaries per customer with immediate transfers; CUST-0921 to CUST-0925'),
    ('SCN-D', 'GEO_ANOMALY',        'CUST-0931', NULL, DATEADD('day',-7,CURRENT_DATE()), CURRENT_DATE(), 'UNUSUAL_COUNTRIES,HIGH_RISK_JURISDICTIONS', 'HIGH', 'International transfers to UAE, Nigeria, Panama, Hong Kong, Cayman Islands; CUST-0931 to CUST-0935'),
    ('SCN-E', 'DORMANT_ACTIVATION', 'CUST-0941', NULL, DATEADD('day',-5,CURRENT_DATE()), CURRENT_DATE(), 'DORMANT_TO_ACTIVE,SUDDEN_ACTIVITY', 'HIGH', 'Previously dormant accounts with 20 transactions in 5 days; CUST-0941 to CUST-0945'),
    ('SCN-F', 'VALUE_SPIKE',        'CUST-0951', NULL, DATEADD('day',-4,CURRENT_DATE()), CURRENT_DATE(), 'AMOUNT_ANOMALY,EXCEEDS_BASELINE', 'HIGH', 'Transaction values 5-10x above customer historical baseline; CUST-0951 to CUST-0955'),
    ('SCN-G', 'CHANNEL_ANOMALY',    'CUST-0961', NULL, DATEADD('day',-3,CURRENT_DATE()), CURRENT_DATE(), 'UNUSUAL_CHANNEL,BRANCH_SPIKE', 'MEDIUM', 'Normally online/mobile customers suddenly using branch channel; CUST-0961 to CUST-0965'),
    ('SCN-H', 'NETWORK_PATTERN',    'CUST-0971', NULL, DATEADD('day',-10,CURRENT_DATE()), CURRENT_DATE(), 'COMMON_BENEFICIARY,COORDINATED_TRANSFERS', 'HIGH', 'Five customers all transferring to the same UAE beneficiary; CUST-0971 to CUST-0975');
-- SCN-I (hero) is in 03_seed_hero_case.sql

-- ============================================================
-- FRAUD_ALERTS (~290 scenario + false-positive alerts)
-- ============================================================
-- Scenario alerts are generated from scenario customer ranges.
-- Normal false-positive alerts are sampled from customers < CUST-0900.
-- See executed session for full INSERT logic.

-- ============================================================
-- INVESTIGATION_CASES (~150 from alerts)
-- ============================================================
-- Cases are created from a subset of alerts.
-- Priority derived from risk score; status from alert disposition.
-- Assigned to synthetic analysts: Priya Sharma, Rahul Verma, Ananya Nair, Vikram Singh, Meera Patel.
