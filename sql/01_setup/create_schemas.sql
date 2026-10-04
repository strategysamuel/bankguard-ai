-- BANKGUARD AI – M1 Database and Schema Setup
-- Creates BANKGUARD_DB and all schemas.
-- Idempotent: safe to re-run.
-- NOTE: M0 originally used USER$STRATEGYSAMUEL (personal DB) but tables
--       cannot be created in personal databases. BANKGUARD_DB is the
--       standard database used for all BANKGUARD objects.

USE WAREHOUSE COMPUTE_WH;

CREATE DATABASE IF NOT EXISTS BANKGUARD_DB
  COMMENT = 'BANKGUARD AI – Risk, Fraud & Regulatory Intelligence Copilot (Synthetic Data Only)';

CREATE SCHEMA IF NOT EXISTS BANKGUARD_DB.BANKGUARD_RAW
  COMMENT = 'Raw ingested data (synthetic banking transactions, accounts, customers)';

CREATE SCHEMA IF NOT EXISTS BANKGUARD_DB.BANKGUARD_CORE
  COMMENT = 'Cleansed and enriched data models';

CREATE SCHEMA IF NOT EXISTS BANKGUARD_DB.BANKGUARD_RISK
  COMMENT = 'Risk scoring, fraud detection, AML analytics';

CREATE SCHEMA IF NOT EXISTS BANKGUARD_DB.BANKGUARD_REGULATORY
  COMMENT = 'Regulatory knowledge base, policies, compliance references';

CREATE SCHEMA IF NOT EXISTS BANKGUARD_DB.BANKGUARD_AUDIT
  COMMENT = 'Investigation findings, audit trails, AI decision logs';
