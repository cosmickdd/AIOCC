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

export default function LogsPage() {
  const [logs, setLogs] = useState<any[]>([])

  useEffect(() => {
    fetch(`${getApiBase()}/workflows/logs?limit=50`).then(r => r.json()).then(d => setLogs(d.runs || []))
  }, [])

  return (
    <main>
      <h1 className="text-2xl font-semibold mb-4">Workflow Logs</h1>
      <div className="space-y-2">
        {logs.map((l: any, i: number) => (
          <div key={i} className="card">
            <div><strong>{l.workflow_name}</strong> — {l.status}</div>
            <pre className="mt-2 text-sm">{JSON.stringify(l.log, null, 2)}</pre>
          </div>
        ))}
      </div>
    </main>
  )
}
