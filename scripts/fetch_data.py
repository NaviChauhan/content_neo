"""
fetch_data.py — pulls Instagram data for your account and competitors via Apify.
Run: python scripts/fetch_data.py
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")
MY_HANDLE = os.getenv("MY_HANDLE", "neorakii")
COMPETITOR_HANDLES = os.getenv("COMPETITOR_HANDLES", "").split(",")

ALL_HANDLES = [MY_HANDLE] + [h.strip() for h in COMPETITOR_HANDLES if h.strip()]

DATA_PATH = Path(__file__).parent.parent / "dashboard" / "data" / "data.json"
ACTOR_ID = "apify~instagram-profile-scraper"


def run_apify_actor(usernames: list[str]) -> list[dict]:
    """Start an Apify actor run and wait for results."""
    print(f"  Starting Apify scrape for: {usernames}")

    # Start the run
    run_url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={APIFY_TOKEN}"
    payload = {
        "usernames": usernames,
        "resultsLimit": 50,       # posts per account
    }
    resp = requests.post(run_url, json=payload, timeout=30)
    resp.raise_for_status()
    run_id = resp.json()["data"]["id"]
    print(f"  Run started: {run_id}")

    # Poll until finished
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"
    for attempt in range(30):
        time.sleep(10)
        status_resp = requests.get(status_url, timeout=15)
        status = status_resp.json()["data"]["status"]
        print(f"  [{attempt+1}] Status: {status}")
        if status == "SUCCEEDED":
            break
        if status in ("FAILED", "ABORTED", "TIMED-OUT"):
            raise RuntimeError(f"Apify run {run_id} ended with status: {status}")
    else:
        raise RuntimeError("Apify run timed out after 5 minutes")

    # Fetch results from default dataset
    dataset_id = status_resp.json()["data"]["defaultDatasetId"]
    items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}&limit=200"
    items_resp = requests.get(items_url, timeout=30)
    items_resp.raise_for_status()
    return items_resp.json()


def extract_profile(raw: dict) -> dict:
    return {
        "username": raw.get("username", ""),
        "full_name": raw.get("fullName", ""),
        "followers": raw.get("followersCount", 0),
        "following": raw.get("followsCount", 0),
        "posts_count": raw.get("postsCount", 0),
        "bio": raw.get("biography", ""),
        "is_verified": raw.get("verified", False),
    }


def extract_posts(raw: dict) -> list[dict]:
    posts = []
    for post in raw.get("latestPosts", []):
        posts.append({
            "username": raw.get("username", ""),
            "shortcode": post.get("shortCode", ""),
            "type": post.get("type", ""),
            "caption": (post.get("caption") or "")[:500],
            "likes": post.get("likesCount", 0),
            "comments": post.get("commentsCount", 0),
            "views": post.get("videoViewCount", 0),
            "timestamp": post.get("timestamp", ""),
            "url": post.get("url", ""),
        })
    return posts


def main():
    print("=== Fetching Instagram data ===")
    print(f"Your account : @{MY_HANDLE}")
    print(f"Competitors  : {', '.join(['@' + h for h in COMPETITOR_HANDLES])}")
    print()

    raw_items = run_apify_actor(ALL_HANDLES)
    print(f"\n  Got {len(raw_items)} profile(s) back from Apify")

    my_profile = {}
    my_posts = []
    competitor_profiles = []
    competitor_posts = []

    for item in raw_items:
        username = item.get("username", "").lower()
        profile = extract_profile(item)
        posts = extract_posts(item)

        if username == MY_HANDLE.lower():
            my_profile = profile
            my_posts = posts
        else:
            competitor_profiles.append(profile)
            competitor_posts.extend(posts)

    data = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "my_profile": my_profile,
        "my_posts": my_posts,
        "competitor_profiles": competitor_profiles,
        "competitor_posts": competitor_posts,
    }

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"\n✅ Data saved to {DATA_PATH}")
    print(f"   Your posts      : {len(my_posts)}")
    print(f"   Competitor posts: {len(competitor_posts)}")


if __name__ == "__main__":
    main()
