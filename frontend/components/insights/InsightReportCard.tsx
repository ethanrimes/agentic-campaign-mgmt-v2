// frontend/components/insights/InsightReportCard.tsx

'use client'

import ExpandableCard from '@/components/common/ExpandableCard'
import { formatDateTime, formatRelativeTime } from '@/lib/utils'
import { Activity, Brain, Clock, Code } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import type { InsightReport } from '@/types'

interface InsightReportCardProps {
  report: InsightReport
}

export default function InsightReportCard({ report }: InsightReportCardProps) {
  const preview = (
    <div className="space-y-3">
      <p className="text-sm font-medium text-slate-700 dark:text-slate-200 leading-relaxed line-clamp-2">{report.summary}</p>
      <div className="flex items-center gap-3">
        <span className="flex items-center gap-1.5 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 px-3 py-1 rounded-full text-xs font-medium border border-green-100 dark:border-green-800">
          <Activity className="w-3.5 h-3.5" />
          {report.tool_calls.length} tool calls
        </span>
      </div>
    </div>
  )

  return (
    <ExpandableCard
      title={`Insight Report`}
      subtitle={`Generated ${formatRelativeTime(report.created_at)}`}
      preview={preview}
      badge={
        <span className="text-xs bg-gradient-to-r from-green-500 to-emerald-500 text-white px-2.5 py-1 rounded-full flex items-center gap-1.5 font-bold shadow-sm">
          <Activity className="w-3 h-3" />
          {report.tool_calls.length}
        </span>
      }
    >
      <div className="space-y-8 p-2">
        {/* Summary */}
        <div className="p-6 rounded-2xl bg-green-50/50 dark:bg-green-900/10 border border-green-100 dark:border-green-800">
          <h4 className="text-sm font-bold text-green-900 dark:text-green-100 mb-3 flex items-center gap-2">
            <Brain className="w-4 h-4 text-green-600 dark:text-green-400" />
            Executive Summary
          </h4>
          <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-base">{report.summary}</p>
        </div>

        {/* Findings */}
        <div>
          <h4 className="text-sm font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2 pl-1">
            <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
            Detailed Analysis
          </h4>
          <div className="glass-panel p-6 bg-white/40 dark:bg-slate-900/40">
            <div className="prose prose-sm prose-slate dark:prose-invert max-w-none prose-headings:font-bold prose-p:leading-relaxed prose-li:marker:text-blue-500">
              <ReactMarkdown>{report.findings}</ReactMarkdown>
            </div>
          </div>
        </div>

        {/* Tool Calls */}
        {report.tool_calls && report.tool_calls.length > 0 && (
          <div>
            <h4 className="text-sm font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2 pl-1">
              <Code className="w-4 h-4 text-purple-500" />
              Tool Executions ({report.tool_calls.length})
            </h4>
            <div className="space-y-3">
              {report.tool_calls.map((call, i) => (
                <div key={i} className="group p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50 hover:border-purple-200 dark:hover:border-purple-800 transition-all">
                  <div className="flex items-start justify-between mb-3">
                    <span className="inline-flex items-center gap-2 text-xs font-bold text-purple-700 dark:text-purple-300 bg-purple-100 dark:bg-purple-900/30 px-2.5 py-1 rounded-md border border-purple-200 dark:border-purple-800">
                      {call.tool_name}
                    </span>
                    <span className="text-xs text-slate-500 dark:text-slate-400 font-mono flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatDateTime(call.timestamp)}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div>
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Arguments</p>
                      <pre className="text-[11px] text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-900 p-3 rounded-lg border border-slate-200 dark:border-slate-700 overflow-x-auto font-mono custom-scrollbar">
                        {JSON.stringify(call.arguments, null, 2)}
                      </pre>
                    </div>
                    <div>
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Result</p>
                      <pre className="text-[11px] text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-900 p-3 rounded-lg border border-slate-200 dark:border-slate-700 overflow-x-auto max-h-32 font-mono custom-scrollbar">
                        {JSON.stringify(call.result, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Metadata */}
        <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 pt-4 border-t border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2">
            <Clock className="w-3.5 h-3.5" />
            Created {formatDateTime(report.created_at)}
          </div>
          <div className="flex items-center gap-2">
            <span className="font-medium text-slate-700 dark:text-slate-300">Model:</span>
            <span className="bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded border border-slate-200 dark:border-slate-700">
              {report.created_by}
            </span>
          </div>
        </div>
      </div>
    </ExpandableCard>
  )
}
