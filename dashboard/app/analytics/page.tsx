import React from 'react'
import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(r => r.json())

export default function AnalyticsPage() {
  const { data } = useSWR('/analytics/failures', fetcher)
  const failures = data?.failures || []

  return (
    <main>
      <h1 className="text-2xl font-semibold mb-4">Recent Failures</h1>
      <div className="space-y-2">
        {failures.map((f: any) => (
          <div key={f.id} className="card">Workflow: {f.workflow_name} — Status: {f.status}</div>
        ))}
      </div>
    </main>
  )
}
