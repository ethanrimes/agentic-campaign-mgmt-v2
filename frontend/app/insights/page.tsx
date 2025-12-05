// frontend/app/insights/page.tsx

'use client'

import { useState, useEffect, useMemo } from 'react'
import { getInsightReports } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'
import { formatDateTime, formatRelativeTime, cn } from '@/lib/utils'
import {
  BarChart3, Filter, Calendar, Hash, CheckCircle2,
  Clock, ChevronRight, Brain, Lightbulb, Code, Activity,
  Search, SlidersHorizontal, Layers, FileText
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import type { InsightReport, ToolCall } from '@/types'

type DateRange = 'all' | '1d' | '7d' | '30d'

interface Filters {
  dateRange: DateRange
  hasRecommendations: 'all' | 'yes' | 'no'
  search: string
}

export default function InsightsPage() {
  const { selectedAsset } = useBusinessAsset()
  const [reports, setReports] = useState<InsightReport[]>([])
  const [loading, setLoading] = useState(true)
  const [filterOpen, setFilterOpen] = useState(false)
  const [expandedRow, setExpandedRow] = useState<string | null>(null)
  const [filters, setFilters] = useState<Filters>({
    dateRange: 'all',
    hasRecommendations: 'all',
    search: ''
  })

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

  const filteredReports = useMemo(() => {
    return reports.filter(report => {
      // Filter by recommendations
      if (filters.hasRecommendations === 'yes' && (!report.recommendations || report.recommendations.length === 0)) return false
      if (filters.hasRecommendations === 'no' && report.recommendations && report.recommendations.length > 0) return false

      // Filter by search
      if (filters.search && !report.summary.toLowerCase().includes(filters.search.toLowerCase()) &&
          !report.findings.toLowerCase().includes(filters.search.toLowerCase())) return false

      // Filter by date range
      if (filters.dateRange !== 'all') {
        const date = new Date(report.created_at)
        const now = new Date()
        const diffDays = Math.floor((now.getTime() - date.getTime()) / 86400000)
        if (filters.dateRange === '1d' && diffDays > 1) return false
        if (filters.dateRange === '7d' && diffDays > 7) return false
        if (filters.dateRange === '30d' && diffDays > 30) return false
      }
      return true
    })
  }, [reports, filters])

  const stats = useMemo(() => ({
    total: filteredReports.length,
    withRecommendations: filteredReports.filter(r => r.recommendations && r.recommendations.length > 0).length,
    totalTools: filteredReports.reduce((acc, r) => acc + (r.tool_calls?.length || 0), 0),
    totalRecommendations: filteredReports.reduce((acc, r) => acc + (r.recommendations?.length || 0), 0)
  }), [filteredReports])

  const activeFiltersCount = Object.entries(filters).filter(([key, value]) =>
    (key !== 'search' && value !== 'all') || (key === 'search' && value !== '')
  ).length

  if (!selectedAsset || loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <BarChart3 className="w-16 h-16 text-green-400 mx-auto mb-4 animate-pulse" />
          <p className="text-lg text-slate-600 dark:text-slate-400">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex">
      {/* Filter Sidebar */}
      <div
        className={cn(
          "fixed left-0 top-16 h-[calc(100%-4rem)] z-40 transition-all duration-300 ease-out",
          filterOpen ? 'w-72' : 'w-12'
        )}
        onMouseEnter={() => setFilterOpen(true)}
        onMouseLeave={() => setFilterOpen(false)}
      >
        <div className="h-full bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl border-r border-slate-200 dark:border-slate-800 flex flex-col shadow-lg">
          {/* Filter Toggle Tab */}
          <div className={cn(
            "p-3 border-b border-slate-200 dark:border-slate-800 flex items-center",
            filterOpen ? 'justify-between' : 'justify-center'
          )}>
            <div className="flex items-center gap-2">
              <SlidersHorizontal className="w-5 h-5 text-green-500" />
              {filterOpen && <span className="font-semibold text-sm">Filters</span>}
            </div>
            {filterOpen && (
              <button
                onClick={() => setFilters({ dateRange: 'all', hasRecommendations: 'all', search: '' })}
                className="text-xs text-slate-400 hover:text-green-500 transition-colors"
              >
                Reset
              </button>
            )}
          </div>

          {/* Filter Content */}
          <div className={cn(
            "flex-1 overflow-y-auto transition-opacity duration-200",
            filterOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
          )}>
            <div className="p-4 space-y-5">
              {/* Search */}
              <div>
                <label className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2 block">Search</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search reports..."
                    value={filters.search}
                    onChange={(e) => setFilters(f => ({ ...f, search: e.target.value }))}
                    className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg pl-9 pr-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500/20"
                  />
                </div>
              </div>

              {/* Date Range */}
              <div>
                <label className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                  <Calendar className="w-3.5 h-3.5" /> Date Range
                </label>
                <div className="grid grid-cols-2 gap-1.5">
                  {[['all', 'All'], ['1d', '24h'], ['7d', '7d'], ['30d', '30d']].map(([value, label]) => (
                    <button
                      key={value}
                      onClick={() => setFilters(f => ({ ...f, dateRange: value as DateRange }))}
                      className={cn(
                        "px-3 py-1.5 rounded-md text-xs font-medium transition-all",
                        filters.dateRange === value
                          ? 'bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/30'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                      )}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Recommendations Filter */}
              <div>
                <label className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                  <Lightbulb className="w-3.5 h-3.5" /> Recommendations
                </label>
                <div className="space-y-1.5">
                  {[['all', 'All Reports'], ['yes', 'With Recommendations'], ['no', 'Without Recommendations']].map(([value, label]) => (
                    <button
                      key={value}
                      onClick={() => setFilters(f => ({ ...f, hasRecommendations: value as 'all' | 'yes' | 'no' }))}
                      className={cn(
                        "w-full px-3 py-2 rounded-md text-xs font-medium transition-all text-left",
                        filters.hasRecommendations === value
                          ? 'bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/30'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                      )}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Active Filters Count */}
          {!filterOpen && activeFiltersCount > 0 && (
            <div className="p-3 border-t border-slate-200 dark:border-slate-800">
              <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center text-xs font-bold text-white mx-auto">
                {activeFiltersCount}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 ml-12 p-6 pt-20">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg shadow-green-500/20">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Insight Reports</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400">Performance analysis & recommendations</p>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-6 bg-white dark:bg-slate-900/50 backdrop-blur border border-slate-200 dark:border-slate-800 rounded-xl px-5 py-2.5 shadow-sm">
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold">{stats.total}</span>
                <span className="text-xs text-slate-500 dark:text-slate-400">Reports</span>
              </div>
              <div className="w-px h-8 bg-slate-200 dark:bg-slate-700" />
              <div className="flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-amber-500" />
                <span className="text-sm font-semibold text-amber-600 dark:text-amber-400">{stats.totalRecommendations}</span>
                <span className="text-xs text-slate-500 dark:text-slate-400">tips</span>
              </div>
              <div className="flex items-center gap-2">
                <Code className="w-4 h-4 text-purple-500" />
                <span className="text-sm font-semibold text-purple-600 dark:text-purple-400">{stats.totalTools}</span>
                <span className="text-xs text-slate-500 dark:text-slate-400">calls</span>
              </div>
            </div>
          </div>
        </div>

        {/* Reports Table */}
        <div className="bg-white dark:bg-slate-900/50 backdrop-blur border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm">
          {/* Table Header */}
          <div className="grid grid-cols-12 gap-4 px-4 py-3 bg-slate-50 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            <div className="col-span-2">Time</div>
            <div className="col-span-5">Summary</div>
            <div className="col-span-1 text-center">Posts</div>
            <div className="col-span-1 text-center">Tools</div>
            <div className="col-span-2 text-center">Recommendations</div>
            <div className="col-span-1"></div>
          </div>

          {/* Table Body */}
          <div className="divide-y divide-slate-100 dark:divide-slate-800/50">
            {filteredReports.map((report) => (
              <div key={report.id}>
                {/* Row */}
                <div
                  className={cn(
                    "grid grid-cols-12 gap-4 px-4 py-3 items-center cursor-pointer transition-all hover:bg-slate-50 dark:hover:bg-slate-800/30",
                    expandedRow === report.id && 'bg-slate-50 dark:bg-slate-800/50'
                  )}
                  onClick={() => setExpandedRow(expandedRow === report.id ? null : report.id)}
                >
                  {/* Time */}
                  <div className="col-span-2">
                    <div className="text-sm font-medium">{formatRelativeTime(report.created_at)}</div>
                    <div className="text-xs text-slate-400">{formatDateTime(report.created_at)}</div>
                  </div>

                  {/* Summary */}
                  <div className="col-span-5">
                    <p className="text-sm text-slate-700 dark:text-slate-300 line-clamp-1">{report.summary}</p>
                  </div>

                  {/* Reviewed Post IDs */}
                  <div className="col-span-1 text-center">
                    {report.reviewed_post_ids && report.reviewed_post_ids.length > 0 ? (
                      <span className="inline-flex items-center gap-1 text-xs font-mono bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 px-2 py-1 rounded border border-blue-200 dark:border-blue-800">
                        <FileText className="w-3 h-3" />
                        {report.reviewed_post_ids.length}
                      </span>
                    ) : (
                      <span className="text-slate-400">—</span>
                    )}
                  </div>

                  {/* Tool Calls */}
                  <div className="col-span-1 text-center">
                    <span className="inline-flex items-center gap-1 text-xs font-medium bg-purple-50 dark:bg-purple-500/10 text-purple-600 dark:text-purple-400 px-2 py-1 rounded-full border border-purple-200 dark:border-purple-500/20">
                      <Code className="w-3 h-3" />
                      {report.tool_calls?.length || 0}
                    </span>
                  </div>

                  {/* Recommendations */}
                  <div className="col-span-2 text-center">
                    {report.recommendations && report.recommendations.length > 0 ? (
                      <span className="inline-flex items-center gap-1 text-xs font-medium bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400 px-2 py-1 rounded-full border border-amber-200 dark:border-amber-500/20">
                        <Lightbulb className="w-3 h-3" />
                        {report.recommendations.length} tips
                      </span>
                    ) : (
                      <span className="text-slate-400">—</span>
                    )}
                  </div>

                  {/* Expand */}
                  <div className="col-span-1 flex justify-end">
                    <ChevronRight className={cn(
                      "w-4 h-4 text-slate-400 transition-transform",
                      expandedRow === report.id && 'rotate-90'
                    )} />
                  </div>
                </div>

                {/* Expanded Content */}
                {expandedRow === report.id && (
                  <div className="px-4 pb-4 bg-slate-50/50 dark:bg-slate-900/30 border-t border-slate-100 dark:border-slate-800/50">
                    <div className="space-y-4 pt-4">
                      {/* Summary Card - Full Width */}
                      <div className="bg-white dark:bg-slate-800/50 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center gap-2 mb-2">
                          <Brain className="w-4 h-4 text-green-500" />
                          <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">Summary</span>
                        </div>
                        <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">{report.summary}</p>
                      </div>

                      {/* Findings - Full Width */}
                      <div className="bg-white dark:bg-slate-800/50 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center gap-2 mb-2">
                          <Activity className="w-4 h-4 text-blue-500" />
                          <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">Detailed Analysis</span>
                        </div>
                        <div className="prose prose-sm prose-slate dark:prose-invert max-w-none text-slate-600 dark:text-slate-300">
                          <ReactMarkdown>{report.findings}</ReactMarkdown>
                        </div>
                      </div>

                      {/* Recommendations - Full Width */}
                      {report.recommendations && report.recommendations.length > 0 && (
                        <div className="bg-amber-50/50 dark:bg-amber-500/5 rounded-lg p-4 border border-amber-200 dark:border-amber-500/20">
                          <div className="flex items-center gap-2 mb-3">
                            <Lightbulb className="w-4 h-4 text-amber-500" />
                            <span className="text-xs font-semibold text-amber-700 dark:text-amber-300 uppercase tracking-wider">Recommendations</span>
                          </div>
                          <ul className="space-y-2">
                            {report.recommendations.map((rec, i) => (
                              <li key={i} className="flex items-start gap-2 text-sm text-slate-700 dark:text-slate-300">
                                <CheckCircle2 className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                                {rec}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Tool Calls and Reviewed Posts - Side by Side */}
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        {report.tool_calls && report.tool_calls.length > 0 && (
                          <div className="bg-white dark:bg-slate-800/50 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
                            <div className="flex items-center gap-2 mb-3">
                              <Code className="w-4 h-4 text-purple-500" />
                              <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">Tool Executions</span>
                            </div>
                            <div className="space-y-2 max-h-80 overflow-y-auto">
                              {report.tool_calls.map((call: ToolCall, i: number) => (
                                <div key={i} className="flex items-center justify-between bg-slate-50 dark:bg-slate-900/50 rounded-md px-3 py-2 border border-slate-200 dark:border-slate-700/50">
                                  <div className="flex items-center gap-2">
                                    <span className="text-xs font-mono font-semibold text-purple-600 dark:text-purple-300">{call.tool_name}</span>
                                  </div>
                                  <div className="flex items-center gap-3">
                                    <code className="text-[10px] text-slate-500 font-mono max-w-[200px] truncate">{JSON.stringify(call.arguments)}</code>
                                    <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-green-100 dark:bg-green-500/20 text-green-600 dark:text-green-400">
                                      OK
                                    </span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Reviewed Posts */}
                        {report.reviewed_post_ids && report.reviewed_post_ids.length > 0 && (
                          <div className="bg-white dark:bg-slate-800/50 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
                            <div className="flex items-center gap-2 mb-3">
                              <FileText className="w-4 h-4 text-blue-500" />
                              <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">Reviewed Posts ({report.reviewed_post_ids.length})</span>
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {report.reviewed_post_ids.map((postId: string, i: number) => (
                                <span key={i} className="text-xs font-mono bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 px-2 py-1 rounded border border-blue-200 dark:border-blue-800">
                                  {postId.slice(0, 8)}...
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Metadata - Full Width */}
                      <div className="flex items-center justify-between text-xs text-slate-500 px-1">
                        <span>Model: <span className="text-slate-700 dark:text-slate-400 font-mono">{report.created_by}</span></span>
                        <span>ID: <span className="text-slate-700 dark:text-slate-400 font-mono">{report.id.slice(0, 8)}</span></span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Empty State */}
          {filteredReports.length === 0 && (
            <div className="py-16 text-center">
              <BarChart3 className="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
              <p className="text-slate-600 dark:text-slate-400 font-medium">No reports match your filters</p>
              <button
                onClick={() => setFilters({ dateRange: 'all', hasRecommendations: 'all', search: '' })}
                className="mt-2 text-sm text-green-500 hover:text-green-400"
              >
                Clear all filters
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
