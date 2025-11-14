#!/usr/bin/env python3
"""
Test script to re-parse messages from Bear's channel for a full day (yesterday)
"""

from datetime import datetime, timedelta, timezone

import discord  # this is discord.py-self package

from DiscordAlertsTrader.configurator import cfg
from DiscordAlertsTrader.message_parser import parse_trade_alert
from DiscordAlertsTrader.server_alert_formatting import bear_alerts

# Bear's channel ID from your config
BEAR_CHANNEL_ID = 979906463487103006


class TestBot(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")

        # Calculate yesterday's date range
        now = datetime.now(timezone.utc)
        yesterday_start = (now - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        yesterday_end = (now - timedelta(days=1)).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        print(f"\nFetching messages from Bear channel for yesterday:")
        print(f"  From: {yesterday_start.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"  To:   {yesterday_end.strftime('%Y-%m-%d %H:%M:%S %Z')}\n")

        channel = self.get_channel(BEAR_CHANNEL_ID)
        if channel is None:
            print(f"ERROR: Could not find channel {BEAR_CHANNEL_ID}")
            await self.close()
            return

        messages = []
        async for message in channel.history(
            after=yesterday_start, before=yesterday_end, oldest_first=True, limit=None
        ):
            messages.append(message)

        # Filter to only show messages with trade keywords
        trade_messages = [
            m
            for m in messages
            if m.embeds
            and any(
                keyword in (m.embeds[0].description or "")
                or keyword in (m.embeds[0].title or "")
                for keyword in [
                    "Entry:",
                    "Contract:",
                    "Daytrade",
                    "LOTTO",
                    "Swing",
                    "trimming",
                    "closing",
                ]
            )
        ]

        print(
            f"Found {len(trade_messages)} trade-related messages out of {len(messages)} total messages\n"
        )

        for i, message in enumerate(trade_messages, 1):
            print("=" * 80)
            print(f"Message {i}/{len(trade_messages)}")
            print("=" * 80)
            print(f"Author: {message.author.name}#{message.author.discriminator}")
            print(f"Date: {message.created_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")

            # Test the bear_alerts formatting
            print("\n--- PARSING ---")
            try:
                formatted_message = bear_alerts(message)
                print(
                    f"Formatted Author: {formatted_message.author.name}#{formatted_message.author.discriminator}"
                )
                print(f"Formatted Content:\n  {formatted_message.content}")

                # Parse the alert to extract action
                parsed, order = parse_trade_alert(formatted_message.content)
                if parsed:
                    print(f"\n--- PARSED ACTION ---")
                    print(f"  Action: {order.get('action', 'N/A')}")
                    print(f"  Symbol: {order.get('Symbol', 'N/A')}")
                    print(f"  Asset: {order.get('asset', 'N/A')}")
                    if order.get("asset") == "option":
                        print(f"  Strike: {order.get('strike', 'N/A')}")
                        print(f"  Expiry: {order.get('expDate', 'N/A')}")
                    print(f"  Price: {order.get('price', 'N/A')}")
                    print(f"  Qty: {order.get('Qty', 'N/A')}")
                    if order.get("action") in ["BTO", "STO"]:
                        print(f"  PT1: {order.get('PT1', 'N/A')}")
                        print(f"  PT2: {order.get('PT2', 'N/A')}")
                        print(f"  PT3: {order.get('PT3', 'N/A')}")
                        print(f"  SL: {order.get('SL', 'N/A')}")
                    elif order.get("action") in ["STC", "BTC"]:
                        print(f"  Exit Qty: {order.get('xQty', 'N/A')}")
                else:
                    print(f"\n--- PARSE FAILED ---")
                    print(f"  Could not parse alert into trading action")

            except Exception as e:
                print(f"ERROR parsing: {e}")
                import traceback

                traceback.print_exc()

            print()

        print("=" * 80)
        print(f"\nSummary:")
        print(f"  Total messages: {len(messages)}")
        print(f"  Trade alerts: {len(trade_messages)}")
        print("Test complete!")
        await self.close()


def main():
    """Run the test bot"""
    token = cfg["discord"]["discord_token"]

    if not token or token == "test":
        print("ERROR: No valid Discord token found in config.ini")
        print("Please set your discord_token in the [discord] section")
        return

    client = TestBot()
    client.run(token)


if __name__ == "__main__":
    main()
