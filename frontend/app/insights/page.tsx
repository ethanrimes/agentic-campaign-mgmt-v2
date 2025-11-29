// frontend/app/insights/page.tsx

'use client'

import { useState, useEffect } from 'react'
import { getInsightReports } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'
import InsightReportCard from '@/components/insights/InsightReportCard'
import { BarChart3 } from 'lucide-react'
import type { InsightReport } from '@/types'

export default function InsightsPage() {
  const { selectedAsset } = useBusinessAsset()
  const [reports, setReports] = useState<InsightReport[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadReports() {
      if (!selectedAsset) return

      try {
        setLoading(true)
        const data = await getInsightReports(selectedAsset.id)
        setReports(data)
      } catch (error) {
        console.error('Failed to load insight reports:', error)
      } finally {
        setLoading(false)
      }
    }

    loadReports()
  }, [selectedAsset])

  if (!selectedAsset || loading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="text-center py-16">
          <BarChart3 className="w-16 h-16 text-green-400 mx-auto mb-4 animate-pulse" />
          <p className="text-lg text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto animate-fade-in">
      <div className="relative mb-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-100/30 via-blue-100/20 to-slate-100/30 rounded-3xl blur-3xl"></div>
        <div className="relative bg-white rounded-2xl p-8 border border-slate-200 shadow-xl">
          <div className="flex items-center gap-4 mb-3">
            <div className="relative">
              <div className="w-14 h-14 bg-gradient-to-br from-green-600 to-emerald-600 rounded-2xl flex items-center justify-center shadow-lg">
                <BarChart3 className="w-7 h-7 text-white" />
              </div>
              <div className="absolute inset-0 bg-green-500 rounded-2xl blur-xl opacity-30"></div>
            </div>
            <div>
              <h1 className="text-4xl font-bold text-slate-900">
                Insight Reports
              </h1>
              <p className="text-slate-600 mt-1">
                Performance analysis and strategic recommendations from the insights agent
              </p>
            </div>
          </div>
          <div className="mt-6 flex items-center gap-3">
            <div className="bg-slate-100 px-4 py-2 rounded-full border border-slate-200">
              <span className="text-sm font-bold text-slate-900">{reports.length}</span>
              <span className="text-sm text-slate-600 ml-1">total reports</span>
            </div>
          </div>
        </div>
      </div>

      {reports.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-slate-200 shadow-xl">
          <div className="relative inline-block mb-6">
            <BarChart3 className="w-16 h-16 text-slate-400 mx-auto" />
            <div className="absolute inset-0 bg-slate-500 blur-2xl opacity-20"></div>
          </div>
          <p className="text-lg font-semibold text-slate-900 mb-2">No insight reports found</p>
          <p className="text-sm text-slate-600 max-w-md mx-auto">
            Run the insights agent to generate performance analysis reports
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {reports.map((report, index) => (
            <div key={report.id} className="animate-slide-up" style={{ animationDelay: `${index * 50}ms` }}>
              <InsightReportCard report={report} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
