-- Marketing Intelligence Agent: Streamlit in Snowflake setup
-- Run this with a role that can create objects in your chosen database/schema.
-- Replace names as needed for your account.

CREATE DATABASE IF NOT EXISTS MARKETING_INTELLIGENCE;
CREATE SCHEMA IF NOT EXISTS MARKETING_INTELLIGENCE.APP;

USE DATABASE MARKETING_INTELLIGENCE;
USE SCHEMA APP;

-- Sample KPI table so the app can demo Snowflake-native data access immediately.
CREATE OR REPLACE TABLE MARKETING_KPIS (
    metric VARCHAR,
    current FLOAT,
    prior FLOAT,
    segment VARCHAR,
    channel VARCHAR
);

INSERT OVERWRITE INTO MARKETING_KPIS VALUES
    ('revenue', 92, 100, 'all', NULL),
    ('search_traffic', 112, 100, 'all', 'search'),
    ('checkout_conversion', 0.255, 0.30, 'all', NULL),
    ('returning_conversion', 0.20, 0.25, 'returning', NULL);

-- Optional OpenAI setup.
-- IMPORTANT: do not put your real API key in GitHub. Execute the CREATE SECRET statement
-- manually with your key, or use your organization's approved secret-management process.
--
-- CREATE OR REPLACE SECRET OPENAI_API_KEY
--   TYPE = GENERIC_STRING
--   SECRET_STRING = '<YOUR_OPENAI_API_KEY>';
--
-- CREATE OR REPLACE NETWORK RULE OPENAI_NETWORK_RULE
--   MODE = EGRESS
--   TYPE = HOST_PORT
--   VALUE_LIST = ('api.openai.com:443');
--
-- CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION OPENAI_ACCESS_INTEGRATION
--   ALLOWED_NETWORK_RULES = (OPENAI_NETWORK_RULE)
--   ALLOWED_AUTHENTICATION_SECRETS = (OPENAI_API_KEY)
--   ENABLED = TRUE;
--
-- When configuring the Streamlit app, bind:
--   secret alias: openai_key -> MARKETING_INTELLIGENCE.APP.OPENAI_API_KEY
-- and attach OPENAI_ACCESS_INTEGRATION as the app's external access integration.
--
-- The app can be demoed without OpenAI first. Leave "Use OpenAI synthesis" unchecked
-- and select Snowflake table MARKETING_INTELLIGENCE.APP.MARKETING_KPIS.
