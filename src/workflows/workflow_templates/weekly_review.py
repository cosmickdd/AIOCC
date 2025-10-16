"""Example workflow template for Weekly Review.

This file contains a programmatic description of a simple weekly workflow.
"""

from typing import Dict


def weekly_review_plan() -> Dict:
    return {
        "name": "weekly_review",
        "steps": [
            {"step": "fetch_tasks", "description": "Collect open tasks from Notion, Gmail, Slack", "payload": {}},
            {"step": "summarize", "description": "Generate AI summary of current tasks", "payload": {"model": "gpt-4"}},
            {"step": "notify", "description": "Send summary to Slack and email manager", "payload": {"channel": "{{channel}}", "manager": "{{manager_email}}"}},
        ],
    }
