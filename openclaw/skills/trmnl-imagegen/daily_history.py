#!/usr/bin/env python3
"""
Daily "This Day in History" image generator for TRMNL
Runs via cron at 6am daily
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import requests

# Read credentials from environment variables
TRMNL_WEBHOOK_URL = os.environ.get("TRMNL_WEBHOOK_URL", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Add skill directory to path
sys.path.insert(0, str(Path(__file__).parent))
from skill import skill
from wikipedia_history import get_wikipedia_on_this_day


def summarize_caption(event, max_chars=35):
    """Use GPT-4o-mini to summarize an event into a short caption."""
    if len(event) <= max_chars:
        return event

    if not OPENAI_API_KEY:
        return event[:max_chars - 3] + "..."

    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": "Bearer " + OPENAI_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "max_tokens": 60,
                "messages": [
                    {
                        "role": "user",
                        "content": "Summarize this historical event in " + str(max_chars) + " characters or fewer. Return ONLY the summary, nothing else.\n\n" + event,
                    }
                ],
            },
            timeout=10,
        )
        if resp.status_code == 200:
            summary = resp.json()["choices"][0]["message"]["content"].strip()
            if len(summary) <= max_chars:
                return summary
            print("Summary too long (" + str(len(summary)) + " chars): " + summary)
    except Exception as e:
        print("Summarize error: " + str(e))

    return event[:max_chars - 3] + "..."


def make_image_prompt(event):
    """Use GPT-4o-mini to create a safe, visual DALL-E prompt from the event."""
    if not OPENAI_API_KEY:
        return "A historical scene in vintage engraving style"

    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": "Bearer " + OPENAI_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": "Create a short DALL-E image prompt depicting this historical event as a peaceful visual scene. Focus on architecture, landscape, people, or objects. Avoid any violent, military, or politically sensitive language. Return ONLY the image description, under 80 characters.\n\n" + event,
                    }
                ],
            },
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("Prompt generation error: " + str(e))

    return "A historical scene in vintage engraving style"


def main():
    """Generate and send daily history image"""
    skill.webhook_url = TRMNL_WEBHOOK_URL
    skill.api_key = OPENAI_API_KEY

    today = datetime.now()
    date_str = today.strftime("%B %d")

    # Fetch a real historical event from Wikipedia
    event = get_wikipedia_on_this_day()
    if not event:
        print("Warning: Could not fetch Wikipedia event, using fallback")
        event = "A historical scene from " + date_str

    print("Generating daily history image for " + date_str)
    print("Event: " + event)

    # Summarize for the TRMNL title bar
    caption = summarize_caption(event)
    print("Caption: " + caption)

    # Create a safe visual prompt for DALL-E
    scene = make_image_prompt(event)
    print("Scene prompt: " + scene)

    prompt = scene + ". Vintage black and white newspaper illustration, engraving style, high contrast. IMPORTANT: absolutely no text, no words, no letters, no labels, no captions anywhere in the image"

    result = skill.process_request(prompt, style="vintage", caption=caption)
    print(result)


if __name__ == "__main__":
    main()
