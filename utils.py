# utils.py
import re

# Full URLs and x.com alias
SOCIAL_PATTERNS = {
    # "twitter": r"(https?://(?:www\.)?(?:twitter\.com|x\.com)/\w+)",
    "github": r"(https?://(?:www\.)?github\.com/\w+)",
    "linkedin": r"(https?://(?:www\.)?linkedin\.com/in/[\w\-]+)",
    "youtube": r"(https?://(?:www\.)?(?:youtube\.com/@[\w\-]+|youtube\.com/channel/[\w\-]+))",
    "instagram": r"(https?://(?:www\.)?instagram\.com/[\w\.\-]+)"
}

# Soft guessing from handles like @username or @platform/username
HANDLE_PATTERN = r"@(?:(\w+)/)?([\w\.-_]+)"  # matches @username or @platform/username

DEFAULT_HANDLE_GUESS_ORDER = ["instagram", "github"]

def extract_socials(text):
    found = []

    # Match full URLs
    for platform, pattern in SOCIAL_PATTERNS.items():
        matches = re.findall(pattern, text)
        for url in matches:
            found.append((platform, url))

    # Match handle-based mentions
    for match in re.finditer(HANDLE_PATTERN, text):
        platform_hint, username = match.groups()
        platform = platform_hint.lower() if platform_hint else None

        # If platform is hinted (e.g., @twitter/john), use it directly
        if platform in SOCIAL_PATTERNS:
            url = f"https://{platform}.com/{username}"
            found.append((platform, url))

        # Otherwise, guess
        elif platform is None:
            for guess in DEFAULT_HANDLE_GUESS_ORDER:
                url = f"https://{guess}.com/{username}"
                found.append((guess, url))

    return found
