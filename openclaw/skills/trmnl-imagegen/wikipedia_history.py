#!/usr/bin/env python3
"""
Fetch real "This Day in History" events from Wikipedia
"""

import random
import re

import requests
from datetime import datetime


def get_wikipedia_on_this_day():
    """Fetch a historical event from Wikipedia for today's date"""
    today = datetime.now()
    month = today.strftime("%m")
    day = today.strftime("%d")

    try:
        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
        response = requests.get(
            url,
            headers={"User-Agent": "TRMNLBot/1.0 (daily history display)"},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            events = data.get("events", [])

            if events:
                event = random.choice(events[:15])
                year = event.get("year", "")
                text = event.get("text", "")

                # Clean up text
                text = re.sub(r"\[.*?\]", "", text)
                text = text[:200]

                return f"In {year}: {text}"
    except Exception as e:
        print(f"Error fetching Wikipedia: {e}")

    return None


if __name__ == "__main__":
    event = get_wikipedia_on_this_day()
    print(event or "Could not fetch today's event")
