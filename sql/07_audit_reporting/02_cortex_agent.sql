-- BANKGUARD AI – M4 Cortex Agent Definition
-- Creates the BANKGUARD_AGENT with Cortex Analyst + Cortex Search tools.

USE DATABASE BANKGUARD_DB;

CREATE OR REPLACE AGENT BANKGUARD_CORE.BANKGUARD_AGENT
  COMMENT = 'BANKGUARD AI Risk, Fraud and Regulatory Intelligence Copilot.'
  PROFILE = '{"display_name": "BANKGUARD AI", "color": "red"}'
  FROM SPECIFICATION
  $$
  models:
    orchestration: auto

  orchestration:
    capabilities:
      analytical_search: true
    tool_not_accessible: accept
    budget:
      seconds: 60
      tokens: 32000

  instructions:
    response: >
      You are BANKGUARD AI, a Risk, Fraud and Regulatory Intelligence Copilot.
      All data is SYNTHETIC DEMONSTRATION DATA.
      Never declare fraud or crime. Use "potential pattern" or "requires analyst review".
      Never recommend freezing accounts or filing reports.
      Cite policies as [PC-XXX-001 vX.X, Section X.X].
      If evidence is insufficient, state so clearly.

    orchestration: >
      For risk or transaction data, use RiskAnalyst.
      For policy guidance, use PolicySearch.
      For investigations, use both tools.

    sample_questions:
      - question: "What is the risk profile for CUST-1042?"
      - question: "Show me all CRITICAL risk customers"
      - question: "What policy applies to transaction structuring?"

  tools:
    - tool_spec:
        type: "cortex_analyst_text_to_sql"
        name: "RiskAnalyst"
        description: "Queries BANKGUARD structured data: customer profiles, risk scores (0-100), risk signals with severity, transactions, alerts, investigation cases."
    - tool_spec:
        type: "cortex_search"
        name: "PolicySearch"
        description: "Searches synthetic regulatory policy knowledge base. Returns policy sections with ID, version, and content."

  tool_resources:
    RiskAnalyst:
      semantic_view: "BANKGUARD_DB.BANKGUARD_CORE.BANKGUARD_RISK_ANALYST"
      warehouse: COMPUTE_WH
    PolicySearch:
      search_service: "BANKGUARD_DB.BANKGUARD_REGULATORY.POLICY_SEARCH_SERVICE"
      max_results: "5"
  $$;
