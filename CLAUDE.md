# Content Agent Dashboard

## Project Overview
A 5-agent content intelligence system for Instagram, with a live dashboard and Telegram reporting.

## Your Accounts
- **Your handle:** @neorakii
- **Competitors:** @yo_creativ, @saymoshimoshi, @weforvolume, @newvisiondigitalin

## Agents
1. **Ideator** — scouts trending ideas from your niche
2. **Hook & Script** — writes hooks and short-form scripts
3. **Planner** — builds a daily/weekly content calendar
4. **Analyst** — analyses post performance and competitor stats
5. **DM Manager** — drafts and manages DM responses

## Stack
- **Data:** Apify instagram-scraper
- **Dashboard:** Python (Flask) + HTML/JS
- **Telegram:** python-telegram-bot
- **Scheduler:** APScheduler

## File Structure
```
content-agent/
├── CLAUDE.md
├── .env                  # secrets — never commit
├── .gitignore
├── scripts/
│   ├── fetch_data.py     # Apify scraper runner
│   ├── agents.py         # 5 agent logic
│   └── telegram_bot.py   # Telegram reporter
└── dashboard/
    ├── app.py            # Flask server
    ├── templates/
    │   └── index.html    # Dashboard UI
    └── data/
        └── data.json     # Live data store
```

## Rules
- All tokens and secrets live in `.env` only
- Never hardcode credentials
- Improve existing files rather than replacing them
