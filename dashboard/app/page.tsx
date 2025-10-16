import React from 'react'
import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(r => r.json())

export default function Page() {
  const { data, error } = useSWR('/analytics/insights', fetcher)
  if (error) return <div>Error loading metrics</div>
  if (!data) return <div>Loading...</div>

  const m = data.metrics || {}

  return (
    <main>
      <h1 className="text-3xl font-bold mb-6">AIOCC Dashboard</h1>
      <div className="grid grid-cols-3 gap-4">
        <div className="card"> <h3>Success Rate</h3> <p className="text-2xl">{m.success_rate?.toFixed(1)}%</p></div>
        <div className="card"> <h3>Avg Duration (s)</h3> <p className="text-2xl">{m.avg_duration?.toFixed(1)}</p></div>
        <div className="card"> <h3>Total Runs</h3> <p className="text-2xl">{m.total_runs}</p></div>
      </div>
    </main>
  )
}
