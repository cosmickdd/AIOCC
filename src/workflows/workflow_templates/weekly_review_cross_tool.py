from typing import Dict


def weekly_review_cross_tool_plan() -> Dict:
    return {
        "name": "weekly_review_cross_tool",
        "steps": [
            {"step": "fetch_emails", "description": "Collect starred/unread emails from Gmail", "payload": {"label": "STARRED"}},
            {"step": "notify", "description": "Send status summary to Slack", "payload": {"channel": "{{channel}}"}},
            {"step": "persist_summary", "description": "Create Notion summary page", "payload": {"database_id": "{{database_id}}"}},
        ],
    }
