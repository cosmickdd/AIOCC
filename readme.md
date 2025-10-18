# AI Operations Command Center (AIOCC)

An intelligent, lightweight operations command center for SMBs that unifies Gmail, Slack, Notion, and Google Drive through the Composio ToolRouter.

---

## Quick workflow execution (Weekly Review)

This repository includes a minimal WorkflowPlanner and a ToolRouter stub so you can simulate workflows locally without external credentials.

1. Start the backend (PowerShell):

```powershell
python main.py
```

2. Execute the weekly review workflow via the API:

```powershell
curl -X POST "http://localhost:8000/workflows/execute" -H "Content-Type: application/json" -d "{\"workflow_name\": \"weekly_review\"}"
```

3. Or run the demo runner locally (no server required):

```powershell
python demo_runner.py
```

The demo will print a step-by-step execution summary using the ToolRouter stub (no external API calls are made).

---

For full project setup and other details, see the project README in the repository root.
# AI Operations Command Center (AIOCC)

An intelligent, lightweight operations command center for SMBs that unifies Gmail, Slack, Notion, and Google Drive through the Composio ToolRouter.

---

## Table of Contents

- Project overview
- Problem statement
- Solution & key features
- Architecture
- Getting started (Windows)
- Environment variables & integrations
- Example Composio setup (Python)
- Example workflow (Weekly Status Check)
- Roadmap
- Security & privacy
- Testing & validation
- Contributors
- License
- Acknowledgements

## Project overview

AIOCC (AI Operations Command Center) is an agentic operations platform designed for small and medium businesses. It aggregates actionable items across common productivity tools, applies AI to detect risk and friction, and can take agentic corrective actions (reminders, escalations, and updates) while keeping humans in the loop.

Why it matters: SMBs rarely have the budget or time for heavy enterprise automation. AIOCC brings high-impact operational automation and visibility with serverless, cost-aware architecture and secure integrations via Composio ToolRouter.

## Problem statement

SMBs commonly suffer from tool fragmentation. Consequences include:

- Missed follow-ups and untracked tasks
- Duplicated efforts and unclear ownership
- Manual status tracking and poor visibility
- Increased response delays and team burnout

These inefficiencies cost teams time, focus, and money.

## Solution overview

AIOCC consolidates actionable items from Gmail, Slack, Notion, and Drive into a single orchestration layer powered by Composio ToolRouter and AI. It provides:

- Unified task aggregation
- AI-driven insights (overdue tasks, missing owners, workload imbalance)
- Agentic follow-ups and cross-tool sync
- Workflow templates for recurring routines
- Lightweight, serverless-first deployment for low cost

Core principles: least privilege integrations, human-in-the-loop controls, and transparent audit logging.

## Key features

- **Unified Task Aggregation** — Collect actionable items from flagged Gmail messages, Slack threads, Notion to-dos, and Drive documents.
- **AI Insights Engine** — Detect overdue tasks, missing owners, workload imbalance, and unresolved threads.
- **Agentic Follow-Ups** — Automatically send reminders, summaries, or escalations with configurable escalation paths.
- **Cross-Tool Sync** — Bi-directional status updates across connected apps.
- **Workflow Templates** — Automate common routines (weekly reviews, invoice approvals).
- **Lightweight & Cost-Aware** — Designed for serverless or on-demand execution to reduce continuous costs.

## Project architecture

AI Operations Command Center (AIOCC)

```
├── src/
│   ├── agents/
│   │   ├── gmail_agent.py
│   │   ├── slack_agent.py
│   │   ├── notion_agent.py
│   │   └── drive_agent.py
│   ├── workflows/
│   │   ├── reminder_agent.py
│   │   ├── escalation_agent.py
│   │   └── workflow_templates/
│   ├── core/
│   │   ├── toolrouter_config.py
│   │   ├── task_store.py
│   │   └── analytics.py
│   └── utils/
│       └── logger.py
├── dashboard/
│   └── app/
├── .env.example
├── requirements.txt
├── README.md
└── main.py
```

### Contract (minimal)

- Inputs: OAuth connections (Gmail, Slack, Notion, Drive) via Composio; environment configuration.
- Outputs: consolidated task list, notifications across channels, audit logs, and automated actions (reminders/escalations).
- Error modes: expired tokens, permission errors, transient API failures — retried and surfaced to human operators.

Edge cases considered: empty inboxes/threads, duplicate tasks from multiple sources, rate limits, and partial integration failures.

## Getting started (Windows)

### Prerequisites

- Python 3.9+ (recommended)
- Node.js (only if you plan to run the optional web dashboard)
- Composio SDK (install via pip)
- Developer credentials for Gmail, Slack, Notion, and Google Drive

### Quick start (PowerShell)

1. Clone the repository

   git clone https://github.com/<your-username>/ai-operations-command-center.git
   cd ai-operations-command-center

2. Create and activate a virtual environment (PowerShell)

   python -m venv venv
   venv\Scripts\Activate.ps1

3. Install Python dependencies

   pip install -r requirements.txt

4. Create a `.env` file from `.env.example` and populate the variables (see next section)

5. Start the backend

   python main.py

Optional: Frontend dashboard (if included)

   cd dashboard
   npm install
   npm run dev

Visit http://localhost:8000 (default) once the backend is running.

## Environment variables (.env.example)

Use a `.env` file (never store secrets in source control).

Example keys to set:

```
COMPOSIO_API_KEY=<your_composio_api_key>
OPENAI_API_KEY=<your_openai_api_key>

# App integrations
GMAIL_CLIENT_ID=<gmail_client_id>
GMAIL_CLIENT_SECRET=<gmail_client_secret>
SLACK_BOT_TOKEN=<slack_bot_token>
NOTION_TOKEN=<notion_integration_token>
GOOGLE_DRIVE_KEY=<drive_service_key>

# App configuration
PORT=8000
DEBUG=True
```

Scopes & least privilege: request only the minimal scopes needed for each integration (read-only where possible, write only for actions).

## Connecting Third-Party Tools (via Composio ToolRouter)

AIOCC uses Composio’s ToolRouter to securely connect and orchestrate services. Connections use OAuth and tokens are managed by Composio.

Steps to connect accounts:

1. Launch the app and open Settings → Integrations.
2. Click “Connect” next to Gmail / Slack / Notion / Drive.
3. Authenticate via OAuth. Composio handles token storage and refresh.
4. Optionally test each integration in Composio’s Remote Workbench.

Example Composio setup (Python)

```python
import os
from composio import Composio, ToolRouter

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
router = ToolRouter(composio)

# Example connections (Composio handles tokens & OAuth flow in production)
router.connect("gmail", token=os.getenv("GMAIL_CLIENT_ID"))
router.connect("slack", token=os.getenv("SLACK_BOT_TOKEN"))
router.connect("notion", token=os.getenv("NOTION_TOKEN"))
router.connect("drive", token=os.getenv("GOOGLE_DRIVE_KEY"))

# Use router to invoke tools, manage connections, plan, and multi-execute workflows
```

## Example workflow — Weekly Status Check (template)

Every Monday morning the workflow runs:

1. Fetch open tasks from Notion, flagged Gmail messages, and unresolved Slack threads.
2. AI summarizes tasks and creates a Notion summary page.
3. Send a Slack message requesting updates from assigned owners and email summary to manager via Gmail.
4. Wait 24 hours and re-check responses. Non-responders receive reminders or escalations.

This template uses Composio meta-tools: `plan` (workflow definition), `multi-execute` (create tasks/notifications), and `manage connections` (OAuth handling).

## Roadmap

- Microsoft 365 integration (Outlook + Teams)
- Fine-grained user permissions and role-based access
- Natural-language query interface ("Show me pending tasks")
- Meeting-notes summarization and action extraction
- Event-triggered automations (calendar, webhooks, cron)

## Security & privacy

- All secrets are stored via environment variables; tokens managed by Composio.
- Principle of least privilege for agent scopes.
- Full audit trails and logs for any agent actions.

## Testing & validation

### Unit tests

Run unit tests locally using pytest:

```
pytest tests/
```

### Integration testing

- Use Composio sandbox / Remote Workbench to validate OAuth scopes and API calls.
- Include tests for expired tokens, partial failures, and retry logic.

### Quality gates

- Build: n/a (Python script)
- Linting: run flake8 or pylint as configured
- Tests: pytest (unit + small integration mocks)

## Testing & CI (developer)

Unit and integration tests are provided under the `tests/` directory. The project includes a GitHub Actions workflow that runs tests on push and pull requests.

Run tests locally (after installing dependencies):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
```

GitHub Actions:

- Workflow file: `.github/workflows/tests.yml`
- Runs on pushes and PRs against `main` using Python 3.9 and executes `pytest`.


## Contributors

- Utkarsh Tiwari — Project Lead
- [Team Member 2] — AI & Integration Engineer
- [Team Member 3] — UI/UX & Frontend Developer
- [Team Member 4] — Testing & Deployment

If you'd like to contribute, please open a pull request or an issue describing the enhancement.

## License

This project is licensed under the MIT License — see the LICENSE file for details.

## Acknowledgements

Built with ❤️ using Composio ToolRouter, OpenAI APIs, Notion SDK, Slack SDK, and Google APIs.

---

## Development Notes

- Why `composio-sdk` was replaced with a stub

   The `composio-sdk` entry in `requirements.txt` was removed because the package is not available on PyPI and would block dependency installation. During early development we use a local `ToolRouterStub` (in `src/core/toolrouter_config.py`) that implements the minimal interface required by `WorkflowPlanner` so you can run tests and iterate without external credentials.

- How to plug in the real SDK later

   1. If `composio-sdk` becomes available on PyPI, add it back to `requirements.txt` and run `pip install -r requirements.txt`.
   2. Prefer adding an adapter that implements `ToolRouterInterface` (see `src/core/interfaces.py`) and register the real client behind that interface. The `ToolRouterStub` already implements the same methods and can be swapped with a real implementation with minimal changes.
   3. If the real SDK is private, configure pip to use a private index or vendor the SDK into your environment and document the install steps in this README.

- Running tests and CI locally

   - Create venv and install deps:

      ```powershell
      python -m venv venv
      & .\venv\Scripts\python.exe -m pip install --upgrade pip
      & .\venv\Scripts\python.exe -m pip install -r requirements.txt
      ```

   - Run full test suite:

      ```powershell
      & .\venv\Scripts\python.exe -m pytest -q
      ```

   - Run linters and type checks (locally match CI):

      ```powershell
      & .\venv\Scripts\python.exe -m pip install ruff mypy black
      & .\venv\Scripts\python.exe -m ruff check .
      & .\venv\Scripts\python.exe -m mypy src
      & .\venv\Scripts\python.exe -m black --check .
      ```
## Cross-Tool Orchestration (Gmail + Slack + Notion)

This repository now includes a cross-tool workflow template `weekly_review_cross_tool` that demonstrates how AIOCC can orchestrate Gmail, Slack, and Notion in a single automation.

Quick demo (start the backend or run the demo script):

1) Run via HTTP API (backend must be running at localhost:8000):

```powershell
curl -X POST http://localhost:8000/workflows/execute \
   -H "Content-Type: application/json" \
   -d '{"workflow_name": "weekly_review_cross_tool", "params": {"channel": "#general", "database_id": "db_1"}}'
```

2) Run demo script locally (no server required):

```powershell
python scripts/demo_cross_tool.py
```

Required environment variables (add to `.env` from `.env.example`):

```
SLACK_BOT_TOKEN=
GMAIL_API_KEY=
NOTION_API_KEY=
OPENAI_API_KEY=
```

Interpreting structured workflow logs

- Each workflow run is saved as a structured JSON `log` in the `workflow_runs` table. The `log` contains an `executions` list showing each tool action, its status, and tool-specific outputs (for example Gmail returns `messages`, Slack returns `ts`, Notion returns `page_id`).
- Example `log` fragment:

```json
{
   "executions": [
      {"tool": "gmail", "action": "fetch_messages", "status": "ok", "messages": [...]},
      {"tool": "slack", "action": "post_message", "status": "ok", "ts": "12345"},
      {"tool": "notion", "action": "create_summary_page", "status": "ok", "page_id": "p_1"}
   ],
   "params": {"channel": "#tests", "database_id": "db_1"}
}
```

The cross-tool demo shows how data flows from Gmail -> Slack -> Notion. This structured logging makes it easy to build analytics on success rate, average duration, and failure modes.


