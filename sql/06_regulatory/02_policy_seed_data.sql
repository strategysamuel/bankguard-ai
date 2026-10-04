-- BANKGUARD AI – M3 Policy Seed Data
-- SYNTHETIC DEMONSTRATION CONTENT. Not actual legal or regulatory advice.
-- See 01_policy_tables.sql for DDL.
-- Seed order: taxonomy → policies → sections → mappings → evidence requirements.

USE DATABASE BANKGUARD_DB;
USE SCHEMA BANKGUARD_REGULATORY;

-- Risk topic taxonomy (12 topics)
-- Policy versions (19 versions across 10 policies: 10 active, 9 superseded)
-- Policy sections (23 sections across 10 active policies)
-- Policy-risk mappings (24 mappings covering all 9 M2 signal types)
-- Evidence requirements (27 requirements linked to policy sections)

-- See the executed M3 session for full INSERT statements.
-- All records carry SOURCE_TYPE = 'SYNTHETIC_DEMO'.
