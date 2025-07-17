# populate_message_log.py
import discord
import argparse
import asyncio
from datetime import datetime
from models import session, ParsedLog
from config import (
    DISCORD_BOT_TOKEN,
    WELCOME_CHANNEL_NAME,
    INTRO_CHANNEL_NAME,
    SOCIAL_SHARE_CHANNEL_NAME,
)
from sqlalchemy import create_engine, Table, Column, String, MetaData
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from config import DB_URL

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=str, required=True)
parser.add_argument("--end", type=str, required=True)
parser.add_argument("--autoclose", action="store_true")
args = parser.parse_args()

start = datetime.strptime(args.start, "%Y-%m-%d")
end = datetime.strptime(args.end, "%Y-%m-%d")

# Setup raw insert into message_log table
engine = create_engine(DB_URL)
metadata = MetaData()
message_log = Table(
    "message_log", metadata,
    Column("user_id", String),
    Column("channel", String),
    Column("content", String),
)
metadata.create_all(engine)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    guild = discord.utils.get(client.guilds)

    channels_to_parse = {
        WELCOME_CHANNEL_NAME: discord.utils.get(guild.text_channels, name=WELCOME_CHANNEL_NAME),
        INTRO_CHANNEL_NAME: discord.utils.get(guild.text_channels, name=INTRO_CHANNEL_NAME),
        SOCIAL_SHARE_CHANNEL_NAME: discord.utils.get(guild.text_channels, name=SOCIAL_SHARE_CHANNEL_NAME)
    }

    with engine.begin() as conn:
        for name, channel in channels_to_parse.items():
            if not channel:
                print(f"❌ Channel not found: {name}")
                continue

            print(f"📥 Fetching messages from #{name}")
            async for msg in channel.history(limit=1000, after=start, before=end):
                insert_stmt = sqlite_insert(message_log).values(
                    user_id=str(msg.author.id),
                    channel=name,
                    content=msg.content
                )
                conn.execute(insert_stmt)

    print("✅ Finished storing messages to message_log.")
    if args.autoclose:
        await client.close()

client.run(DISCORD_BOT_TOKEN)
