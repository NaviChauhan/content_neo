"""
telegram_bot.py — sends a daily content report to your Telegram.
Run: python scripts/telegram_bot.py
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATA_PATH = Path(__file__).parent.parent / "dashboard" / "data" / "data.json"


def send_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }, timeout=15)
    resp.raise_for_status()
    return resp.json()


def build_report(data: dict) -> str:
    my = data.get("my_profile", {})
    my_posts = data.get("my_posts", [])
    comp_profiles = data.get("competitor_profiles", [])
    comp_posts = data.get("competitor_posts", [])
    last_updated = data.get("last_updated", "unknown")[:10]

    # Stats
    avg_likes = round(sum(p.get("likes", 0) for p in my_posts) / len(my_posts), 1) if my_posts else 0
    avg_views = round(sum(p.get("views", 0) for p in my_posts) / len(my_posts), 1) if my_posts else 0
    best_post = max(my_posts, key=lambda p: p.get("likes", 0), default={})

    # Top competitor idea
    top_comp_post = max(comp_posts, key=lambda p: p.get("likes", 0) + p.get("comments", 0) * 3, default={})

    # Best content type
    type_stats = {}
    for p in my_posts:
        t = p.get("type", "Unknown")
        type_stats[t] = type_stats.get(t, 0) + p.get("likes", 0)
    best_type = max(type_stats, key=type_stats.get, default="Video") if type_stats else "Video"

    top_competitor = max(comp_profiles, key=lambda c: c.get("followers", 0), default={})

    lines = [
        f"📊 *Daily Content Report — @{my.get('username', 'neorakii')}*",
        f"_Date: {last_updated}_",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "🔢 *YOUR STATS*",
        f"• Followers: *{my.get('followers', 0):,}*",
        f"• Posts tracked: *{len(my_posts)}*",
        f"• Avg likes/post: *{avg_likes}*",
        f"• Avg views/video: *{avg_views}*",
        f"• Best format: *{best_type}*",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "🏆 *TOP COMPETITOR*",
        f"• @{top_competitor.get('username', '?')} — {top_competitor.get('followers', 0):,} followers",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "💡 *IDEA TO STEAL TODAY*",
    ]

    if top_comp_post:
        caption = top_comp_post.get("caption", "")[:200]
        lines += [
            f"From @{top_comp_post.get('username', '?')}:",
            f"_{caption}_",
            f"❤️ {top_comp_post.get('likes', 0)}  💬 {top_comp_post.get('comments', 0)}",
        ]

    lines += [
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "✍️ *HOOK FORMULA FOR TODAY*",
        f"Lead with a *{best_type}* — it's your highest-engagement format.",
        "Try: [Bold claim] → [3-point proof] → [CTA]",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "🗓 *TODAY'S CONTENT TASK*",
    ]

    day_of_week = datetime.now().weekday()
    plan = [
        ("Carousel", "Brand positioning tip"),
        ("Reel", "Behind-the-scenes / process"),
        ("Carousel", "Competitor gap insight"),
        ("Story Poll", "Client result / testimonial"),
        ("Reel", "Trending meme in your niche"),
        ("Quote Card", "Motivational / value post"),
        ("Rest", "Engage with comments & DMs"),
    ]
    fmt, topic = plan[day_of_week]
    lines += [
        f"Format: *{fmt}*",
        f"Topic: {topic}",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "💬 *DM MOVE OF THE DAY*",
        "Reply to every comment with a question to boost reach.",
        "",
        "🤖 _Sent by ContentAgent OS_",
    ]

    return "\n".join(lines)


def main():
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in .env")
        return

    if not DATA_PATH.exists():
        print("❌ No data.json found. Run fetch_data.py first.")
        return

    data = json.loads(DATA_PATH.read_text())
    report = build_report(data)

    print("Sending report to Telegram...")
    send_message(report)
    print("✅ Report sent!")


if __name__ == "__main__":
    main()
