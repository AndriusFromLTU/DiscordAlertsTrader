# Quick Reference: Testing Different Dates

## Single Date Test

```bash
# Test default date (2025-11-11)
.venv/bin/python tests/test_full_flow_bear_to_ibkr.py

# Test specific date
.venv/bin/python tests/test_full_flow_bear_to_ibkr.py 2025-11-12

# With verbose output
.venv/bin/python tests/test_full_flow_bear_to_ibkr.py 2025-11-12 -v
```

## Multiple Dates Test

```bash
# Using the helper script (tests available dates)
./tests/test_multiple_days.sh

# Test specific dates
./tests/test_multiple_days.sh 2025-11-11 2025-11-12 2025-11-13

# Loop through dates manually
for date in 2025-11-11 2025-11-12; do
    echo "Testing $date..."
    .venv/bin/python tests/test_full_flow_bear_to_ibkr.py $date
done
```

## What You'll See

### Header showing the date being tested:
```
================================================================================
Testing Bear Alerts for Date: 2025-11-12
Message File: bear_messages_2025-11-12.json
Total Messages: 48
================================================================================
```

### IBKR commands generated for each alert:
```
Command 3:
  Action: send_order
  Order Type: LMT
  Action: BUY
  Quantity: 1
  Limit Price: $0.84
  Asset: OPT
  Order ID: 1000
```

### Summary at the end:
```
Summary:
  Processed: 5
  Skipped: 5
  Total Commands: 23
```

## Available Dates

To see which dates have message files:
```bash
ls tests/data/bear_messages_*.json
```

## Typical Workflow

1. **Fetch messages for a date** (if you have the Bear message fetcher)
2. **Run the test for that date:**
   ```bash
   .venv/bin/python tests/test_full_flow_bear_to_ibkr.py 2025-11-XX
   ```
3. **Review the output** to see:
   - Which alerts were parsed successfully
   - What IBKR commands would have been executed
   - Any alerts that failed to parse

4. **Compare across days:**
   ```bash
   ./tests/test_multiple_days.sh 2025-11-11 2025-11-12 2025-11-13
   ```

## Troubleshooting

**Date file not found?**
```
FileNotFoundError: No Bear messages file found for date 2025-11-13.
Available dates: 2025-11-12, 2025-11-11
```
→ The test helpfully shows you which dates are available

**Want to add a new date?**
1. Create `tests/data/bear_messages_YYYY-MM-DD.json` with the message data
2. Run the test with that date

## Tips

- **Focus on specific test:** Add the test name after the date isn't supported with current setup, use pytest instead
- **Save output to file:** Redirect output to analyze later:
  ```bash
  .venv/bin/python tests/test_full_flow_bear_to_ibkr.py 2025-11-12 > results_11-12.txt 2>&1
  ```
- **Compare days:** Save outputs for different days and diff them
  ```bash
  .venv/bin/python tests/test_full_flow_bear_to_ibkr.py 2025-11-11 > day1.txt 2>&1
  .venv/bin/python tests/test_full_flow_bear_to_ibkr.py 2025-11-12 > day2.txt 2>&1
  diff day1.txt day2.txt
  ```
