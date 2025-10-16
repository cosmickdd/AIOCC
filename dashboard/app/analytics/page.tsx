"use client"
import React, { useEffect, useState } from 'react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || ''
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

export default function AnalyticsPage() {
  const { data } = useFetch('/analytics/failures')
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
