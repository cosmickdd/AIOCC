"""Run lightweight, non-destructive integration checks for configured keys.

Checks performed (only if the corresponding key is present):
- Slack: calls auth.test to verify token validity.
- OpenAI: a small request to models.list (non-billing test) if supported by SDK; otherwise HEAD to api endpoint.
- Google Drive: attempts to list files using an API key (may be limited depending on key type).

This script never prints secrets. It prints PASS/FAIL and short diagnostics.

Run with your venv activated:
  python scripts/integration_test.py

Install dependencies:
  python -m pip install python-dotenv requests openai slack-sdk google-api-python-client
"""

from __future__ import annotations
import os
import sys
from typing import Optional

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

import requests


def check_slack(token: str) -> bool:
    url = "https://slack.com/api/auth.test"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.post(url, headers=headers, timeout=10)
        j = r.json()
        return bool(j.get("ok"))
    except Exception as e:
        print("Slack check error:", e)
        return False


def check_openai(key: str) -> bool:
    # Use simple HTTP ping to OpenAI account endpoints to avoid requiring SDK versions.
    url = "https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {key}"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print("OpenAI check error:", e)
        return False


def check_google_drive(api_key: str) -> bool:
    # Use a lightweight files list request (may require OAuth for full access);
    # for API keys this can be limited; we treat 200 as success.
    url = "https://www.googleapis.com/drive/v3/files"
    params = {"pageSize": 1, "key": api_key}
    try:
        r = requests.get(url, params=params, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print("Google Drive check error:", e)
        return False


def main() -> None:
    keys = {
        "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GOOGLE_DRIVE_KEY": os.getenv("GOOGLE_DRIVE_KEY"),
    }

    print("Integration test summary:\n")

    if keys["SLACK_BOT_TOKEN"]:
        ok = check_slack(keys["SLACK_BOT_TOKEN"])
        print(f"Slack: {'PASS' if ok else 'FAIL'}")
    else:
        print("Slack: SKIPPED (no SLACK_BOT_TOKEN)")

    if keys["OPENAI_API_KEY"]:
        ok = check_openai(keys["OPENAI_API_KEY"])
        print(f"OpenAI: {'PASS' if ok else 'FAIL'}")
    else:
        print("OpenAI: SKIPPED (no OPENAI_API_KEY)")

    if keys["GOOGLE_DRIVE_KEY"]:
        ok = check_google_drive(keys["GOOGLE_DRIVE_KEY"])
        print(f"Google Drive: {'PASS' if ok else 'FAIL'}")
    else:
        print("Google Drive: SKIPPED (no GOOGLE_DRIVE_KEY)")


if __name__ == "__main__":
    main()
