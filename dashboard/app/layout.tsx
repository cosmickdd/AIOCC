import './globals.css'
import React from 'react'
import Link from 'next/link'

export const metadata = {
  title: 'AIOCC Dashboard',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="max-w-6xl mx-auto p-6">
          <header className="mb-6 flex items-center justify-between">
            <div className="text-xl font-bold">AIOCC</div>
            <nav className="space-x-4">
              <Link href="/" className="text-slate-300 hover:underline">Home</Link>
              <Link href="/analytics" className="text-slate-300 hover:underline">Analytics</Link>
              <Link href="/agents" className="text-slate-300 hover:underline">Agents</Link>
              <Link href="/logs" className="text-slate-300 hover:underline">Logs</Link>
              <Link href="/settings" className="text-slate-300 hover:underline">Settings</Link>
            </nav>
          </header>
          {children}
        </div>
      </body>
    </html>
  )
}
