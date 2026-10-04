-- BANKGUARD AI – M2 Risk Parameters & Configuration
-- Rule Version: M2-RISK-V1.0
-- All thresholds are illustrative for synthetic demonstration purposes.

USE DATABASE BANKGUARD_DB;
USE SCHEMA BANKGUARD_RISK;

-- ============================================================
-- RISK_THRESHOLDS: Centralized configurable parameters
-- ============================================================
CREATE OR REPLACE TABLE RISK_THRESHOLDS (
    SIGNAL_TYPE   VARCHAR(50)   NOT NULL,
    PARAM_NAME    VARCHAR(50)   NOT NULL,
    PARAM_VALUE   NUMBER(18,4)  NOT NULL,
    DESCRIPTION   VARCHAR(200)  NOT NULL,
    RULE_VERSION  VARCHAR(20)   NOT NULL DEFAULT 'M2-RISK-V1.0',
    CONSTRAINT PK_THRESHOLDS PRIMARY KEY (SIGNAL_TYPE, PARAM_NAME)
) COMMENT = 'Centralized configurable risk thresholds. M2-RISK-V1.0.';

-- ============================================================
-- RISK_SIGNAL_WEIGHTS: Composite scoring weights
-- Severity percentages: LOW=30%, MEDIUM=55%, HIGH=80%, CRITICAL=100%
-- Signal Concentration Amplifier applied for 3+ HIGH/CRITICAL primary signals
-- ============================================================
CREATE OR REPLACE TABLE RISK_SIGNAL_WEIGHTS (
    SIGNAL_TYPE       VARCHAR(50)  NOT NULL,
    WEIGHT            NUMBER(5,2)  NOT NULL,
    SEVERITY_LOW_PCT  NUMBER(5,2)  NOT NULL  DEFAULT 0.30,
    SEVERITY_MED_PCT  NUMBER(5,2)  NOT NULL  DEFAULT 0.55,
    SEVERITY_HIGH_PCT NUMBER(5,2)  NOT NULL  DEFAULT 0.80,
    SEVERITY_CRIT_PCT NUMBER(5,2)  NOT NULL  DEFAULT 1.00,
    RULE_VERSION      VARCHAR(20)  NOT NULL  DEFAULT 'M2-RISK-V1.0',
    CONSTRAINT PK_WEIGHTS PRIMARY KEY (SIGNAL_TYPE)
) COMMENT = 'Signal weight config. Total weights = 100.';

-- Weights (total = 100)
INSERT INTO RISK_SIGNAL_WEIGHTS VALUES
    ('VELOCITY',          15, 0.30, 0.55, 0.80, 1.00, 'M2-RISK-V1.0'),
    ('STRUCTURING',       20, 0.30, 0.55, 0.80, 1.00, 'M2-RISK-V1.0'),
    ('BENEFICIARY_BURST', 15, 0.30, 0.55, 0.80, 1.00, 'M2-RISK-V1.0'),
    ('GEO_ANOMALY',       10, 0.30, 0.55, 0.80, 1.00, 'M2-RISK-V1.0'),
    ('DORMANT_ACTIVATION',10, 0.30, 0.55, 0.80, 1.00, 'M2-RISK-V1.0'),
    ('VALUE_SPIKE',       10, 0.30, 0.55, 0.80, 1.00, 'M2-RISK-V1.0'),
    ('CHANNEL_ANOMALY',    5, 0.30, 0.55, 0.80, 1.00, 'M2-RISK-V1.0'),
    ('NETWORK_PATTERN',   10, 0.30, 0.55, 0.80, 1.00, 'M2-RISK-V1.0'),
    ('MULTI_SIGNAL',       5, 0.30, 0.55, 0.80, 1.00, 'M2-RISK-V1.0');

-- All threshold parameters
INSERT INTO RISK_THRESHOLDS VALUES
    ('VELOCITY','OBSERVATION_DAYS',7,'Recent observation window','M2-RISK-V1.0'),
    ('VELOCITY','BASELINE_DAYS',330,'Historical baseline lookback','M2-RISK-V1.0'),
    ('VELOCITY','MIN_BASELINE_TXNS',10,'Min historical txns for baseline','M2-RISK-V1.0'),
    ('VELOCITY','LOW_RATIO',2.0,'Deviation ratio for LOW','M2-RISK-V1.0'),
    ('VELOCITY','MEDIUM_RATIO',2.5,'Deviation ratio for MEDIUM','M2-RISK-V1.0'),
    ('VELOCITY','HIGH_RATIO',3.0,'Deviation ratio for HIGH','M2-RISK-V1.0'),
    ('VELOCITY','CRITICAL_RATIO',4.0,'Deviation ratio for CRITICAL','M2-RISK-V1.0'),
    ('STRUCTURING','AMOUNT_THRESHOLD',1000000,'Illustrative threshold INR','M2-RISK-V1.0'),
    ('STRUCTURING','PROXIMITY_LOW_PCT',0.80,'Lower proximity band (80%)','M2-RISK-V1.0'),
    ('STRUCTURING','WINDOW_HOURS',48,'Time window for pattern','M2-RISK-V1.0'),
    ('STRUCTURING','LOW_COUNT',2,'Min txns for LOW','M2-RISK-V1.0'),
    ('STRUCTURING','MEDIUM_COUNT',3,'Min txns for MEDIUM','M2-RISK-V1.0'),
    ('STRUCTURING','HIGH_COUNT',4,'Min txns for HIGH','M2-RISK-V1.0'),
    ('STRUCTURING','CRITICAL_AGGREGATE_RATIO',3.0,'Aggregate/threshold for CRITICAL','M2-RISK-V1.0'),
    ('BENEFICIARY_BURST','OBSERVATION_DAYS',30,'New beneficiary window','M2-RISK-V1.0'),
    ('BENEFICIARY_BURST','LOW_COUNT',2,'New bens for LOW','M2-RISK-V1.0'),
    ('BENEFICIARY_BURST','MEDIUM_COUNT',3,'for MEDIUM','M2-RISK-V1.0'),
    ('BENEFICIARY_BURST','HIGH_COUNT',4,'for HIGH','M2-RISK-V1.0'),
    ('BENEFICIARY_BURST','CRITICAL_COUNT',5,'for CRITICAL','M2-RISK-V1.0'),
    ('GEO_ANOMALY','OBSERVATION_DAYS',30,'Recent window','M2-RISK-V1.0'),
    ('GEO_ANOMALY','BASELINE_DAYS',330,'Historical window','M2-RISK-V1.0'),
    ('GEO_ANOMALY','CRITICAL_NEW_HR_COUNTRIES',2,'New high-risk for CRITICAL','M2-RISK-V1.0'),
    ('GEO_ANOMALY','HIGH_NEW_COUNTRIES',2,'New countries for HIGH','M2-RISK-V1.0'),
    ('DORMANT_ACTIVATION','DORMANT_DAYS',180,'Min dormancy period','M2-RISK-V1.0'),
    ('DORMANT_ACTIVATION','MAX_DORMANT_TXNS',2,'Max txns during dormancy','M2-RISK-V1.0'),
    ('DORMANT_ACTIVATION','ACTIVATION_DAYS',30,'Post-activation window','M2-RISK-V1.0'),
    ('DORMANT_ACTIVATION','LOW_TXNS',5,'Min activation txns for LOW','M2-RISK-V1.0'),
    ('DORMANT_ACTIVATION','CRITICAL_TXNS',15,'Activation txns for CRITICAL','M2-RISK-V1.0'),
    ('VALUE_SPIKE','OBSERVATION_DAYS',7,'Recent value window','M2-RISK-V1.0'),
    ('VALUE_SPIKE','BASELINE_DAYS',330,'Historical baseline','M2-RISK-V1.0'),
    ('VALUE_SPIKE','LOW_RATIO',3.0,'for LOW','M2-RISK-V1.0'),
    ('VALUE_SPIKE','MEDIUM_RATIO',5.0,'for MEDIUM','M2-RISK-V1.0'),
    ('VALUE_SPIKE','HIGH_RATIO',10.0,'for HIGH','M2-RISK-V1.0'),
    ('VALUE_SPIKE','CRITICAL_RATIO',15.0,'for CRITICAL','M2-RISK-V1.0'),
    ('CHANNEL_ANOMALY','OBSERVATION_DAYS',30,'Recent window','M2-RISK-V1.0'),
    ('CHANNEL_ANOMALY','BASELINE_DAYS',330,'Historical baseline','M2-RISK-V1.0'),
    ('CHANNEL_ANOMALY','MIN_SHIFT_PCT',25,'Channel share shift to trigger','M2-RISK-V1.0'),
    ('NETWORK_PATTERN','MIN_CUSTOMERS',3,'Min customers sharing dest','M2-RISK-V1.0'),
    ('NETWORK_PATTERN','OBSERVATION_DAYS',60,'Network detection window','M2-RISK-V1.0'),
    ('NETWORK_PATTERN','MEDIUM_CUSTOMERS',4,'for MEDIUM','M2-RISK-V1.0'),
    ('NETWORK_PATTERN','HIGH_CUSTOMERS',5,'for HIGH','M2-RISK-V1.0'),
    ('MULTI_SIGNAL','LOW_SIGNALS',2,'Active signals for LOW','M2-RISK-V1.0'),
    ('MULTI_SIGNAL','MEDIUM_SIGNALS',3,'for MEDIUM','M2-RISK-V1.0'),
    ('MULTI_SIGNAL','HIGH_SIGNALS',4,'for HIGH','M2-RISK-V1.0'),
    ('MULTI_SIGNAL','CRITICAL_SIGNALS',5,'for CRITICAL','M2-RISK-V1.0'),
    ('COMPOSITE','AMP_3_SIGNALS',1.05,'Amplifier for 3 HIGH+ signals','M2-RISK-V1.0'),
    ('COMPOSITE','AMP_4_SIGNALS',1.15,'Amplifier for 4 HIGH+ signals','M2-RISK-V1.0'),
    ('COMPOSITE','AMP_5_SIGNALS',1.25,'Amplifier for 5+ HIGH+ signals','M2-RISK-V1.0');
