-- BANKGUARD AI – M3 Retrieval Views and Negative Policy Gate

USE DATABASE BANKGUARD_DB;
USE SCHEMA BANKGUARD_REGULATORY;

-- ============================================================
-- V_RETRIEVAL_DOCUMENTS: Search-ready documents for future Cortex Search
-- ============================================================
CREATE OR REPLACE VIEW V_RETRIEVAL_DOCUMENTS AS
SELECT
    ps.SECTION_ID AS DOCUMENT_ID,
    p.POLICY_ID, p.POLICY_VERSION, ps.SECTION_ID,
    ps.SECTION_NUMBER || ' ' || ps.SECTION_TITLE AS TITLE,
    ps.SECTION_TEXT AS CONTENT,
    p.POLICY_DOMAIN, ps.RISK_TOPIC, p.STATUS, p.EFFECTIVE_DATE,
    p.SOURCE_TYPE, p.SOURCE_NAME,
    p.POLICY_TITLE || ' | ' || ps.SECTION_NUMBER || ' ' || ps.SECTION_TITLE || ' | ' ||
        ps.SECTION_TEXT || ' | ' || COALESCE(ps.CONTROL_OBJECTIVE, '') || ' | ' ||
        COALESCE(ps.REQUIRED_ACTION, '') || ' | ' || ps.RISK_TOPIC AS SEARCH_TEXT
FROM POLICY_SECTIONS ps
JOIN POLICIES p ON ps.POLICY_ID = p.POLICY_ID AND ps.POLICY_VERSION = p.POLICY_VERSION
WHERE p.STATUS = 'ACTIVE';

-- ============================================================
-- V_SIGNAL_POLICY_CHAIN: End-to-end signal → policy → evidence chain
-- ============================================================
CREATE OR REPLACE VIEW V_SIGNAL_POLICY_CHAIN AS
SELECT
    e.CUSTOMER_ID, e.SIGNAL_TYPE, e.SEVERITY AS SIGNAL_SEVERITY,
    m.POLICY_ID, m.POLICY_VERSION, m.SECTION_ID,
    ps.SECTION_NUMBER || ' ' || ps.SECTION_TITLE AS SECTION_TITLE,
    p.STATUS AS POLICY_STATUS, p.EFFECTIVE_DATE,
    m.RELEVANCE, ps.EVIDENCE_REQUIREMENT, p.SOURCE_TYPE
FROM BANKGUARD_RISK.RISK_SIGNAL_EVIDENCE e
JOIN POLICY_RISK_MAPPING m ON e.SIGNAL_TYPE = m.RISK_SIGNAL
JOIN POLICIES p ON m.POLICY_ID = p.POLICY_ID AND m.POLICY_VERSION = p.POLICY_VERSION
JOIN POLICY_SECTIONS ps ON m.SECTION_ID = ps.SECTION_ID
WHERE p.STATUS = 'ACTIVE';

-- ============================================================
-- V_NEGATIVE_POLICY_GATE: Validates unmapped topics return no policy
-- ============================================================
CREATE OR REPLACE VIEW V_NEGATIVE_POLICY_GATE AS
WITH all_signals AS (
    SELECT DISTINCT SIGNAL_TYPE FROM BANKGUARD_RISK.RISK_SIGNAL_EVIDENCE
),
mapped_signals AS (
    SELECT DISTINCT RISK_SIGNAL AS SIGNAL_TYPE
    FROM POLICY_RISK_MAPPING m
    JOIN POLICIES p ON m.POLICY_ID = p.POLICY_ID AND m.POLICY_VERSION = p.POLICY_VERSION
    WHERE p.STATUS = 'ACTIVE'
),
test_topics AS (
    SELECT 'CRYPTOCURRENCY' AS SIGNAL_TYPE
    UNION ALL SELECT SIGNAL_TYPE FROM all_signals
)
SELECT t.SIGNAL_TYPE,
    CASE WHEN m.SIGNAL_TYPE IS NOT NULL THEN 'POLICY_FOUND'
         ELSE 'NO_APPLICABLE_POLICY_FOUND' END AS POLICY_STATUS,
    CASE WHEN m.SIGNAL_TYPE IS NOT NULL THEN 'Active policy mapping exists'
         ELSE 'No policy covers this risk topic. Do not fabricate a policy connection.' END AS GUIDANCE
FROM test_topics t
LEFT JOIN mapped_signals m ON t.SIGNAL_TYPE = m.SIGNAL_TYPE;
