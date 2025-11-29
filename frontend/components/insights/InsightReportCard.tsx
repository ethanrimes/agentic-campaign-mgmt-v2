// frontend/components/insights/InsightReportCard.tsx

'use client'

import ExpandableCard from '@/components/common/ExpandableCard'
import { formatDateTime, formatRelativeTime } from '@/lib/utils'
import { Activity } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import type { InsightReport } from '@/types'

interface InsightReportCardProps {
  report: InsightReport
}

export default function InsightReportCard({ report }: InsightReportCardProps) {
  const preview = (
    <div className="space-y-3">
      <p className="text-sm font-medium text-gray-900 leading-relaxed">{report.summary}</p>
      <div className="flex items-center gap-3">
        <span className="flex items-center gap-1.5 bg-green-50 text-green-700 px-3 py-1.5 rounded-full text-xs font-medium border border-green-100">
          <Activity className="w-3.5 h-3.5" />
          {report.tool_calls.length} tool calls
        </span>
      </div>
    </div>
  )

  return (
    <ExpandableCard
      title={`Insight Report`}
      subtitle={`Generated ${formatRelativeTime(report.created_at)} • ${report.created_by}`}
      preview={preview}
      badge={
        <span className="text-xs bg-gradient-to-r from-green-50 to-emerald-50 text-green-700 px-3 py-1.5 rounded-full flex items-center gap-1.5 font-medium border border-green-200">
          <Activity className="w-3.5 h-3.5" />
          {report.tool_calls.length} calls
        </span>
      }
    >
      <div className="space-y-6">
        {/* Summary */}
        <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-100">
          <h4 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
            <div className="w-1 h-4 bg-gradient-to-b from-green-500 to-emerald-500 rounded-full"></div>
            Executive Summary
          </h4>
          <p className="text-gray-700 leading-relaxed">{report.summary}</p>
        </div>

        {/* Findings */}
        <div className="p-4 bg-gradient-to-br from-blue-50/50 to-purple-50/50 rounded-xl border border-blue-100/50">
          <h4 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
            <div className="w-1 h-4 bg-gradient-to-b from-blue-500 to-purple-500 rounded-full"></div>
            Detailed Findings
          </h4>
          <div className="prose prose-sm prose-gray max-w-none prose-headings:text-gray-900 prose-headings:font-bold prose-h2:text-base prose-h2:mt-4 prose-h2:mb-2 prose-h3:text-sm prose-p:text-gray-700 prose-p:leading-relaxed prose-ul:my-2 prose-li:my-0.5 prose-strong:text-gray-900 prose-table:text-sm">
            <ReactMarkdown>{report.findings}</ReactMarkdown>
          </div>
        </div>

        {/* Tool Calls */}
        {report.tool_calls && report.tool_calls.length > 0 && (
          <div>
            <h4 className="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center text-white text-xs font-bold">
                {report.tool_calls.length}
              </div>
              Tool Executions
            </h4>
            <div className="space-y-3">
              {report.tool_calls.map((call, i) => (
                <div key={i} className="group p-4 bg-white rounded-xl border border-gray-200 shadow-soft hover:shadow-glow hover:border-primary-200 transition-all overflow-hidden">
                  <div className="flex items-start justify-between mb-3">
                    <span className="inline-flex items-center gap-2 text-sm font-bold text-gray-900 bg-gradient-to-r from-primary-50 to-secondary-50 px-3 py-1.5 rounded-lg border border-primary-100">
                      {call.tool_name}
                    </span>
                    <span className="text-xs text-gray-500 font-medium">
                      {formatDateTime(call.timestamp)}
                    </span>
                  </div>

                  {/* Arguments */}
                  <div className="mb-3">
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Arguments:</p>
                    <pre className="text-xs text-gray-700 bg-gray-50 p-3 rounded-lg border border-gray-200 overflow-x-auto font-mono">
                      {JSON.stringify(call.arguments, null, 2)}
                    </pre>
                  </div>

                  {/* Result */}
                  <div>
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Result:</p>
                    <pre className="text-xs text-gray-700 bg-gradient-to-br from-green-50 to-emerald-50 p-3 rounded-lg border border-green-100 overflow-x-auto max-h-40 font-mono">
                      {JSON.stringify(call.result, null, 2)}
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Metadata */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-soft">
            <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Created</h4>
            <p className="text-sm text-gray-900 font-medium">{formatDateTime(report.created_at)}</p>
          </div>
          <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-100 shadow-soft">
            <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">AI Model</h4>
            <p className="text-sm text-purple-900 font-medium">{report.created_by}</p>
          </div>
        </div>
      </div>
    </ExpandableCard>
  )
}
