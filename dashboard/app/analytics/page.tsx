"use client"
import React, { useEffect, useState } from 'react'
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip as RTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts'

function formatSeriesForLine(series: any[]) {
  return series.map((s) => ({ date: s.date, success: s.success, failure: s.failure }))
}

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
  const [days, setDays] = useState(30)
  const [workflow, setWorkflow] = useState<string | null>(null)
  const [workflowsList, setWorkflowsList] = useState<string[]>([])
  const [startDate, setStartDate] = useState<string | null>(null)
  const [endDate, setEndDate] = useState<string | null>(null)
  const { data: failuresData } = useFetch('/analytics/failures')
  const failures = failuresData?.failures || []
  // build trends query: either days-based or explicit start/end if provided
  let trendsQuery = `/analytics/trends?days=${days}`
  if (workflow) trendsQuery += `&workflow=${encodeURIComponent(workflow)}`
  if (startDate) trendsQuery += `&start=${encodeURIComponent(startDate)}`
  if (endDate) trendsQuery += `&end=${encodeURIComponent(endDate)}`
  const { data: trendsData } = useFetch(trendsQuery)
  const series = trendsData?.series || []

  // fetch insights for workflow activity
  const { data: insights } = useFetch('/analytics/insights')
  const mostActive = insights?.metrics?.most_active_workflows || []

  // fetch workflows list on mount
  useEffect(() => {
    let mounted = true
    fetcher('/workflows/list')
      .then((d) => {
        if (!mounted) return
        const items = (d?.workflows || [])
        setWorkflowsList(items)
      })
      .catch(() => {})
    return () => {
      mounted = false
    }
  }, [])

  return (
    <main>
      <h1 className="text-2xl font-semibold mb-4">Recent Failures</h1>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-sm">Start Date</label>
          <input type="date" value={startDate || ''} onChange={(e) => setStartDate(e.target.value || null)} className="mt-1 p-2 border rounded w-full" />
        </div>
        <div>
          <label className="block text-sm">End Date</label>
          <input type="date" value={endDate || ''} onChange={(e) => setEndDate(e.target.value || null)} className="mt-1 p-2 border rounded w-full" />
        </div>
        <div>
          <label className="block text-sm">Workflow</label>
          <select value={workflow || ''} onChange={(e) => setWorkflow(e.target.value || null)} className="mt-1 p-2 border rounded w-full">
            <option value="">All workflows</option>
            {workflowsList.map((w) => (
              <option key={w} value={w}>{w}</option>
            ))}
          </select>
        </div>
        <div className="flex items-end">
          <button onClick={() => { setDays(30); setWorkflow(null) }} className="btn">Reset Filters</button>
        </div>
      </div>

      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Success / Failure Trend</h2>
        <div style={{ width: '100%', height: 260 }}>
          <ResponsiveContainer>
            <LineChart data={formatSeriesForLine(series)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <RTooltip />
              <Line type="monotone" dataKey="success" stroke="#10b981" />
              <Line type="monotone" dataKey="failure" stroke="#ef4444" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Most Active Workflows</h2>
        <div style={{ width: '100%', height: 240 }}>
          <ResponsiveContainer>
            <BarChart data={mostActive || []} layout="vertical">
              <XAxis type="number" />
              <YAxis dataKey="workflow" type="category" width={160} />
              <RTooltip />
              <Bar dataKey="runs" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <div className="space-y-2">
        {failures.map((f: any) => (
          <div key={f.id} className="card">Workflow: {f.workflow_name} — Status: {f.status}</div>
        ))}
      </div>
    </main>
  )
}
