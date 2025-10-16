"use client"
import React, { useEffect, useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || ''
// If NEXT_PUBLIC_API_URL isn't set at build time, fall back at runtime to the
// backend on the same host but port 8000 (useful for local dev).
const getApiBase = () => {
  if (API_BASE && API_BASE.length > 0) return API_BASE
  if (typeof window !== 'undefined') {
    return `${window.location.protocol}//${window.location.hostname}:8000`
  }
  return ''
}
const fetcher = (url: string) => fetch(`${getApiBase()}${url}`).then(r => r.json())

function useFetch(url: string) {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<any>(null)
  useEffect(() => {
    let mounted = true
    fetcher(url)
      .then((d) => mounted && setData(d))
      .catch((e) => mounted && setError(e))
    return () => {
      mounted = false
    }
  }, [url])
  return { data, error }
}

export default function Page() {
  const { data, error } = useFetch('/analytics/insights')
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
      <section className="mt-6">
        <h2 className="text-xl font-semibold mb-2">Top Failed Tools</h2>
        {(!m.top_failed_tools || m.top_failed_tools.length === 0) ? (
          <div className="p-4 rounded bg-slate-800">No failed tools recorded</div>
        ) : (
          <div style={{ width: '100%', height: 240 }}>
            <ResponsiveContainer>
              <BarChart data={m.top_failed_tools || []} layout="vertical" margin={{ left: 20 }}>
                <XAxis type="number" />
                <YAxis dataKey="tool" type="category" width={120} />
                <Tooltip />
                <Bar dataKey="fails" fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </section>
    </main>
  )
}
