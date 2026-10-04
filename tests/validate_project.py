"""BANKGUARD AI – Project Structure Validation (M0)"""
import os
import sys
import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_DIRS = [
    "docs",
    "config",
    "tests",
    "streamlit",
    "scripts",
    "sql/01_setup",
    "sql/02_tables",
    "sql/03_views",
    "sql/04_seed",
    "sql/05_risk_analytics",
    "sql/06_regulatory",
    "sql/07_audit_reporting",
]

REQUIRED_FILES = [
    "PROJECT_BIBLE.md",
    "config/project.yaml",
    "docs/ARCHITECTURE.md",
    "docs/DATA_MODEL.md",
    "docs/DEVELOPMENT_PLAN.md",
    "docs/AI_GOVERNANCE.md",
    "sql/01_setup/create_schemas.sql",
]


def validate_directories():
    missing = []
    for d in REQUIRED_DIRS:
        path = os.path.join(PROJECT_ROOT, d)
        if not os.path.isdir(path):
            missing.append(d)
    return missing


def validate_files():
    missing = []
    for f in REQUIRED_FILES:
        path = os.path.join(PROJECT_ROOT, f)
        if not os.path.isfile(path):
            missing.append(f)
    return missing


def validate_config():
    config_path = os.path.join(PROJECT_ROOT, "config", "project.yaml")
    with open(config_path, "r") as fh:
        cfg = yaml.safe_load(fh)
    errors = []
    if cfg.get("project", {}).get("name") != "BANKGUARD AI":
        errors.append("project.name is not 'BANKGUARD AI'")
    sf = cfg.get("snowflake", {})
    if sf.get("database") != "USER$STRATEGYSAMUEL":
        errors.append("snowflake.database mismatch")
    if sf.get("warehouse") != "COMPUTE_WH":
        errors.append("snowflake.warehouse mismatch")
    expected_schemas = {"raw", "core", "risk", "regulatory", "audit"}
    actual_schemas = set(sf.get("schemas", {}).keys())
    if not expected_schemas.issubset(actual_schemas):
        errors.append(f"Missing schema keys: {expected_schemas - actual_schemas}")
    return errors


def main():
    print("BANKGUARD AI – M0 Project Validation\n")
    passed = 0
    failed = 0

    missing_dirs = validate_directories()
    if missing_dirs:
        print(f"FAIL  Missing directories: {missing_dirs}")
        failed += 1
    else:
        print(f"PASS  All {len(REQUIRED_DIRS)} directories present")
        passed += 1

    missing_files = validate_files()
    if missing_files:
        print(f"FAIL  Missing files: {missing_files}")
        failed += 1
    else:
        print(f"PASS  All {len(REQUIRED_FILES)} required files present")
        passed += 1

    try:
        config_errors = validate_config()
        if config_errors:
            print(f"FAIL  Config errors: {config_errors}")
            failed += 1
        else:
            print("PASS  project.yaml is valid")
            passed += 1
    except Exception as e:
        print(f"FAIL  Config validation error: {e}")
        failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
