// frontend/app/insights/page.tsx

import { getInsightReports } from '@/lib/api'
import InsightReportCard from '@/components/insights/InsightReportCard'
import { BarChart3 } from 'lucide-react'

export const dynamic = 'force-dynamic'

export default async function InsightsPage() {
  const reports = await getInsightReports()

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <BarChart3 className="w-8 h-8 text-green-600" />
          <h1 className="text-3xl font-bold text-gray-900">Insight Reports</h1>
        </div>
        <p className="text-gray-600">
          Engagement analysis reports showing what content works with your audience
        </p>
        <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
          <span className="font-medium">{reports.length} total reports</span>
        </div>
      </div>

      {reports.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No insight reports found</p>
          <p className="text-sm text-gray-500 mt-2">
            Run the insights analysis CLI command to generate reports
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {reports.map((report) => (
            <InsightReportCard key={report.id} report={report} />
          ))}
        </div>
      )}
    </div>
  )
}
