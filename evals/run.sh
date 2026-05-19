#!/usr/bin/env bash
# evals/run.sh — minimal eval runner.
#
# Iterates over case folders under evals/{ingest,lint,query}/, runs the
# deterministic checks each case supports, and writes one JSON file
# under evals/results/. Prints a summary on stdout.
#
# Usage:
#   ./evals/run.sh                    # all skills, all cases
#   ./evals/run.sh ingest             # one skill, all cases
#   ./evals/run.sh lint case-001-*    # specific glob within a skill
#
# Exit codes:
#   0  ok (some cases may have failed — see JSON)
#   2  no cases matched
#   3  runner error
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

SKILL_FILTER="${1:-}"
CASE_FILTER="${2:-}"

mkdir -p evals/results
TIMESTAMP="$(date -u +"%Y-%m-%dT%H-%M-%SZ")"
RESULTS_JSON="evals/results/${TIMESTAMP}.json"
RESULTS_MD="evals/results/${TIMESTAMP}.md"

discover_cases() {
    local skill="$1"
    local pattern="${2:-*}"
    find "evals/${skill}" -maxdepth 1 -type d -name "${pattern}" 2>/dev/null \
        | grep -v "^evals/${skill}\$" \
        | sort
}

run_lint_case() {
    local case_dir="$1"
    local vault="${case_dir}/vault"
    local expected="${case_dir}/expected-findings.json"

    if [ ! -d "$vault" ] || [ ! -f "$expected" ]; then
        printf '{"case":"%s","skill":"lint","status":"skipped","reason":"missing vault/ or expected-findings.json"}' "$case_dir"
        return
    fi

    local actual
    actual=$(python3 scripts/lint-terminology.py "$vault" --json 2>/dev/null || echo "[]")

    python3 - "$expected" "$actual" "$case_dir" <<'PY'
import json, sys
expected_path, actual_str, case = sys.argv[1], sys.argv[2], sys.argv[3]
expected = json.loads(open(expected_path).read())
actual = json.loads(actual_str)

def matches(exp, act):
    return all(
        (k == "path" and v in act.get("path", "")) or act.get(k) == v
        for k, v in exp.items()
    )

found = sum(1 for e in expected if any(matches(e, a) for a in actual))
recall = found / len(expected) if expected else 1.0
extras = [a for a in actual if not any(matches(e, a) for e in expected)]
false_pos = len(extras) / len(actual) if actual else 0.0

status = "ok" if recall == 1.0 and false_pos == 0.0 else "fail"
print(json.dumps({
    "case": case,
    "skill": "lint",
    "status": status,
    "metrics": {
        "recall": round(recall, 3),
        "false_positive_rate": round(false_pos, 3),
        "expected_findings": len(expected),
        "actual_findings": len(actual),
    },
    "extras": extras[:5],
}))
PY
}

run_manual_case() {
    local case_dir="$1"
    local skill="$2"
    local meta="${case_dir}/case.json"
    if [ ! -f "$meta" ]; then
        printf '{"case":"%s","skill":"%s","status":"skipped","reason":"no case.json"}' "$case_dir" "$skill"
        return
    fi
    printf '{"case":"%s","skill":"%s","status":"manual","reason":"requires live agent run"}' "$case_dir" "$skill"
}

declare -a SKILLS
if [ -z "$SKILL_FILTER" ]; then
    SKILLS=(ingest lint query)
else
    SKILLS=("$SKILL_FILTER")
fi

# Build the JSON array by appending into the results file.
{
    echo "["
    FIRST=1
    for skill in "${SKILLS[@]}"; do
        if [ ! -d "evals/${skill}" ]; then
            continue
        fi
        while IFS= read -r case_dir; do
            if [ $FIRST -eq 0 ]; then echo ","; fi
            FIRST=0
            case "$skill" in
                lint)   run_lint_case   "$case_dir" ;;
                ingest) run_manual_case "$case_dir" "ingest" ;;
                query)  run_manual_case "$case_dir" "query" ;;
            esac
        done < <(discover_cases "$skill" "${CASE_FILTER:-*}")
    done
    echo
    echo "]"
} > "$RESULTS_JSON"

python3 evals/score-summary.py "$RESULTS_JSON" > "$RESULTS_MD" || true

echo "Wrote $RESULTS_JSON"
echo "Wrote $RESULTS_MD"
cat "$RESULTS_MD"
