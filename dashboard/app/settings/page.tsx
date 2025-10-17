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

export default function SettingsPage() {
  const [integrations, setIntegrations] = useState<any>(null)

  useEffect(() => {
    // Read-only: show which integrations appear configured via backend settings
    fetch(`${getApiBase()}/integrations`).then(r => r.json()).then(d => setIntegrations(d)).catch(() => setIntegrations(null))
  }, [])

  return (
    <main>
      <h1 className="text-2xl font-semibold mb-4">Settings & Integrations</h1>
      <pre className="p-4 bg-slate-800 rounded">{JSON.stringify(integrations, null, 2)}</pre>
    </main>
  )
}
