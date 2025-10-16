# Demo Walkthrough — Weekly Review (local)

1. Start the backend:

```powershell
python main.py
```

2. Create some sample tasks (PowerShell / curl):

```powershell
curl -X POST "http://localhost:8000/tasks?source=notion&title=Finish+Q3+report&description=Draft+the+report"
curl -X POST "http://localhost:8000/tasks?source=slack&title=Reply+to+client&description=Provide+ETA"
```

3. Check analytics

```powershell
curl http://localhost:8000/analytics/overview
```

This lightweight demo simulates ingesting tasks and viewing analytics. For real integrations, configure Composio credentials and replace the ToolRouterStub.
