# Discord Community Intelligence Bot

This project is a **Discord bot** that parses community activity to:

- ✅ Detect new members from a `#welcome` channel
- ✅ Collect user introduction messages from `#introductions`
- ✅ Extract social media links (Twitter, GitHub, YouTube, Instagram, LinkedIn)
- ✅ Fetch public follower stats
- ✅ Save all data to a local SQLite database (via SQLAlchemy)
- ✅ Export user profiles by join date range with detailed analytics

---

## 🧱 Project Structure

```
discord_bot/
├── config.py              # API keys & config
├── models.py              # SQLAlchemy models
├── scraper.py             # Social stat scrapers
├── utils.py               # Regex for socials
├── main.py                # Bot for data ingestion
├── export_users.py        # CLI to export structured data
├── requirements.txt
└── README.md              # You're here!
```

---

## ⚙️ Setup

### 1. Clone the Repo

```bash
git https://github.com/Sxela/discord-community-intel
cd discord-community-intel
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Configuration

Edit `config.py`:

```python
DISCORD_BOT_TOKEN = "your-discord-bot-token"
YOUTUBE_API_KEY = "your-youtube-data-api-key"
DB_URL = "sqlite:///community.db"
```

- Get a YouTube API key: https://console.cloud.google.com/apis/library/youtube.googleapis.com

---

## 🔐 Discord Token & Bot Permissions

To run this bot, you'll need to create a Discord bot and give it proper permissions.

### 1. Create a Bot on Discord Developer Portal

- Go to: https://discord.com/developers/applications
- Click **"New Application"** → give it a name
- Go to **Bot** → click **"Add Bot"**
- Copy the **bot token** and paste it into `config.py`:

```python
DISCORD_BOT_TOKEN = "your-discord-token"
```

---

### 2. Enable Required Privileged Intents

In the **Bot** settings, under **Privileged Gateway Intents**, enable:

- ✅ `MESSAGE CONTENT INTENT`
- ✅ `SERVER MEMBERS INTENT`

---

### 3. Invite the Bot to Your Server

Go to the **OAuth2 > URL Generator**, select:

- **Scopes**:
  - `bot`
- **Bot Permissions**:
  - `Read Message History`
  - `View Channels`
  - `Read Messages/View Channels`
  - `Send Messages`
  - `Manage Messages` (optional)
  - `Use Slash Commands` (optional if extended)

Generate the URL, open it in your browser, and invite the bot to your server.

You're now ready to run the bot!

---

## 🚀 Usage

### 1. Parse Discord Messages

```bash
python main.py --start 2025-07-01 --end 2025-07-15 --autoclose
```

This will:
- Fetch `#welcome`, `#introductions`, and `#social-share` messages within range
- Store users, messages, socials, and follower stats
- Avoid reprocessing already-parsed messages

---

### 2. Export Users to CSV

```bash
python export_users.py --start 2025-07-01 --end 2025-07-15 --out influencer_report.csv
```

Exports:

- Basic user info (ID, name, join date)
- Their intro message
- All their social links
- Follower counts **per platform**
- A calculated `influence_score` using log-scale + weighting

---

## 🧠 Influence Score

The score is a weighted sum of followers using this formula:

```
influence_score = Σ log(followers + 1) * platform_weight
```

Platform weights:

| Platform   | Weight |
|------------|--------|
| GitHub     | 0.3    |
| Twitter    | 0.6    |
| YouTube    | 0.9    |
| Instagram  | 1.0    |
| LinkedIn   | 0.4    |

This avoids inflated totals when people have the same audience across networks.

---

## 📊 Output Sample (CSV)

| username | github_followers | twitter_followers | ... | all_social_links | influence_score |
|----------|------------------|--------------------|-----|------------------|-----------------|

---

## 📌 Notes

- Scraping is subject to platform rate limits.
- Instagram scraping uses public HTML, and may break if Instagram changes their structure.
- No LinkedIn scraping — only logs shared URLs.

---

## 🔮 Roadmap

- [ ] LLM-based NER extraction from intro messages
- [ ] Dashboard with Streamlit or Flask
- [ ] Scheduled runs via cron or Docker
- [ ] Export to Airtable / Google Sheets

---

## 🧑‍💻 Contributing

PRs welcome! This is an internal tool built for real-world Discord community management — suggestions and improvements are encouraged.

---

## 📄 License

Apache-2.0 © 2025
