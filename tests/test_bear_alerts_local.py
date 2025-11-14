#!/usr/bin/env python3
"""
Test script to parse Bear's channel messages from a saved JSON file (offline testing)
Usage: python test_bear_alerts_local.py [YYYY-MM-DD]
If no date provided, uses 2025-11-12
"""

import json
import os
import sys
from datetime import datetime

from DiscordAlertsTrader.message_parser import parse_trade_alert
from DiscordAlertsTrader.server_alert_formatting import BEAR_STATE_FILE, bear_alerts


class MockEmbedAuthor:
    """Mock embed author object matching discord.py structure"""

    def __init__(self, data):
        if data is None:
            # EmbedCopy expects these attributes to exist
            self.name = None
            self.discriminator = "0"
            self.id = 0
            self.bot = False
        else:
            self.name = data.get("name")
            self.discriminator = (
                "0"  # Embed authors don't have discriminators typically
            )
            self.id = 0  # Embed authors don't have IDs typically
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
        # Always create an author object, even if None, so EmbedCopy can access attributes
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
        self.name = "Bear's Trading Server"  # Add name attribute that may be accessed


class MockMessage:
    def __init__(self, data):
        self.id = data.get("id")
        self.author = MockAuthor(data.get("author", {}))
        self.content = data.get("content", "")
        self.created_at = datetime.fromisoformat(data.get("created_at"))
        self.channel = MockChannel(data.get("channel_id"))
        self.guild = MockGuild()
        self.embeds = [MockEmbed(e) for e in data.get("embeds", [])]


def load_messages(filename):
    """Load messages from JSON file"""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    # Toggle: when True only parsed trading actions are printed (concise mode)
    SHOW_ACTIONS_ONLY = True

    # Get date from command line or use default
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
        try:
            # Validate date format
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print(f"ERROR: Invalid date format '{date_str}'. Use YYYY-MM-DD")
            return
    else:
        date_str = "2025-11-12"  # default

    # Clean up any existing state files for fresh test
    if os.path.exists(BEAR_STATE_FILE):
        os.remove(BEAR_STATE_FILE)
        print("Cleared previous position state for fresh test")
    print()

    # Load saved messages
    data_file = f"tests/data/bear_messages_{date_str}.json"
    print(f"Loading messages from {data_file}...")

    try:
        data = load_messages(data_file)
    except FileNotFoundError:
        print(f"ERROR: File not found: {data_file}")
        print("Please run test_bear_alerts_fetch.py first to fetch messages")
        return

    messages = [MockMessage(msg) for msg in data["messages"]]

    print(
        f"Loaded {len(messages)} messages from {data['date_range']['start']} to {data['date_range']['end']}"
    )

    # Filter to only show messages relevant to trades or trade updates.
    # Previous filter missed "Updates:" style profit/trim context messages (e.g. message 5: "Back at trim level").
    # We expand criteria:
    #  1. Standard trade keywords (entries/contracts/daytrade etc.)
    #  2. Update titles like "Updates:" or "UPDATE:".
    #  3. Profit/percentage patterns ("Up __105__%" or "for 52%") using simple substrings.
    #  4. Trim context phrases ("trim level", "last trim").
    base_keywords = [
        "Entry:",
        "Contract:",
        "Daytrade",
        "LOTTO",
        "Swing",
        "trimming",
        "closing",
        "Updates:",
        "UPDATE:",
        "trim level",
        "last trim",
        "runners",  # Keep runner updates
        "adding",  # Position size increases
        "de risk",  # De-risking operations
        "close the rest",  # Closing remaining positions
        "stopped out",  # Stopped out positions
    ]
    percent_indicators = ["Up ", "%", " for "]  # coarse matches for profit update text

    def is_trade_related(msg):
        if not msg.embeds:
            return False
        title = msg.embeds[0].title or ""
        desc = msg.embeds[0].description or ""
        text = f"{title}\n{desc}".lower()
        # Check base keywords (case-insensitive)
        if any(k.lower() in text for k in base_keywords):
            return True
        # Check profit indicators with percentage symbol or "Up " prefix
        if any(indicator.lower() in text for indicator in percent_indicators):
            # Require a digit before '%' to reduce false positives
            if "%" in text and any(ch.isdigit() for ch in text.split("%")[0][-4:]):
                return True
        return False

    trade_messages = [m for m in messages if is_trade_related(m)]

    print(
        f"Found {len(trade_messages)} trade-related messages out of {len(messages)} total\n"
    )

    successful_parses = 0
    failed_parses = 0

    for i, message in enumerate(trade_messages, 1):
        try:
            formatted_message = bear_alerts(message)
            parsed, order = parse_trade_alert(formatted_message.content)
            if parsed:
                successful_parses += 1
                if SHOW_ACTIONS_ONLY:
                    # Single-line concise output
                    action = order.get("action")
                    sym = order.get("Symbol")
                    price = order.get("price")
                    xqty = (
                        order.get("xQty")
                        if action in ["STC", "BTC"]
                        else order.get("Qty")
                    )
                    print(
                        f"{i:02d}/{len(trade_messages)} {action} {sym} price={price} xQty={xqty} :: {formatted_message.content}"
                    )
                else:
                    # Fallback verbose mode (original style simplified)
                    print("=" * 80)
                    print(f"Message {i}/{len(trade_messages)}")
                    print(f"Content: {formatted_message.content}")
            else:
                failed_parses += 1
                if not SHOW_ACTIONS_ONLY:
                    print(
                        f"{i:02d}/{len(trade_messages)} PARSE_FAILED :: {formatted_message.content[:120]}"
                    )
        except Exception as e:
            failed_parses += 1
            if not SHOW_ACTIONS_ONLY:
                print(f"{i:02d}/{len(trade_messages)} ERROR :: {e}")

    print("\nSummary:")
    print(f"Total messages: {len(messages)}")
    print(f"Trade alerts (filtered): {len(trade_messages)}")
    print(f"Parsed actions: {successful_parses}")
    print(f"Parse failures: {failed_parses}")
    if trade_messages:
        print(f"Success rate: {successful_parses / len(trade_messages) * 100:.1f}%")

    # Clean up state files after test
    if os.path.exists(BEAR_STATE_FILE):
        os.remove(BEAR_STATE_FILE)
        print("\nCleaned up position state file")


if __name__ == "__main__":
    main()
