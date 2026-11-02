import json
import os
from itertools import islice

import instaloader
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
USERNAME = os.environ["INSTAGRAM_USERNAME"]
STATE_FILE = "seen.json"


def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def load_seen():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return set(json.load(f)), False
    return set(), True  # first run


def save_seen(seen):
    with open(STATE_FILE, "w") as f:
        json.dump(sorted(seen), f)


def main():
    seen, first_run = load_seen()

    loader = instaloader.Instaloader()
    profile = instaloader.Profile.from_username(loader.context, USERNAME)

    current = []
    for post in islice(profile.get_posts(), 12):
        if post.is_video:
            current.append(post.shortcode)

    for code in current:
        if code not in seen:
            if not first_run:
                link = f"https://www.instagram.com/reel/{code}/"
                send_telegram(f"New reel from @{USERNAME}!\n{link}")
            seen.add(code)

    save_seen(seen)
    print("Done. First run:", first_run, "| Reels checked:", len(current))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error (will try again next time):", e)
