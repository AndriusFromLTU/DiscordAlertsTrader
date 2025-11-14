#!/bin/bash
# Test multiple days of Bear alerts
# Usage: ./test_multiple_days.sh [date1] [date2] ...
# Example: ./test_multiple_days.sh 2025-11-11 2025-11-12

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEST_SCRIPT="$PROJECT_ROOT/tests/test_full_flow_bear_to_ibkr.py"

# Default dates if none provided
if [ $# -eq 0 ]; then
    DATES=("2025-11-11" "2025-11-12")
else
    DATES=("$@")
fi

echo "========================================================================"
echo "Testing Bear Alerts to IBKR Flow - Multiple Days"
echo "========================================================================"
echo ""

TOTAL_TESTS=${#DATES[@]}
PASSED=0
FAILED=0

for date in "${DATES[@]}"; do
    echo "========================================================================"
    echo "Testing Date: $date"
    echo "========================================================================"
    
    if .venv/bin/python "$TEST_SCRIPT" "$date" 2>&1 | grep -q "OK"; then
        echo "✓ $date - PASSED"
        ((PASSED++))
    else
        echo "✗ $date - FAILED"
        ((FAILED++))
    fi
    echo ""
done

echo "========================================================================"
echo "Summary"
echo "========================================================================"
echo "Total Dates Tested: $TOTAL_TESTS"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "========================================================================"

if [ $FAILED -gt 0 ]; then
    exit 1
fi
