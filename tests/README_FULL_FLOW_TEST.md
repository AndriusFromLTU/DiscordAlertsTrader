# Full Flow Integration Test: Bear Discord Alerts → IBKR Commands

## Overview

This test (`test_full_flow_bear_to_ibkr.py`) provides end-to-end integration testing of the complete trading flow from Discord message ingestion to IBKR brokerage command generation.

**Key Feature**: Test different dates by passing them as command-line arguments, making it easy to analyze how each day's alerts were processed.

## What It Tests

The test validates the entire pipeline:

1. **Discord Message Parsing** - Loads real Bear channel messages from JSON files
2. **Server-Specific Formatting** - Applies Bear alert formatting transformations
3. **Trade Alert Parsing** - Extracts trade details (BTO/STC, symbol, price, etc.)
4. **AlertsTrader Processing** - Routes through full trader logic
5. **IBKR Command Generation** - Produces broker-specific order commands

## Test Structure

### Mock IBKR Broker

The test uses a `MockIBKRBroker` that:
- Records all commands sent to it
- Returns success responses for all operations
- Implements the full IBKR API interface:
  - `make_BTO_lim_order()` - Create buy-to-open limit orders
  - `make_STC_lim()` - Create sell-to-close limit orders
  - `make_Lim_SL_order()` - Create orders with profit targets and stop losses
  - `make_STC_SL()` - Create stop loss orders
  - `send_order()` - Submit orders (returns mock success)
  - `get_quotes()` - Get market quotes (returns mock prices)
  - `get_order_info()` - Get order status (returns FILLED)

### Test Cases

1. **test_full_flow_single_message**
   - Processes one Bear alert through complete flow
   - Validates message parsing and order creation
   - Verifies IBKR commands are generated

2. **test_full_flow_multiple_messages**
   - Processes up to 10 Bear alerts sequentially
   - Tests handling of mixed BTO/STC messages
   - Shows comprehensive command output

3. **test_full_flow_bto_stc_sequence**
   - Tests opening and closing position sequence
   - Validates BTO followed by STC for same symbol

4. **test_command_structure**
   - Validates IBKR command structure
   - Checks required fields: action, orderType, quant, asset, conId
   - Ensures data types and values are correct

## Input Data

Uses JSON files from `tests/data/`:
- `bear_messages_2025-11-11.json`
- `bear_messages_2025-11-12.json`

These contain real Discord message data including:
- Message metadata (author, timestamp, channel)
- Embedded content (title, description)
- Trade alerts (entry, exits, notes)

## Output

The test prints detailed information about:

### Command Execution
```
Command 1:
  Action: get_quotes
  Symbols: QQQ_111125C623

Command 2:
  Action: make_BTO_lim_order
  Symbol: QQQ_111125C623
  Quantity: 1
  Price: $0.84
  Order Action: BTO

Command 3:
  Action: send_order
  Order Type: LMT
  Action: BUY
  Quantity: 1
  Limit Price: $0.84
  Asset: OPT
  Order ID: 1000
```

### Summary Statistics
- Total commands sent
- Number of successful/failed parses
- BTO vs STC command counts

## Running the Test

### Basic Usage

```bash
# Run with default date (2025-11-11)
.venv/bin/python tests/test_full_flow_bear_to_ibkr.py

# Test a specific date
.venv/bin/python tests/test_full_flow_bear_to_ibkr.py 2025-11-12

# Test another date
.venv/bin/python tests/test_full_flow_bear_to_ibkr.py 2025-11-13

# Show help
.venv/bin/python tests/test_full_flow_bear_to_ibkr.py --help

# Run with verbose output
.venv/bin/python tests/test_full_flow_bear_to_ibkr.py 2025-11-12 -v
```

### Using pytest

```bash
# Note: When using pytest, set the date via environment or modify the TEST_DATE global
.venv/bin/pytest tests/test_full_flow_bear_to_ibkr.py -v

# Run specific test
.venv/bin/pytest tests/test_full_flow_bear_to_ibkr.py::TestFullFlowBearToIBKR::test_full_flow_single_message -v
```

### Date Parameter

The test accepts a date in `YYYY-MM-DD` format:
- If no date is provided, defaults to `2025-11-11`
- The test looks for message files named `bear_messages_YYYY-MM-DD.json` in the `tests/data/` directory
- If the date file doesn't exist, you'll get a helpful error message showing available dates

**Example Error Message:**
```
FileNotFoundError: No Bear messages file found for date 2025-11-13.
Looking for: /path/to/tests/data/bear_messages_2025-11-13.json
Available dates: 2025-11-12, 2025-11-11
```

### Testing Multiple Days

You can easily test multiple days in sequence:

```bash
# Test all available days
for date in 2025-11-11 2025-11-12 2025-11-13; do
    echo "Testing date: $date"
    .venv/bin/python tests/test_full_flow_bear_to_ibkr.py $date
    echo "---"
done
```

## Configuration

The test uses these config overrides:
```python
cfg["order_configs"]["max_trade_capital"] = "{'default': 10000}"
cfg["order_configs"]["default_bto_qty"] = "{'default': 'buy_one'}"
cfg["order_configs"]["trade_capital"] = "{'default': 1000}"
cfg["general"]["DO_BTO_TRADES"] = "true"
cfg["general"]["DO_STC_TRADES"] = "true"
```

## Benefits

1. **Full Integration Testing** - Tests entire pipeline, not isolated components
2. **Real Data** - Uses actual Discord messages from production
3. **Reproducible** - Runs offline with saved message data
4. **Command Visibility** - Shows exactly what would be sent to IBKR
5. **Safe** - No actual trades executed (mock broker)

## Future Enhancements

- [ ] Test profit target and stop loss handling
- [ ] Test position averaging scenarios
- [ ] Test error handling (rejected orders, etc.)
- [ ] Add more analysts/servers beyond Bear
- [ ] Test STC with price = 0 (no price specified)
- [ ] Test trailing stops
- [ ] Validate portfolio state after trades

## Example Output

When running the test, you'll see a clear header showing which date is being tested:

```
================================================================================
Testing Bear Alerts for Date: 2025-11-12
Message File: bear_messages_2025-11-12.json
Total Messages: 48
================================================================================

================================================================================
TEST: Single Message Flow
================================================================================

Original Message:
  Author: Bear's Bot#5893
  Date: 2025-11-11 14:30:45.359000+00:00
  Embed Title: Daytrade
  Embed Description: Contract:  **QQQ 11/11 623C**...

Formatted Content:
  BTO QQQ 623C 11/11 @0.84 Daytrade

Parsed Order:
  Action: BTO
  Symbol: QQQ_111125C623
  Asset: option
  Quantity: None
  Price: 0.84

Sent order BTO 1 QQQ_111125C623 @0.84
BTO QQQ_111125C623 sent @ 0.84. Status: FILLED

================================================================================
IBKR BROKERAGE COMMANDS
================================================================================

Command 1:
  Action: get_quotes
  Symbols: QQQ_111125C623

Command 2:
  Action: make_BTO_lim_order
  Symbol: QQQ_111125C623
  Quantity: 1
  Price: $0.84
  Order Action: BTO

Command 3:
  Action: send_order
  Order Type: LMT
  Action: BUY
  Quantity: 1
  Limit Price: $0.84
  Asset: OPT
  Order ID: 1000

Command 4:
  Action: get_order_info
  Order ID: 1000

================================================================================
Total Commands: 4
================================================================================

✓ Test passed: Message processed successfully
```
