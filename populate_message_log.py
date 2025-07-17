# populate_message_log.py
import discord
import argparse
import asyncio
from datetime import datetime
from models import MessageLog
from config import (
    DISCORD_BOT_TOKEN,
    WELCOME_CHANNEL_NAME,
    INTRO_CHANNEL_NAME,
    SOCIAL_SHARE_CHANNEL_NAME,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
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

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    guild = discord.utils.get(client.guilds)

    channels_to_parse = {
        WELCOME_CHANNEL_NAME: discord.utils.get(guild.text_channels, name=WELCOME_CHANNEL_NAME),
        INTRO_CHANNEL_NAME: discord.utils.get(guild.text_channels, name=INTRO_CHANNEL_NAME),
        SOCIAL_SHARE_CHANNEL_NAME: discord.utils.get(guild.text_channels, name=SOCIAL_SHARE_CHANNEL_NAME)
    }

    for name, channel in channels_to_parse.items():
        if not channel:
            print(f"❌ Channel not found: {name}")
            continue

        print(f"📥 Fetching messages from #{name}")
        async for msg in channel.history(limit=1000, after=start, before=end):
            if session.query(MessageLog).filter_by(id=str(msg.id)).first():
                continue  # Skip duplicates

            entry = MessageLog(
                id=str(msg.id),
                user_id=str(msg.author.id),
                username=str(msg.author),
                channel=name,
                content=msg.content,
                timestamp=msg.created_at
            )
            session.add(entry)

    session.commit()
    print("✅ Message log table updated.")
    if args.autoclose:
        await client.close()

client.run(DISCORD_BOT_TOKEN)
