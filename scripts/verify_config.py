"""Simple config verification script.

This script loads environment variables from a local `.env` (if present) and prints
a summary table indicating which keys are loaded and whether they look valid.

Security: the script never prints secret values in full. It only shows presence,
length and a masked preview to help you confirm which variables are set locally.

Usage:
  python scripts/verify_config.py

If you don't have `python-dotenv` installed, install it with:
  python -m pip install python-dotenv
"""

from __future__ import annotations
import os
from typing import Dict, Optional

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

if load_dotenv:
    load_dotenv()  # read .env in cwd

# Keys to check and simple heuristics for validation
KEY_SPECS: Dict[str, Dict[str, Optional[str]]] = {
    "COMPOSIO_API_KEY": {"prefix": None},
    "OPENAI_API_KEY": {"prefix": "sk-"},
    "SLACK_BOT_TOKEN": {"prefix": "xoxb-"},
    "GMAIL_API_KEY": {"prefix": None},
    "NOTION_API_KEY": {"prefix": "ntn_"},
    "GOOGLE_DRIVE_KEY": {"prefix": "AIza"},
}


def mask_value(v: Optional[str]) -> str:
    """Return a masked preview for a secret (do not reveal full value)."""
    if not v:
        return ""
    if len(v) <= 8:
        return "*" * len(v)
    return v[:3] + "..." + v[-3:]


def check_key(name: str, spec: Dict[str, Optional[str]]) -> Dict[str, object]:
    v = os.getenv(name)
    present = bool(v)
    prefix = spec.get("prefix")
    prefix_ok: Optional[bool] = None
    if present and prefix:
        # v is str here because present is True
        prefix_ok = v.startswith(prefix)  # type: ignore[arg-type]
    length = len(v) if present else 0
    length_ok = length >= 8
    return {
        "name": name,
        "present": present,
        "prefix": prefix,
        "prefix_ok": prefix_ok,
        "length": length,
        "length_ok": length_ok,
        "preview": mask_value(v) if present else "",
    }


def main() -> None:
    results = [check_key(k, s) for k, s in KEY_SPECS.items()]

    # Print a simple table
    print("Configuration verification summary:\n")
    header = f"{'ENV VAR':<22}{'LOADED':<8}{'LEN':<6}{'PREFIX':<10}{'PREFIX_OK':<10}PREVIEW"
    print(header)
    print("-" * 80)
    for r in results:
        name = r["name"]
        loaded = "YES" if r["present"] else "NO"
        length = str(r["length"]) if r["present"] else "-"
        prefix = r["prefix"] or "-"
        prefix_ok = (
            "YES" if r["prefix_ok"] is True else ("NO" if r["prefix_ok"] is False else "-")
        )
        preview = r["preview"]
        print(f"{name:<22}{loaded:<8}{length:<6}{prefix:<10}{prefix_ok:<10}{preview}")

    print("\nNotes:")
    print(" - This script does not perform network validation. Use the dashboard or API clients to test keys against real services.")
    print(" - If a key is missing, create a local `.env` file at the project root with the required variables (do not commit it).")


if __name__ == '__main__':
    main()
