# main.py
import discord
import argparse
import asyncio
from datetime import datetime, timedelta
from models import session, WelcomeUser, Introduction, SocialProfile, ParsedLog
from utils import extract_socials
from scraper import fetch_followers
from config import (
    DISCORD_BOT_TOKEN,
    WELCOME_CHANNEL_NAME,
    INTRO_CHANNEL_NAME,
    SOCIAL_SHARE_CHANNEL_NAME,
)

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
extended_start = start - timedelta(days=2)
extended_end = end + timedelta(days=2)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    guild = discord.utils.get(client.guilds)

    # Use channel names from config
    welcome_channel = discord.utils.get(guild.text_channels, name=WELCOME_CHANNEL_NAME)
    intro_channel = discord.utils.get(guild.text_channels, name=INTRO_CHANNEL_NAME)
    social_share_channel = discord.utils.get(guild.text_channels, name=SOCIAL_SHARE_CHANNEL_NAME)

    for channel, name in zip([welcome_channel, intro_channel, social_share_channel], [WELCOME_CHANNEL_NAME, INTRO_CHANNEL_NAME, SOCIAL_SHARE_CHANNEL_NAME]):
        print(f"📝 Parsing {name} channel with id {channel.id}")
        if not channel:
            print(f"❌ {name} channel could not be found. Please check the config values.")
            return

    if not all([welcome_channel, intro_channel, social_share_channel]):
        print("❌ One or more channels could not be found. Please check the config values.")
        return

    # Welcome
    last_welcome = session.query(ParsedLog).filter_by(channel=WELCOME_CHANNEL_NAME).first()
    welcome_after = max(start, last_welcome.last_parsed) if last_welcome else start
    async for msg in welcome_channel.history(limit=1000, after=welcome_after, before=end):
        uid = str(msg.author.id)
        if not session.query(WelcomeUser).filter_by(user_id=uid).first():
            session.add(WelcomeUser(user_id=uid, username=str(msg.author), joined_at=msg.created_at))
    session.merge(ParsedLog(channel=WELCOME_CHANNEL_NAME, last_parsed=end))
    session.commit()

    user_ids = [u.user_id for u in session.query(WelcomeUser).all()]

    async def log_socials(channel, is_intro=False):
        last = session.query(ParsedLog).filter_by(channel=channel.name).first()
        after = max(extended_start, last.last_parsed) if last else extended_start

        async for msg in channel.history(limit=1000, after=after, before=extended_end):
            uid = str(msg.author.id)
            if uid not in user_ids:
                continue
            if is_intro and not session.query(Introduction).filter_by(user_id=uid).first():
                session.add(Introduction(user_id=uid, intro_message=msg.content, intro_time=msg.created_at))

            for platform, url in extract_socials(msg.content):
                if session.query(SocialProfile).filter_by(user_id=uid, url=url).first():
                    continue
                followers = fetch_followers(platform, url)
                session.add(SocialProfile(user_id=uid, platform=platform, url=url, followers=followers))

        session.merge(ParsedLog(channel=channel.name, last_parsed=extended_end))
        session.commit()

    await log_socials(intro_channel, is_intro=True)
    await log_socials(social_share_channel, is_intro=False)

    print("📊 Done parsing.")
    if args.autoclose:
        await client.close()

client.run(DISCORD_BOT_TOKEN)
