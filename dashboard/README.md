AI Operations Command Center - Dashboard

Local dev:

1. cd dashboard
2. npm install
3. npm run dev

The dashboard expects the backend API to be available at the same origin during development
or set FRONTEND_URL in the backend `.env` to allow CORS. The dashboard provides two pages:
- / -> Overview cards (Success Rate, Avg Duration, Total Runs)
- /analytics -> Recent failures list
