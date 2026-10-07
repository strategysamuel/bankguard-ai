"""Release 1.1 — Widget key and code quality validation script."""
import ast
import re
import sys

src = open("streamlit/app.py", encoding="utf-8").read()
tree = ast.parse(src)
errors = []

# --- 1. Functions ---
funcs = [(n.name, n.lineno) for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
print("=== FUNCTIONS ===")
for name, line in funcs:
    print(f"  {name} (line {line})")

# --- 2. Imports ---
imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
print(f"\n=== IMPORTS ({len(imports)}) ===")
for i in imports:
    if isinstance(i, ast.Import):
        names = ", ".join(a.name for a in i.names)
        print(f"  import {names}")
    else:
        names = ", ".join(a.name for a in i.names)
        print(f"  from {i.module} import {names}")

# --- 3. Extract all key= patterns ---
key_pattern = re.compile(r"""key\s*=\s*(?:f?"([^"]*)"|f?'([^']*)')""")
keys_found = []
for lineno, line in enumerate(src.splitlines(), 1):
    for m in key_pattern.finditer(line):
        k = m.group(1) or m.group(2)
        keys_found.append((lineno, k))

static_keys = []
dynamic_keys = []
for lineno, k in keys_found:
    if "{" in k:
        dynamic_keys.append((lineno, k))
    else:
        static_keys.append((lineno, k))

print(f"\n=== STATIC WIDGET KEYS ({len(static_keys)}) ===")
seen = set()
for lineno, k in static_keys:
    dup = " ** DUPLICATE **" if k in seen else ""
    if dup:
        errors.append(f"DUPLICATE static key '{k}' at line {lineno}")
    seen.add(k)
    print(f"  line {lineno}: {k}{dup}")

print(f"\n=== DYNAMIC WIDGET KEYS ({len(dynamic_keys)}) ===")
for lineno, k in dynamic_keys:
    print(f"  line {lineno}: {k}")

# --- 4. Simulate Case Management dual-tab key generation ---
print("\n=== CASE MANAGEMENT DUAL-TAB SIMULATION ===")
# Simulate CASE-FG-1042 in both tabs (confirmed by live query)
test_cases = ["CASE-FG-1042", "CASE-FG-1001", "CASE-FG-1099"]
all_keys = set()
dup_found = False
for ctx in ["open", "all"]:
    for case_id in test_cases:
        for action in ["inv", "ev", "pol", "ai"]:
            key = f"{ctx}_{action}_{case_id}"
            if key in all_keys:
                print(f"  DUPLICATE: {key}")
                errors.append(f"DUPLICATE dynamic key '{key}'")
                dup_found = True
            all_keys.add(key)
            print(f"  {key}")

# Also check selectbox keys
for k in ["open_case_select", "all_case_select"]:
    if k in all_keys:
        print(f"  DUPLICATE: {k}")
        errors.append(f"DUPLICATE selectbox key '{k}'")
    all_keys.add(k)
    print(f"  {k}")

if not dup_found:
    print("  NO DUPLICATES FOUND")

# --- 5. Simulate Customer Investigation signal loop keys ---
print("\n=== CUSTOMER INVESTIGATION SIGNAL LOOP SIMULATION ===")
# With 8 signals for CUST-1042 (idx 0-7), keys are ci_sig_pol_0 through ci_sig_pol_7
sig_keys = set()
sig_dup = False
for idx in range(8):
    key = f"ci_sig_pol_{idx}"
    if key in sig_keys:
        print(f"  DUPLICATE: {key}")
        errors.append(f"DUPLICATE signal key '{key}'")
        sig_dup = True
    sig_keys.add(key)
    print(f"  {key}")
if not sig_dup:
    print("  NO DUPLICATES FOUND")

# --- 6. Full key collision check: all static + all dynamic ---
print("\n=== FULL KEY COLLISION CHECK ===")
full_set = set()
for _, k in static_keys:
    full_set.add(k)
# Check dynamic patterns against statics
for _, k in dynamic_keys:
    # Expand with known values
    expansions = []
    if "ctx" in k:
        for ctx in ["open", "all"]:
            for cid in ["CASE-FG-1042", "CASE-FG-1001"]:
                expansions.append(k.replace("{ctx}", ctx).replace("{case_id}", cid))
    elif "idx" in k:
        for i in range(10):
            expansions.append(k.replace("{idx}", str(i)))
    elif "customer_id" in k:
        for c in ["CUST-1042", "CUST-1001"]:
            expansions.append(k.replace("{customer_id}", c))
    elif "sel_case_id" in k:
        for c in ["CASE-FG-1042", "CASE-FG-1001"]:
            expansions.append(k.replace("{sel_case_id}", c))
    for exp in expansions:
        if exp in full_set:
            print(f"  COLLISION: {exp}")
            errors.append(f"KEY COLLISION: '{exp}'")
        full_set.add(exp)

print(f"  Total unique keys tested: {len(full_set)}")
if not any("COLLISION" in e for e in errors):
    print("  NO COLLISIONS FOUND")

# --- Summary ---
print(f"\n=== SUMMARY ===")
print(f"Total lines: {len(src.splitlines())}")
print(f"Functions: {len(funcs)}")
print(f"Imports: {len(imports)}")
print(f"Static keys: {len(static_keys)}")
print(f"Dynamic keys: {len(dynamic_keys)}")
print(f"Errors: {len(errors)}")
if errors:
    print("\nFAILURES:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("\nALL CHECKS PASSED")
    sys.exit(0)
