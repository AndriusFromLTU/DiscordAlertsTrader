#!/usr/bin/env python3
"""
Full flow integration test: Bear Discord messages -> IBKR brokerage commands
Tests the complete pipeline from parsing Discord messages to generating IBKR orders

Usage:
    python test_full_flow_bear_to_ibkr.py [YYYY-MM-DD]

    If no date provided, defaults to 2025-11-11

Examples:
    python test_full_flow_bear_to_ibkr.py 2025-11-12
    python test_full_flow_bear_to_ibkr.py
"""

import argparse
import json
import os
import queue
import sys
import unittest
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from DiscordAlertsTrader.alerts_trader import AlertsTrader
from DiscordAlertsTrader.configurator import cfg
from DiscordAlertsTrader.message_parser import parse_trade_alert
from DiscordAlertsTrader.server_alert_formatting import bear_alerts

# Global variable to store the test date
TEST_DATE = "2025-11-11"  # Default date


class MockEmbedAuthor:
    """Mock embed author object matching discord.py structure"""

    def __init__(self, data):
        if data is None:
            self.name = None
            self.discriminator = "0"
            self.id = 0
            self.bot = False
        else:
            self.name = data.get("name")
            self.discriminator = "0"
            self.id = 0
            self.bot = False
            self.url = data.get("url")


class MockEmbedField:
    def __init__(self, data):
        self.name = data.get("name", "")
        self.value = data.get("value", "")


class MockEmbed:
    def __init__(self, data):
        self.title = data.get("title")
        self.description = data.get("description")
        author_data = data.get("author")
        self.author = MockEmbedAuthor(author_data)
        self.fields = [MockEmbedField(f) for f in data.get("fields", [])]


class MockAuthor:
    def __init__(self, data):
        self.name = data.get("name", "")
        self.discriminator = data.get("discriminator", "0")
        self.id = data.get("id", 0)
        self.bot = data.get("bot", False)


class MockChannel:
    def __init__(self, channel_id):
        self.id = channel_id


class MockGuild:
    def __init__(self, guild_id=979906463487103006):
        self.id = guild_id
        self.name = "Bear's Trading Server"


class MockMessage:
    def __init__(self, data):
        self.id = data.get("id")
        self.author = MockAuthor(data.get("author", {}))
        self.content = data.get("content", "")
        self.created_at = datetime.fromisoformat(data.get("created_at"))
        self.channel = MockChannel(data.get("channel_id"))
        self.guild = MockGuild()
        self.embeds = [MockEmbed(e) for e in data.get("embeds", [])]


class MockIBKRBroker:
    """Mock IBKR broker that records commands and returns success responses"""

    def __init__(self):
        self.name = "ibkr"
        self.accountId = "TEST_ACCOUNT"
        self.commands = []  # Store all commands sent to broker
        self.order_counter = 1000

    def get_session(self):
        self.commands.append({"action": "get_session"})
        return True

    def get_quotes(self, symbols):
        """Mock get_quotes - return realistic option prices"""
        self.commands.append({"action": "get_quotes", "symbols": symbols})
        quotes = {}
        for symbol in symbols:
            # Return mock bid/ask prices
            quotes[symbol] = {
                "askPrice": 1.50,
                "bidPrice": 1.45,
                "lastPrice": 1.48,
                "description": "Mock Option",
            }
        return quotes

    def make_BTO_lim_order(self, Symbol, Qty, price, action="BTO", **kwargs):
        """Mock make_BTO_lim_order - creates order kwargs dict"""
        order_kwargs = {
            "action": "BUY" if action == "BTO" else "SELL",
            "asset": "OPT" if "_" in Symbol else "STK",
            "enforce": "GTC",
            "quant": Qty,
            "orderType": "LMT",
            "lmtPrice": price,
            "conId": 12345,  # Mock contract ID
        }
        self.commands.append(
            {
                "action": "make_BTO_lim_order",
                "symbol": Symbol,
                "quantity": Qty,
                "price": price,
                "order_action": action,
                "kwargs": order_kwargs,
            }
        )
        return order_kwargs

    def make_STC_lim(self, Symbol, Qty, price, strike=None, action="STC", **kwargs):
        """Mock make_STC_lim - creates STC limit order kwargs"""
        order_kwargs = {
            "action": "SELL" if action == "STC" else "BUY",
            "asset": "OPT" if "_" in Symbol else "STK",
            "enforce": "GTC",
            "quant": Qty,
            "orderType": "LMT",
            "lmtPrice": price,
            "conId": 12345,  # Mock contract ID
        }
        self.commands.append(
            {
                "action": "make_STC_lim",
                "symbol": Symbol,
                "quantity": Qty,
                "price": price,
                "order_action": action,
                "kwargs": order_kwargs,
            }
        )
        return order_kwargs

    def make_Lim_SL_order(self, Symbol, Qty, PT, SL, action="STC", **kwargs):
        """Mock make_Lim_SL_order - creates limit + stop loss order"""
        order_kwargs = {
            "action": "SELL" if action == "STC" else "BUY",
            "asset": "OPT" if "_" in Symbol else "STK",
            "enforce": "GTC",
            "quant": Qty,
            "orderType": "OCA",
            "takeProfit": PT,
            "stopLoss": SL,
            "conId": 12345,  # Mock contract ID
        }
        self.commands.append(
            {
                "action": "make_Lim_SL_order",
                "symbol": Symbol,
                "quantity": Qty,
                "PT": PT,
                "SL": SL,
                "order_action": action,
                "kwargs": order_kwargs,
            }
        )
        return order_kwargs

    def make_STC_SL(self, Symbol, Qty, SL, action="STC", **kwargs):
        """Mock make_STC_SL - creates stop loss order"""
        order_kwargs = {
            "action": "SELL" if action == "STC" else "BUY",
            "asset": "OPT" if "_" in Symbol else "STK",
            "enforce": "GTC",
            "quant": Qty,
            "orderType": "STP",
            "stpPrice": SL,
            "lmtPrice": SL,
            "conId": 12345,  # Mock contract ID
        }
        self.commands.append(
            {
                "action": "make_STC_SL",
                "symbol": Symbol,
                "quantity": Qty,
                "SL": SL,
                "order_action": action,
                "kwargs": order_kwargs,
            }
        )
        return order_kwargs

    def send_order(self, order_dict=None, **kwargs):
        """Mock send_order - record command and return success

        IBKR-style: accepts order_dict with keys like 'action', 'quant', 'orderType', etc.
        """
        if order_dict is None:
            order_dict = kwargs

        order_id = self.order_counter
        self.order_counter += 1

        command = {
            "action": "send_order",
            "order_dict": order_dict,
            "order_id": order_id,
        }
        self.commands.append(command)

        # Return success status and order ID (IBKR style)
        return "WORKING", order_id

    def get_order_info(self, order_id):
        """Mock get_order_info - return filled order status"""
        self.commands.append({"action": "get_order_info", "order_id": order_id})

        # Find the original order
        orig_order = None
        for cmd in self.commands:
            if cmd.get("action") == "send_order" and cmd.get("order_id") == order_id:
                orig_order = cmd
                break

        if orig_order:
            status = "FILLED"
            order_dict = orig_order.get("order_dict", {})
            order_info = {
                "quantity": order_dict.get("quant", 1),
                "price": order_dict.get("lmtPrice", 1.50),
                "filledQuantity": order_dict.get("quant", 1),
                "status": status,
                "orderLegCollection": [
                    {
                        "instrument": {"symbol": "MOCK_SYMBOL"},
                        "instruction": order_dict.get("action", "BUY"),
                    }
                ],
            }
            return [status, order_info]
        else:
            return ["UNKNOWN", {}]

    def cancel_order(self, order_id):
        """Mock cancel_order"""
        self.commands.append({"action": "cancel_order", "order_id": order_id})
        return True

    def get_orders(self):
        """Mock get_orders - return list of orders"""
        self.commands.append({"action": "get_orders"})
        return []

    def print_commands(self):
        """Print all commands sent to broker in a readable format"""
        print("\n" + "=" * 80)
        print("IBKR BROKERAGE COMMANDS")
        print("=" * 80)

        for i, cmd in enumerate(self.commands, 1):
            print(f"\nCommand {i}:")
            print(f"  Action: {cmd['action']}")

            if cmd["action"] == "send_order":
                order_dict = cmd.get("order_dict", {})
                print(f"  Order Type: {order_dict.get('orderType', 'N/A')}")
                print(f"  Action: {order_dict.get('action', 'N/A')}")
                print(f"  Quantity: {order_dict.get('quant', 'N/A')}")
                if order_dict.get("lmtPrice"):
                    print(f"  Limit Price: ${order_dict['lmtPrice']:.2f}")
                if order_dict.get("stpPrice"):
                    print(f"  Stop Price: ${order_dict['stpPrice']:.2f}")
                if order_dict.get("takeProfit"):
                    print(f"  Take Profit: ${order_dict['takeProfit']:.2f}")
                if order_dict.get("stopLoss"):
                    print(f"  Stop Loss: ${order_dict['stopLoss']:.2f}")
                print(f"  Asset: {order_dict.get('asset', 'N/A')}")
                print(f"  Order ID: {cmd['order_id']}")

            elif cmd["action"] == "make_BTO_lim_order":
                print(f"  Symbol: {cmd['symbol']}")
                print(f"  Quantity: {cmd['quantity']}")
                print(f"  Price: ${cmd['price']:.2f}")
                print(f"  Order Action: {cmd['order_action']}")

            elif cmd["action"] == "make_STC_lim":
                print(f"  Symbol: {cmd['symbol']}")
                print(f"  Quantity: {cmd['quantity']}")
                print(f"  Price: ${cmd['price']:.2f}")
                print(f"  Order Action: {cmd['order_action']}")

            elif cmd["action"] == "make_Lim_SL_order":
                print(f"  Symbol: {cmd['symbol']}")
                print(f"  Quantity: {cmd['quantity']}")
                print(f"  Profit Target: ${cmd['PT']:.2f}")
                print(f"  Stop Loss: ${cmd['SL']:.2f}")
                print(f"  Order Action: {cmd['order_action']}")

            elif cmd["action"] == "make_STC_SL":
                print(f"  Symbol: {cmd['symbol']}")
                print(f"  Quantity: {cmd['quantity']}")
                print(f"  Stop Loss: ${cmd['SL']:.2f}")
                print(f"  Order Action: {cmd['order_action']}")

            elif cmd["action"] == "get_quotes":
                print(f"  Symbols: {', '.join(cmd['symbols'])}")

            elif cmd["action"] == "get_order_info":
                print(f"  Order ID: {cmd['order_id']}")

            elif cmd["action"] == "cancel_order":
                print(f"  Order ID: {cmd['order_id']}")

        print("\n" + "=" * 80)
        print(f"Total Commands: {len(self.commands)}")
        print("=" * 80 + "\n")


class TestFullFlowBearToIBKR(unittest.TestCase):
    """Test complete flow from Bear Discord messages to IBKR commands"""

    @classmethod
    def setUpClass(cls):
        """Load Bear messages from JSON file based on TEST_DATE"""
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.data_dir = os.path.join(cls.test_dir, "data")
        cls.test_date = TEST_DATE

        # Load messages file for the specified date
        message_file = os.path.join(cls.data_dir, f"bear_messages_{cls.test_date}.json")

        if not os.path.exists(message_file):
            # List available message files to help user
            available_files = [
                f
                for f in os.listdir(cls.data_dir)
                if f.startswith("bear_messages_") and f.endswith(".json")
            ]
            available_dates = [
                f.replace("bear_messages_", "").replace(".json", "")
                for f in available_files
            ]

            raise FileNotFoundError(
                f"No Bear messages file found for date {cls.test_date}.\n"
                f"Looking for: {message_file}\n"
                f"Available dates: {', '.join(available_dates) if available_dates else 'None'}"
            )

        with open(message_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            cls.messages_data = data.get("messages", [])
            cls.message_file = message_file

        print(f"\n{'=' * 80}")
        print(f"Testing Bear Alerts for Date: {cls.test_date}")
        print(f"Message File: {os.path.basename(message_file)}")
        print(f"Total Messages: {len(cls.messages_data)}")
        print(f"{'=' * 80}\n")

    def setUp(self):
        """Set up test fixtures before each test"""
        # Create temporary portfolio files
        self.test_portfolio = os.path.join(
            self.test_dir, "data", "test_flow_portfolio.csv"
        )
        self.test_alerts_log = os.path.join(
            self.test_dir, "data", "test_flow_alerts_log.csv"
        )

        # Clean up any existing test files
        for f in [self.test_portfolio, self.test_alerts_log]:
            if os.path.exists(f):
                os.remove(f)

        # Configure for testing - use dictionary format for config values
        cfg["order_configs"]["max_trade_capital"] = "{'default': 10000}"
        cfg["order_configs"]["default_bto_qty"] = "{'default': 'buy_one'}"
        cfg["order_configs"]["trade_capital"] = "{'default': 1000}"
        cfg["discord"]["notify_alerts_to_discord"] = "false"
        cfg["general"]["DO_BTO_TRADES"] = "true"
        cfg["general"]["DO_STC_TRADES"] = "true"

        # Create mock broker
        self.mock_broker = MockIBKRBroker()

        # Create AlertsTrader with mock broker
        self.trader = AlertsTrader(
            brokerage=self.mock_broker,
            portfolio_fname=self.test_portfolio,
            alerts_log_fname=self.test_alerts_log,
            update_portfolio=False,
            queue_prints=queue.Queue(maxsize=50),
            cfg=cfg,
        )

    def tearDown(self):
        """Clean up after each test"""
        # Clean up test files
        for f in [self.test_portfolio, self.test_alerts_log]:
            if os.path.exists(f):
                os.remove(f)

    def test_full_flow_single_message(self):
        """Test processing a single Bear alert through to IBKR commands"""
        print("\n" + "=" * 80)
        print("TEST: Single Message Flow")
        print("=" * 80)

        # Find a trade message (BTO/Entry)
        trade_message = None
        for msg_data in self.messages_data:
            if msg_data.get("embeds"):
                embed = msg_data["embeds"][0]
                description = embed.get("description", "")
                if "Entry:" in description and "Contract:" in description:
                    trade_message = msg_data
                    break

        if not trade_message:
            self.skipTest("No trade message found in test data")

        # Create mock message object
        message = MockMessage(trade_message)

        print("\nOriginal Message:")
        print(f"  Author: {message.author.name}#{message.author.discriminator}")
        print(f"  Date: {message.created_at}")
        print(f"  Embed Title: {message.embeds[0].title}")
        print(f"  Embed Description: {message.embeds[0].description[:100]}...")

        # Apply Bear formatting
        formatted_message = bear_alerts(message)
        print("\nFormatted Content:")
        print(f"  {formatted_message.content}")

        # Parse the alert
        parsed, order = parse_trade_alert(formatted_message.content)

        self.assertIsNotNone(parsed, "Message should be parseable")
        self.assertIsNotNone(order, "Order should be extracted")

        print("\nParsed Order:")
        print(f"  Action: {order.get('action')}")
        print(f"  Symbol: {order.get('Symbol')}")
        print(f"  Asset: {order.get('asset')}")
        print(f"  Quantity: {order.get('Qty')}")
        print(f"  Price: {order.get('price')}")

        # Add trader info
        order["Trader"] = (
            f"{formatted_message.author.name}#{formatted_message.author.discriminator}"
        )
        order["Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        # Process through trader
        self.trader.new_trade_alert(order, parsed, formatted_message.content)

        # Print broker commands
        self.mock_broker.print_commands()

        # Verify commands were sent
        self.assertGreater(
            len(self.mock_broker.commands), 0, "Commands should be sent to broker"
        )

        # Check for send_order command
        send_order_cmds = [
            cmd for cmd in self.mock_broker.commands if cmd["action"] == "send_order"
        ]
        self.assertGreater(len(send_order_cmds), 0, "At least one order should be sent")

        print("\n✓ Test passed: Message processed successfully")

    def test_full_flow_multiple_messages(self):
        """Test processing multiple Bear alerts in sequence"""
        print("\n" + "=" * 80)
        print("TEST: Multiple Messages Flow")
        print("=" * 80)

        # Filter for trade messages only
        trade_messages = []
        for msg_data in self.messages_data:
            if msg_data.get("embeds"):
                embed = msg_data["embeds"][0]
                description = embed.get("description", "")
                title = embed.get("title", "")

                # Look for entry or exit keywords
                if any(
                    keyword in (description or "") or keyword in (title or "")
                    for keyword in [
                        "Entry:",
                        "Contract:",
                        "trimming",
                        "closing",
                        "Daytrade",
                        "LOTTO",
                        "Swing",
                    ]
                ):
                    trade_messages.append(msg_data)

        print(f"\nFound {len(trade_messages)} trade-related messages")

        processed_count = 0
        skipped_count = 0

        for i, msg_data in enumerate(trade_messages[:10], 1):  # Process first 10
            print(f"\n--- Processing Message {i}/{min(len(trade_messages), 10)} ---")

            # Create mock message
            message = MockMessage(msg_data)

            # Apply Bear formatting
            try:
                formatted_message = bear_alerts(message)
            except Exception as e:
                print(f"  ✗ Formatting failed: {e}")
                skipped_count += 1
                continue

            # Parse the alert
            parsed, order = parse_trade_alert(formatted_message.content)

            if not parsed or not order:
                print(f"  ✗ Could not parse: {formatted_message.content[:60]}...")
                skipped_count += 1
                continue

            print(f"  ✓ Parsed: {order.get('action')} {order.get('Symbol')}")

            # Add trader info
            order["Trader"] = (
                f"{formatted_message.author.name}#{formatted_message.author.discriminator}"
            )
            order["Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

            # Process through trader
            try:
                self.trader.new_trade_alert(order, parsed, formatted_message.content)
                processed_count += 1
            except Exception as e:
                print(f"  ✗ Trading failed: {e}")
                skipped_count += 1
                continue

        # Print all broker commands
        self.mock_broker.print_commands()

        print("\nSummary:")
        print(f"  Processed: {processed_count}")
        print(f"  Skipped: {skipped_count}")
        print(f"  Total Commands: {len(self.mock_broker.commands)}")

        # Verify some commands were sent
        self.assertGreater(
            len(self.mock_broker.commands),
            0,
            "Commands should be sent to broker for multiple messages",
        )

        print("\n✓ Test passed: Multiple messages processed successfully")

    def test_full_flow_bto_stc_sequence(self):
        """Test a complete BTO -> STC sequence"""
        print("\n" + "=" * 80)
        print("TEST: BTO -> STC Sequence")
        print("=" * 80)

        # Find BTO and STC messages for same symbol
        bto_message = None
        stc_message = None

        for msg_data in self.messages_data:
            if not msg_data.get("embeds"):
                continue

            message = MockMessage(msg_data)
            formatted = bear_alerts(message)
            parsed, order = parse_trade_alert(formatted.content)

            if not parsed or not order:
                continue

            if order.get("action") == "BTO" and not bto_message:
                bto_message = (message, formatted, parsed, order)
            elif order.get("action") == "STC" and bto_message and not stc_message:
                # Check if it's roughly the same underlying
                if bto_message[3].get("Symbol")[:3] == order.get("Symbol")[:3]:
                    stc_message = (message, formatted, parsed, order)
                    break

        if not bto_message:
            self.skipTest("Could not find BTO message in test data")

        # Process BTO
        print("\n1. Processing BTO:")
        _, formatted_msg, parsed, order = bto_message
        order["Trader"] = (
            f"{formatted_msg.author.name}#{formatted_msg.author.discriminator}"
        )
        order["Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(f"   {order['action']} {order['Symbol']} @ {order.get('price')}")

        self.trader.new_trade_alert(order, parsed, formatted_msg.content)

        bto_commands = len(self.mock_broker.commands)

        # Try to process STC if available
        if stc_message:
            print("\n2. Processing STC:")
            _, formatted_msg, parsed, order = stc_message
            order["Trader"] = (
                f"{formatted_msg.author.name}#{formatted_msg.author.discriminator}"
            )
            order["Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            print(f"   {order['action']} {order['Symbol']} @ {order.get('price')}")

            self.trader.new_trade_alert(order, parsed, formatted_msg.content)
            stc_commands = len(self.mock_broker.commands) - bto_commands
        else:
            print("\n2. No matching STC found - testing BTO only")
            stc_commands = 0

        # Print all commands
        self.mock_broker.print_commands()

        print("\nSequence Summary:")
        print(f"  BTO Commands: {bto_commands}")
        print(f"  STC Commands: {stc_commands}")
        print(f"  Total Commands: {len(self.mock_broker.commands)}")

        # Verify BTO sent orders
        send_order_cmds = [
            cmd for cmd in self.mock_broker.commands if cmd["action"] == "send_order"
        ]
        self.assertGreaterEqual(
            len(send_order_cmds), 1, "Should have at least BTO order"
        )

        print("\n✓ Test passed: BTO -> STC sequence completed successfully")

    def test_command_structure(self):
        """Test that IBKR commands have correct structure"""
        print("\n" + "=" * 80)
        print("TEST: Command Structure Validation")
        print("=" * 80)

        # Find a simple trade message
        for msg_data in self.messages_data:
            if not msg_data.get("embeds"):
                continue

            message = MockMessage(msg_data)
            formatted = bear_alerts(message)
            parsed, order = parse_trade_alert(formatted.content)

            if parsed and order and order.get("action") == "BTO":
                order["Trader"] = (
                    f"{formatted.author.name}#{formatted.author.discriminator}"
                )
                order["Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

                self.trader.new_trade_alert(order, parsed, formatted.content)
                break

        # Verify command structure
        send_order_cmds = [
            cmd for cmd in self.mock_broker.commands if cmd["action"] == "send_order"
        ]

        if send_order_cmds:
            cmd = send_order_cmds[0]
            order_dict = cmd.get("order_dict", {})
            print("\nValidating IBKR command structure:")
            print(f"  ✓ Has 'action': {order_dict.get('action')}")
            print(f"  ✓ Has 'orderType': {order_dict.get('orderType')}")
            print(f"  ✓ Has 'quant': {order_dict.get('quant')}")
            print(f"  ✓ Has 'asset': {order_dict.get('asset')}")
            print(f"  ✓ Has 'conId': {order_dict.get('conId')}")

            # Verify required fields for IBKR
            self.assertIn("order_dict", cmd)
            self.assertIn("action", order_dict)
            self.assertIn("orderType", order_dict)
            self.assertIn("quant", order_dict)
            self.assertIn("order_id", cmd)

            # Verify action is valid
            self.assertIn(order_dict["action"], ["BUY", "SELL"])

            # Verify quantity is positive
            self.assertGreater(order_dict["quant"], 0)

            print("\n✓ Test passed: IBKR command structure is valid")
        else:
            self.skipTest("No send_order commands generated")


def main():
    """Run tests with verbose output"""
    global TEST_DATE

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Test Bear Discord alerts to IBKR commands flow for a specific date",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Use default date (2025-11-11)
  %(prog)s 2025-11-12         # Test alerts from Nov 12, 2025
  %(prog)s 2025-11-13         # Test alerts from Nov 13, 2025
  
Note: Message files must exist as tests/data/bear_messages_YYYY-MM-DD.json
        """,
    )
    parser.add_argument(
        "date",
        nargs="?",
        default="2025-11-11",
        help="Date to test in YYYY-MM-DD format (default: 2025-11-11)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase output verbosity"
    )

    # Parse args, but keep remaining for unittest
    args, remaining = parser.parse_known_args()

    # Validate date format
    try:
        datetime.strptime(args.date, "%Y-%m-%d")
        TEST_DATE = args.date
    except ValueError:
        print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD format.")
        sys.exit(1)

    # Restore sys.argv for unittest
    sys.argv = [sys.argv[0]] + remaining

    # Run with verbose output
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFullFlowBearToIBKR)
    verbosity = 2 if args.verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
