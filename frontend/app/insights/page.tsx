// frontend/app/insights/page.tsx

import { getInsightReports } from '@/lib/api'
import InsightReportCard from '@/components/insights/InsightReportCard'
import { BarChart3 } from 'lucide-react'

export const dynamic = 'force-dynamic'

export default async function InsightsPage() {
  const reports = await getInsightReports()

  return (
    <div className="max-w-6xl mx-auto animate-fade-in">
      <div className="relative mb-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-green-100/50 via-emerald-100/30 to-green-100/50 rounded-3xl blur-3xl"></div>
        <div className="relative glass rounded-2xl p-8 border border-white/50 shadow-soft">
          <div className="flex items-center gap-4 mb-3">
            <div className="relative">
              <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl flex items-center justify-center shadow-lg">
                <BarChart3 className="w-7 h-7 text-white" />
              </div>
              <div className="absolute inset-0 bg-green-500 rounded-2xl blur-xl opacity-30"></div>
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                Insight Reports
              </h1>
              <p className="text-gray-600 mt-1">
                Engagement analysis reports showing what content works with your audience
              </p>
            </div>
          </div>
          <div className="mt-6 flex items-center gap-3">
            <div className="glass px-4 py-2 rounded-full border border-white/30">
              <span className="text-sm font-bold text-gray-900">{reports.length}</span>
              <span className="text-sm text-gray-600 ml-1">total reports</span>
            </div>
          </div>
        </div>
      </div>

      {reports.length === 0 ? (
        <div className="text-center py-16 glass rounded-2xl border border-white/50 shadow-soft">
          <div className="relative inline-block mb-6">
            <BarChart3 className="w-16 h-16 text-green-400 mx-auto" />
            <div className="absolute inset-0 bg-green-500 blur-2xl opacity-20"></div>
          </div>
          <p className="text-lg font-semibold text-gray-900 mb-2">No insight reports found</p>
          <p className="text-sm text-gray-600 max-w-md mx-auto">
            Run the insights analysis CLI command to generate engagement reports
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
