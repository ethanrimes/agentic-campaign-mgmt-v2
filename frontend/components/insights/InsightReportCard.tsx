// frontend/components/insights/InsightReportCard.tsx

'use client'

import ExpandableCard from '@/components/common/ExpandableCard'
import { formatDateTime, formatRelativeTime } from '@/lib/utils'
import { Activity } from 'lucide-react'
import type { InsightReport } from '@/types'

interface InsightReportCardProps {
  report: InsightReport
}

export default function InsightReportCard({ report }: InsightReportCardProps) {
  const preview = (
    <div className="space-y-2">
      <p className="text-sm font-medium text-gray-900">{report.summary}</p>
      <div className="flex items-center gap-4 text-xs text-gray-500">
        <span>{report.tool_calls.length} tool calls</span>
      </div>
    </div>
  )

  return (
    <ExpandableCard
      title={`Insight Report`}
      subtitle={`Generated ${formatRelativeTime(report.created_at)} • ${report.created_by}`}
      preview={preview}
      badge={
        <span className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded-full flex items-center gap-1">
          <Activity className="w-3 h-3" />
          {report.tool_calls.length} calls
        </span>
      }
    >
      <div className="space-y-6">
        {/* Summary */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Summary</h4>
          <p className="text-gray-700">{report.summary}</p>
        </div>

        {/* Findings */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Findings</h4>
          <div className="prose prose-gray max-w-none">
            <p className="text-gray-700 whitespace-pre-line">{report.findings}</p>
          </div>
        </div>

        {/* Tool Calls */}
        {report.tool_calls && report.tool_calls.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3">
              Tool Calls ({report.tool_calls.length})
            </h4>
            <div className="space-y-3">
              {report.tool_calls.map((call, i) => (
                <div key={i} className="p-4 bg-gray-50 rounded-md border border-gray-200">
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-sm font-medium text-gray-900">{call.tool_name}</span>
                    <span className="text-xs text-gray-500">
                      {formatDateTime(call.timestamp)}
                    </span>
                  </div>

                  {/* Arguments */}
                  <div className="mb-2">
                    <p className="text-xs font-semibold text-gray-700 mb-1">Arguments:</p>
                    <pre className="text-xs text-gray-600 bg-white p-2 rounded border border-gray-200 overflow-x-auto">
                      {JSON.stringify(call.arguments, null, 2)}
                    </pre>
                  </div>

                  {/* Result */}
                  <div>
                    <p className="text-xs font-semibold text-gray-700 mb-1">Result:</p>
                    <pre className="text-xs text-gray-600 bg-white p-2 rounded border border-gray-200 overflow-x-auto max-h-40">
                      {JSON.stringify(call.result, null, 2)}
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Metadata */}
        <div className="pt-4 border-t border-gray-100">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="text-xs font-semibold text-gray-500 mb-1">Created</h4>
              <p className="text-sm text-gray-900">{formatDateTime(report.created_at)}</p>
            </div>
            <div>
              <h4 className="text-xs font-semibold text-gray-500 mb-1">Model</h4>
              <p className="text-sm text-gray-900">{report.created_by}</p>
            </div>
          </div>
        </div>
      </div>
    </ExpandableCard>
  )
}
