"use client"
import React, { useState } from 'react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || ''
const getApiBase = () => {
  if (API_BASE && API_BASE.length > 0) return API_BASE
  if (typeof window !== 'undefined') {
    return `${window.location.protocol}//${window.location.hostname}:8000`
  }
  return ''
}

export default function AgentsPage() {
  const [status, setStatus] = useState<any>(null)
  const [actionRes, setActionRes] = useState<any>(null)

  const fetchStatus = async () => {
    const r = await fetch(`${getApiBase()}/agents/status`)
    setStatus(await r.json())
  }

  const triggerSlackTest = async () => {
    const r = await fetch(`${getApiBase()}/agents/slack/action`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ action: 'send', payload: { channel: '#general', text: 'Test from dashboard' } }) })
    setActionRes(await r.json())
  }

  return (
    <main>
      <h1 className="text-2xl font-semibold mb-4">Agent Monitor</h1>
      <div className="flex gap-2 mb-4">
        <button onClick={fetchStatus} className="btn">Refresh Status</button>
        <button onClick={triggerSlackTest} className="btn">Trigger Slack Test</button>
      </div>

      <pre className="p-4 bg-slate-800 rounded text-sm">{JSON.stringify(status, null, 2)}</pre>
      <h2 className="mt-4">Last Action</h2>
      <pre className="p-4 bg-slate-800 rounded text-sm">{JSON.stringify(actionRes, null, 2)}</pre>
    </main>
  )
}
