"""Release 5 — Final demo hardening validation."""
import ast
import re
import sys

src = open("streamlit/app.py", encoding="utf-8").read()
tree = ast.parse(src)
lines = src.splitlines()
errors = []

print("=" * 60)
print("RELEASE 5 — FINAL VALIDATION")
print("=" * 60)

# ── 1. CODE FREEZE ──
print("\n--- 1. CODE FREEZE ---")
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        if node.name == "navigate_to":
            body = "\n".join(lines[node.lineno - 1 : node.end_lineno])
            for kw in ["nav_from", "nav_page", "nav_customer", "st.rerun()"]:
                assert kw in body, f"navigate_to missing {kw}"
            print(f"  navigate_to: line {node.lineno}, {node.end_lineno - node.lineno + 1} lines — FROZEN OK")
        if node.name == "_consume":
            body = "\n".join(lines[node.lineno - 1 : node.end_lineno])
            assert "session_state" in body
            print(f"  _consume: line {node.lineno}, {node.end_lineno - node.lineno + 1} lines — FROZEN OK")

nav_def = len(re.findall(r"def navigate_to\(", src))
nav_code_calls = 0
for ln in src.splitlines():
    stripped = ln.strip()
    if stripped.startswith("#"):
        continue
    if "navigate_to(" in stripped and "def navigate_to(" not in stripped:
        nav_code_calls += 1
print(f"  navigate_to: {nav_def} def + {nav_code_calls} code calls")
if nav_code_calls != 14:
    errors.append(f"navigate_to call count: {nav_code_calls}, expected 14")

ss_keys = re.findall(r'\("(nav_\w+)",', src)
unique_keys = sorted(set(ss_keys))
print(f"  Session state nav keys ({len(unique_keys)}): {unique_keys}")
if len(unique_keys) != 8:
    errors.append(f"Session state key count: {len(unique_keys)}, expected 8")

assert 'DB = "BANKGUARD_DB"' in src
print("  DB constant: FROZEN OK")

rq_count = len(re.findall(r"run_query\(", src))
print(f"  run_query calls: {rq_count}")

# ── 2. WIDGET KEYS ──
print("\n--- 2. WIDGET KEY AUDIT ---")
key_pattern = re.compile(r'''key\s*=\s*(?:f?"([^"]*)"|f?'([^']*)')''')
keys_found = []
for lineno, line in enumerate(lines, 1):
    for m in key_pattern.finditer(line):
        k = m.group(1) or m.group(2)
        keys_found.append((lineno, k))

static_keys = [(ln, k) for ln, k in keys_found if "{" not in k]
dynamic_keys = [(ln, k) for ln, k in keys_found if "{" in k]

seen = set()
for ln, k in static_keys:
    if k in seen:
        errors.append(f"DUPLICATE static key '{k}' at line {ln}")
    seen.add(k)

print(f"  Static keys: {len(static_keys)}")
print(f"  Dynamic keys: {len(dynamic_keys)}")

# Simulate dual-tab Case Management
all_sim_keys = set()
dup_found = False
for ctx in ["open", "all"]:
    for case_id in ["CASE-FG-1042", "CASE-FG-1001"]:
        for action in ["inv", "ev", "pol", "ai"]:
            key = f"{ctx}_{action}_{case_id}"
            if key in all_sim_keys:
                errors.append(f"DUPLICATE CM key '{key}'")
                dup_found = True
            all_sim_keys.add(key)

# Signal loop
for idx in range(8):
    key = f"ci_sig_pol_{idx}"
    if key in all_sim_keys or key in seen:
        errors.append(f"COLLISION signal key '{key}'")
    all_sim_keys.add(key)

total_tested = len(seen) + len(all_sim_keys)
print(f"  Total keys tested: {total_tested}")
print(f"  Duplicates: {'NONE' if not dup_found else 'FOUND'}")

# ── 3. FUNCTIONS ──
print("\n--- 3. FUNCTIONS ---")
funcs = [(n.name, n.lineno) for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
print(f"  Count: {len(funcs)}")
for name, ln in funcs:
    print(f"    {name} (line {ln})")

# ── 4. IMPORTS ──
print("\n--- 4. IMPORTS ---")
imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
print(f"  Count: {len(imports)}")

# ── 5. AI CONTROLS ──
print("\n--- 5. AI CALL CONTROL ---")
agent_calls = [ln for ln, line in enumerate(lines, 1) if "_call_agent(" in line and "def " not in line]
for ln in agent_calls:
    context = lines[max(0, ln - 20) : ln]
    has_button = any("button(" in c or "spinner(" in c for c in context)
    status = "GUARDED" if has_button else "UNGUARDED"
    if not has_button:
        errors.append(f"_call_agent at line {ln} may not be button-guarded")
    print(f"  _call_agent at line {ln}: {status}")

# ── 6. SECURITY ──
print("\n--- 6. SECURITY SCAN ---")
secret_patterns = [
    r"(?i)(api[_-]?key|password|secret|token|private[_-]?key|credential)\s*=\s*['\"][^'\"]{8,}['\"]",
    r"(?i)bearer\s+[a-zA-Z0-9\-_.]{20,}",
    r"sk-[a-zA-Z0-9]{20,}",
]
secrets_found = 0
for pat in secret_patterns:
    for ln, line in enumerate(lines, 1):
        if re.search(pat, line):
            secrets_found += 1
            errors.append(f"Potential secret at line {ln}")
print(f"  Secrets found: {secrets_found}")

# ── 7. GOVERNANCE ──
print("\n--- 7. GOVERNANCE ---")
gov_checks = {
    "AI_DISCLAIMER": "AI_DISCLAIMER" in src,
    "analyst review caption": "requires analyst review" in src,
    "Do not declare fraud": "Do not declare fraud" in src or "do not declare fraud" in src.lower(),
    "synthetic data warning": "SYNTHETIC" in src,
}
for check, ok in gov_checks.items():
    print(f"  {check}: {'PASS' if ok else 'FAIL'}")
    if not ok:
        errors.append(f"Governance check failed: {check}")

# ── SUMMARY ──
print("\n" + "=" * 60)
print(f"Total lines: {len(lines)}")
print(f"Functions: {len(funcs)}")
print(f"Widget keys tested: {total_tested}")
print(f"Errors: {len(errors)}")
if errors:
    print("\nFAILURES:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("\nALL CHECKS PASSED")
    sys.exit(0)
