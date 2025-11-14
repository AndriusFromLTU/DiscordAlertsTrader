#!/usr/bin/env python3
"""
Script to fetch messages from Bear's channel and save them to a JSON file for testing
Usage: python test_bear_alerts_fetch.py [YYYY-MM-DD]
If no date provided, fetches yesterday's messages
"""

import json
import sys
from datetime import datetime, timedelta, timezone

import discord  # this is discord.py-self package

from DiscordAlertsTrader.configurator import cfg

# Bear's channel ID from your config
BEAR_CHANNEL_ID = 979906463487103006


class FetchBot(discord.Client):
    def __init__(self, target_date=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_date = target_date

    async def on_ready(self):
        print(f"Logged in as {self.user}")

        # Calculate date range based on target_date or yesterday
        now = datetime.now(timezone.utc)
        if self.target_date:
            target_start = self.target_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            target_end = self.target_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            date_str = self.target_date.strftime("%Y-%m-%d")
        else:
            target_start = (now - timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            target_end = (now - timedelta(days=1)).replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            date_str = target_start.strftime("%Y-%m-%d")

        print(f"\nFetching messages from Bear channel for {date_str}:")
        print(f"  From: {target_start.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"  To:   {target_end.strftime('%Y-%m-%d %H:%M:%S %Z')}\n")

        channel = self.get_channel(BEAR_CHANNEL_ID)
        if channel is None:
            print(f"ERROR: Could not find channel {BEAR_CHANNEL_ID}")
            await self.close()
            return

        messages = []
        async for message in channel.history(
            after=target_start, before=target_end, oldest_first=True, limit=None
        ):
            # Convert message to JSON-serializable format
            msg_data = {
                "id": message.id,
                "author": {
                    "name": message.author.name,
                    "discriminator": message.author.discriminator,
                    "id": message.author.id,
                    "bot": message.author.bot,
                },
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "channel_id": message.channel.id,
                "embeds": [],
            }

            # Extract embed data
            for embed in message.embeds:
                embed_data = {
                    "title": embed.title,
                    "description": embed.description,
                    "author": None,
                    "fields": [],
                }

                if embed.author:
                    embed_data["author"] = {
                        "name": embed.author.name
                        if hasattr(embed.author, "name")
                        else None,
                        "url": embed.author.url
                        if hasattr(embed.author, "url")
                        else None,
                    }

                for field in embed.fields:
                    embed_data["fields"].append(
                        {"name": field.name, "value": field.value}
                    )

                msg_data["embeds"].append(embed_data)

            messages.append(msg_data)

        # Save to JSON file
        output_file = f"tests/data/bear_messages_{date_str}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "fetch_date": now.isoformat(),
                    "date_range": {
                        "start": target_start.isoformat(),
                        "end": target_end.isoformat(),
                    },
                    "channel_id": BEAR_CHANNEL_ID,
                    "message_count": len(messages),
                    "messages": messages,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        print(f"Saved {len(messages)} messages to {output_file}")
        print("Test complete!")
        await self.close()


def main():
    """Run the fetch bot"""
    token = cfg["discord"]["discord_token"]

    if not token or token == "test":
        print("ERROR: No valid Discord token found in config.ini")
        print("Please set your discord_token in the [discord] section")
        return

    # Parse command line argument for date
    target_date = None
    if len(sys.argv) > 1:
        try:
            target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            print(f"Fetching messages for: {sys.argv[1]}")
        except ValueError:
            print(f"ERROR: Invalid date format '{sys.argv[1]}'. Use YYYY-MM-DD")
            return

    client = FetchBot(target_date=target_date)
    client.run(token)


if __name__ == "__main__":
    main()
