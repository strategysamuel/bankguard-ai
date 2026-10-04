-- BANKGUARD AI – Connection Validation
-- Verifies Snowflake connectivity, database, and warehouse access.

SELECT CURRENT_USER()       AS current_user,
       CURRENT_ROLE()       AS current_role,
       CURRENT_DATABASE()   AS current_database,
       CURRENT_WAREHOUSE()  AS current_warehouse,
       CURRENT_TIMESTAMP()  AS test_timestamp;
