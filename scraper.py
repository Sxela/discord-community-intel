# scraper.py
import requests
import snscrape.modules.twitter as sntwitter
from bs4 import BeautifulSoup
from config import YOUTUBE_API_KEY
import re

def fetch_github_followers(url):
    try:
        username = url.rstrip('/').split('/')[-1]
        response = requests.get(f"https://api.github.com/users/{username}")
        return response.json().get("followers", 0) if response.ok else 0
    except:
        return 0

def fetch_twitter_followers(url):
    try:
        username = url.rstrip('/').split('/')[-1]
        for user in sntwitter.TwitterUserScraper(username).get_items():
            return user.followersCount
    except:
        return 0

def fetch_youtube_subs(url):
    try:
        if "channel" in url:
            channel_id = url.split('/')[-1]
        elif "@" in url:
            handle = url.rstrip('/').split('@')[-1]
            search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={handle}&key={YOUTUBE_API_KEY}"
            result = requests.get(search_url).json()
            channel_id = result["items"][0]["snippet"]["channelId"]
        else:
            return 0
        stats_url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={YOUTUBE_API_KEY}"
        stats = requests.get(stats_url).json()
        return int(stats['items'][0]['statistics']['subscriberCount'])
    except:
        return 0

def fetch_instagram_followers(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        page = requests.get(url, headers=headers)
        match = re.search(r'"edge_followed_by":\s*\{"count":\s*(\d+)\}', page.text)
        return int(match.group(1)) if match else 0
    except:
        return 0

def fetch_followers(platform, url):
    if platform == "github":
        return fetch_github_followers(url)
    elif platform == "twitter":
        return fetch_twitter_followers(url)
    elif platform == "youtube":
        return fetch_youtube_subs(url)
    elif platform == "instagram":
        return fetch_instagram_followers(url)
    return 0
