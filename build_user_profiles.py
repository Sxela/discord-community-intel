# build_user_profiles.py
import argparse
from datetime import datetime
from models import session, WelcomeUser
from config import DB_URL
from sqlalchemy import create_engine, text
import json
import google.generativeai as genai

from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-pro-latest")

# Fields to extract via LLM
EXPECTED_FIELDS = [
    "name", "surname", "age", "geo", "occupation", "company", "where_learned_about_mago",
    "youtube", "instagram", "linkedin", "twitter", "bluesky", "soundcloud"
]

# Prompt for Gemini
PROMPT_TEMPLATE = """
You are given user profile messages from a Discord community. Your job is to extract structured info.

Messages:
{messages}

Return a JSON with the following keys (even if some are empty):
name, surname, age, geo, occupation, company, where_learned_about_mago,
youtube, instagram, linkedin, twitter, bluesky, soundcloud
"""

def get_user_messages(user_id):
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 'welcome' AS source, m.content FROM message_log m
            WHERE m.user_id = :user_id AND m.channel = 'welcome'
            UNION ALL
            SELECT 'introductions', m.content FROM message_log m
            WHERE m.user_id = :user_id AND m.channel = 'introductions'
            UNION ALL
            SELECT 'social-share', m.content FROM message_log m
            WHERE m.user_id = :user_id AND m.channel = 'social-share'
        """), {"user_id": user_id})
        messages = [f"[{row.source}] {row.content}" for row in result]
    return "\n".join(messages)

def build_profile(user_id, combined_message):
    prompt = PROMPT_TEMPLATE.format(messages=combined_message)
    try:
        response = model.generate_content(prompt)
        parsed = json.loads(response.text)
        for key in EXPECTED_FIELDS:
            parsed.setdefault(key, "")
        return parsed
    except Exception as e:
        print(f"❌ Failed for user {user_id}: {e}")
        return {}

def main(start, end, output_file):
    users = session.query(WelcomeUser).filter(
        WelcomeUser.joined_at >= start,
        WelcomeUser.joined_at <= end
    ).all()

    all_profiles = []

    for user in users:
        print(f"🧠 Building profile for {user.username}")
        combined_msg = get_user_messages(user.user_id)
        profile_data = build_profile(user.user_id, combined_msg)
        profile_data.update({
            "user_id": user.user_id,
            "username": user.username,
            "joined_at": user.joined_at.isoformat(),
        })
        all_profiles.append(profile_data)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_profiles, f, indent=2)

    print(f"✅ Saved {len(all_profiles)} profiles to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=str, required=True)
    parser.add_argument("--end", type=str, required=True)
    parser.add_argument("--out", type=str, default="user_profiles.json")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")

    main(start, end, args.out)
