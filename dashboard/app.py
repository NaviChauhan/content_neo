"""
app.py — Flask dashboard server for the Content Agent system.
Run: python dashboard/app.py
"""

import json
import os
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify

app = Flask(__name__)
DATA_PATH = Path(__file__).parent / "data" / "data.json"


def load_data() -> dict:
    if DATA_PATH.exists():
        return json.loads(DATA_PATH.read_text())
    return {}


def compute_agent_outputs(data: dict) -> dict:
    my_posts = data.get("my_posts", [])
    competitor_posts = data.get("competitor_posts", [])
    my_profile = data.get("my_profile", {})
    competitor_profiles = data.get("competitor_profiles", [])

    # --- Analyst ---
    total_likes = sum(p.get("likes", 0) for p in my_posts)
    total_views = sum(p.get("views", 0) for p in my_posts)
    avg_likes = round(total_likes / len(my_posts), 1) if my_posts else 0
    avg_views = round(total_views / len(my_posts), 1) if my_posts else 0
    best_post = max(my_posts, key=lambda p: p.get("likes", 0), default={})
    top_competitor = max(competitor_profiles, key=lambda c: c.get("followers", 0), default={})

    # --- Ideator: find competitor posts with highest engagement ---
    comp_sorted = sorted(competitor_posts, key=lambda p: p.get("likes", 0) + p.get("comments", 0) * 3, reverse=True)
    top_ideas = []
    for p in comp_sorted[:5]:
        caption = p.get("caption", "")
        top_ideas.append({
            "source": "@" + p.get("username", ""),
            "hook": caption[:120] + "…" if len(caption) > 120 else caption,
            "likes": p.get("likes", 0),
            "comments": p.get("comments", 0),
        })

    # --- Hook & Script: analyse your own best-performing content types ---
    type_stats = {}
    for p in my_posts:
        t = p.get("type", "Unknown")
        if t not in type_stats:
            type_stats[t] = {"count": 0, "likes": 0, "views": 0}
        type_stats[t]["count"] += 1
        type_stats[t]["likes"] += p.get("likes", 0)
        type_stats[t]["views"] += p.get("views", 0)

    best_type = max(type_stats, key=lambda t: type_stats[t]["likes"], default="Video")
    hook_suggestions = [
        f"Your {best_type}s get the most engagement — lead with one this week.",
        "Try opening with a bold claim, then prove it in 3 slides.",
        "Hook formula that works in your niche: [Controversial truth] + [Proof] + [CTA].",
    ]

    # --- Planner: simple 7-day plan ---
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    formats = ["Carousel", "Reel", "Carousel", "Story Poll", "Reel", "Quote Card", "Rest / Engage"]
    topics = [
        "Brand positioning tip",
        "Behind-the-scenes / process",
        "Competitor gap insight",
        "Client result / testimonial",
        "Trending meme in your niche",
        "Motivational / value post",
        "—",
    ]
    calendar = [{"day": d, "format": f, "topic": t} for d, f, t in zip(days, formats, topics)]

    # --- DM Manager ---
    dm_templates = [
        {"trigger": "New follower from competitor", "reply": "Hey! Noticed you're into [niche] — we help brands like yours grow with strategy + content. What's your biggest challenge right now?"},
        {"trigger": "Post comment: 'How much?'", "reply": "Hey! Pricing depends on your goals — DM us and we'll give you a custom breakdown. Takes 5 mins. 🙌"},
        {"trigger": "Story reply: 'Interested'", "reply": "Love that! Let's talk. We usually start with a quick discovery call — want me to send a link?"},
    ]

    return {
        "analyst": {
            "followers": my_profile.get("followers", 0),
            "posts_count": my_profile.get("posts_count", 0),
            "avg_likes": avg_likes,
            "avg_views": avg_views,
            "best_post": best_post,
            "top_competitor": top_competitor,
            "type_stats": type_stats,
        },
        "ideator": {
            "top_ideas": top_ideas,
        },
        "hook_script": {
            "best_type": best_type,
            "suggestions": hook_suggestions,
            "type_stats": type_stats,
        },
        "planner": {
            "calendar": calendar,
        },
        "dm_manager": {
            "templates": dm_templates,
        },
    }


@app.route("/")
def index():
    data = load_data()
    agents = compute_agent_outputs(data)
    last_updated = data.get("last_updated", "Never")
    my_profile = data.get("my_profile", {})
    return render_template("index.html",
                           agents=agents,
                           my_profile=my_profile,
                           last_updated=last_updated)


@app.route("/api/data")
def api_data():
    data = load_data()
    agents = compute_agent_outputs(data)
    return jsonify({"agents": agents, "profile": data.get("my_profile", {}), "last_updated": data.get("last_updated")})


@app.route("/refresh")
def refresh():
    import threading
    import sys
    import os
    sys.path.insert(0, str(Path(__file__).parent.parent))
    import scripts.fetch_data as fetcher
    def run():
        fetcher.main()
    threading.Thread(target=run).start()
    return "Fetching data in background... check back in 2 minutes.", 202


if __name__ == "__main__":
    app.run(debug=True, port=5050)
