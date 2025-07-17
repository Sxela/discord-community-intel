# utils.py
import re

SOCIAL_PATTERNS = {
    "twitter": r"(https?://(?:www\.)?twitter\.com/\w+)",
    "github": r"(https?://(?:www\.)?github\.com/\w+)",
    "linkedin": r"(https?://(?:www\.)?linkedin\.com/in/[\w\-]+)",
    "youtube": r"(https?://(?:www\.)?(?:youtube\.com/@[\w\-]+|youtube\.com/channel/[\w\-]+))",
    "instagram": r"(https?://(?:www\.)?instagram\.com/[\w\.\-]+)"
}

def extract_socials(text):
    found = []
    for platform, pattern in SOCIAL_PATTERNS.items():
        matches = re.findall(pattern, text)
        for url in matches:
            found.append((platform, url))
    return found
