# export_users.py
import argparse
from datetime import datetime
import csv
import math
from collections import defaultdict
from models import session, WelcomeUser, Introduction, SocialProfile

PLATFORM_WEIGHTS = {
    "github": 0.3,
    "twitter": 0.6,
    "youtube": 0.9,
    "instagram": 1.0,
    "linkedin": 0.4,
}

ALL_PLATFORMS = list(PLATFORM_WEIGHTS.keys())

def log_score(f, weight): return math.log(f + 1) * weight

def compute_influence(socials):
    return sum(log_score(s.followers, PLATFORM_WEIGHTS.get(s.platform, 0.5)) for s in socials)

def export_users(start_date, end_date, out_file="export.csv"):
    users = session.query(WelcomeUser).filter(
        WelcomeUser.joined_at >= start_date,
        WelcomeUser.joined_at <= end_date
    ).all()

    output = []

    for user in users:
        uid = user.user_id
        intro = session.query(Introduction).filter_by(user_id=uid).first()
        socials = session.query(SocialProfile).filter_by(user_id=uid).all()

        social_counts = defaultdict(int)
        social_links = defaultdict(list)

        for s in socials:
            social_counts[s.platform] += s.followers
            social_links[s.platform].append(s.url)

        all_links = []
        for platform in ALL_PLATFORMS:
            all_links.extend(social_links[platform])

        influence = compute_influence(socials)

        row = {
            "user_id": uid,
            "username": user.username,
            "joined_at": user.joined_at.isoformat(),
            "intro_message": intro.intro_message if intro else "",
            "influence_score": round(influence, 2),
            "all_social_links": "; ".join(all_links),
        }

        for platform in ALL_PLATFORMS:
            row[f"{platform}_followers"] = social_counts[platform]

        output.append(row)

    output.sort(key=lambda x: x["influence_score"], reverse=True)

    with open(out_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "user_id", "username", "joined_at", "intro_message"
        ] + [f"{p}_followers" for p in ALL_PLATFORMS] + [
            "all_social_links", "influence_score"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)

    print(f"✅ Exported {len(output)} users to {out_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=str, required=True)
    parser.add_argument("--end", type=str, required=True)
    parser.add_argument("--out", type=str, default="export.csv")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")

    export_users(start, end, args.out)
