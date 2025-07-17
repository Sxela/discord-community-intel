import argparse
from datetime import datetime
import json
import re
from sqlalchemy import and_
from models import session, WelcomeUser, MessageLog
from config import GEMINI_API_KEY
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

EXPECTED_FIELDS = [
    "name", "surname", "age", "geo", "occupation", "company", "where_learned_about_mago",
    "youtube", "instagram", "linkedin", "twitter", "bluesky", "soundcloud"
]

PROMPT_TEMPLATE = """
You are given multiple messages in different channels of a single user from a Discord community. Extract structured information.

Messages:
{messages}

Return a single JSON with the following keys (even if some are unknown or empty):
name, surname, age, geo, occupation, company, where_learned_about_mago,
youtube, instagram, linkedin, twitter, bluesky, soundcloud
"""

def parse_markdown_json(text):
    """Extract JSON from markdown code blocks or plain text"""
    # First try to find JSON in code blocks
    json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    
    # If no code blocks, try to find JSON object directly
    json_pattern = r'(\{.*\})'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    
    return text

def build_prompt(messages):
    formatted = "\n".join(
        f"[{msg.channel}] ({msg.timestamp.strftime('%Y-%m-%d')}): {msg.content.strip()}"
        for msg in messages if msg.content.strip()
    )
    return PROMPT_TEMPLATE.format(messages=formatted)

def build_profile(user, messages):
    prompt = build_prompt(messages)
    try:
        print('prompt', prompt)
        response = model.generate_content(prompt)
        print('response', response.text)
        
        # Parse the markdown JSON response
        json_text = parse_markdown_json(response.text)
        data = json.loads(json_text)
        
        for key in EXPECTED_FIELDS:
            data.setdefault(key, "")
        return data
    except Exception as e:
        print(f"❌ Gemini failed for {user}: {e}")
        return {}

def main(start, end, output_file):
    # Get unique user_ids from MessageLog within the date range
    users = session.query(MessageLog.user_id, MessageLog.username).filter(
        and_(MessageLog.timestamp >= start, MessageLog.timestamp <= end)
    ).distinct().all()

    results = []
    print(f"🧠 Building profiles for {len(users)} users")
    for user in users:
        messages = session.query(MessageLog).filter_by(user_id=user.user_id).order_by(MessageLog.timestamp).all()
        if not messages:
            continue
        else:
            print(f"🧠 Building profile for {user.username} ({len(messages)} messages)")
        profile = build_profile(user, messages)
        profile.update({
            "user_id": user.user_id,
            "username": user.username,
        #     "joined_at": user.joined_at.isoformat(),
        })
        results.append(profile)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"✅ Saved {len(results)} profiles to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=str, required=True)
    parser.add_argument("--end", type=str, required=True)
    parser.add_argument("--out", type=str, default="user_profiles.json")
    args = parser.parse_args()

    start_date = datetime.strptime(args.start, "%Y-%m-%d")
    end_date = datetime.strptime(args.end, "%Y-%m-%d")

    main(start_date, end_date, args.out)
