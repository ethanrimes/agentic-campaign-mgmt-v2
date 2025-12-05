// frontend/app/verifier/page.tsx

'use client'

import { useState, useEffect, useMemo, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { getVerifierResponses, getCompletedPost } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'
import { formatDateTime, formatRelativeTime, cn } from '@/lib/utils'
import {
  ShieldCheck, ShieldX, ShieldAlert, Calendar, Hash,
  Clock, ChevronRight, Search, SlidersHorizontal, Layers,
  CheckCircle2, XCircle, MinusCircle, AlertTriangle, Check, X,
  ExternalLink, Sparkles, RefreshCw, Facebook, Instagram
} from 'lucide-react'
import type { VerifierResponse, CompletedPost } from '@/types'
import Link from 'next/link'

type DateRange = 'all' | '1d' | '7d' | '30d'
type StatusFilter = 'all' | 'approved' | 'rejected' | 'manually_overridden'

interface Filters {
  dateRange: DateRange
  status: StatusFilter
  search: string
}

function VerifierPageContent() {
  const { selectedAsset } = useBusinessAsset()
  const searchParams = useSearchParams()
  const highlightPostId = searchParams.get('post')

  const [reports, setReports] = useState<VerifierResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [filterOpen, setFilterOpen] = useState(false)
  const [expandedRow, setExpandedRow] = useState<string | null>(null)
  const [postCache, setPostCache] = useState<Record<string, CompletedPost>>({})
  const [filters, setFilters] = useState<Filters>({
    dateRange: 'all',
    status: 'all',
    search: ''
  })

  useEffect(() => {
    async function loadReports() {
      if (!selectedAsset) return

      try {
        setLoading(true)
        const data = await getVerifierResponses(selectedAsset.id)
        setReports(data)

        // Pre-fetch posts for all reports
        const uniquePostIds = [...new Set(data.map(r => r.completed_post_id))]
        const postPromises = uniquePostIds.map(async (postId) => {
          try {
            const post = await getCompletedPost(postId, selectedAsset.id)
            return { postId, post }
          } catch {
            return { postId, post: null }
          }
        })
        const postResults = await Promise.all(postPromises)
        const cache: Record<string, CompletedPost> = {}
        postResults.forEach(({ postId, post }) => {
          if (post) cache[postId] = post
        })
        setPostCache(cache)
      } catch (error) {
        console.error('Failed to load verifier reports:', error)
      } finally {
        setLoading(false)
      }
    }

    loadReports()
  }, [selectedAsset])

  // Auto-expand highlighted post
  useEffect(() => {
    if (highlightPostId) {
      const report = reports.find(r => r.completed_post_id === highlightPostId)
      if (report) {
        setExpandedRow(report.id)
      }
    }
  }, [highlightPostId, reports])

  const filteredReports = useMemo(() => {
    return reports.filter(report => {
      // Status filter
      if (filters.status === 'approved' && (!report.is_approved || report.is_manually_overridden)) return false
      if (filters.status === 'rejected' && (report.is_approved || report.is_manually_overridden)) return false
      if (filters.status === 'manually_overridden' && !report.is_manually_overridden) return false

      // Search filter
      if (filters.search) {
        const post = postCache[report.completed_post_id]
        const searchLower = filters.search.toLowerCase()
        const matchesReasoning = report.reasoning.toLowerCase().includes(searchLower)
        const matchesPostText = post?.text?.toLowerCase().includes(searchLower) || false
        const matchesPostId = report.completed_post_id.toLowerCase().includes(searchLower)
        if (!matchesReasoning && !matchesPostText && !matchesPostId) return false
      }

      // Date range filter
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
  }, [reports, filters, postCache])

  // Sort to put highlighted post first
  const sortedReports = useMemo(() => {
    return [...filteredReports].sort((a, b) => {
      if (highlightPostId) {
        if (a.completed_post_id === highlightPostId) return -1
        if (b.completed_post_id === highlightPostId) return 1
      }
      return 0
    })
  }, [filteredReports, highlightPostId])

  const stats = useMemo(() => {
    const total = filteredReports.length
    const approved = filteredReports.filter(r => r.is_approved && !r.is_manually_overridden).length
    const rejected = filteredReports.filter(r => !r.is_approved && !r.is_manually_overridden).length
    const overridden = filteredReports.filter(r => r.is_manually_overridden).length
    return { total, approved, rejected, overridden }
  }, [filteredReports])

  const activeFiltersCount = Object.entries(filters).filter(([key, value]) =>
    (key !== 'search' && value !== 'all') || (key === 'search' && value !== '')
  ).length

  const getStatusBadge = (report: VerifierResponse) => {
    if (report.is_manually_overridden) {
      return (
        <div className="w-7 h-7 rounded-lg bg-orange-500/10 border border-orange-500/20 flex items-center justify-center" title="Manually Overridden">
          <RefreshCw className="w-4 h-4 text-orange-500" />
        </div>
      )
    }
    if (report.is_approved) {
      return (
        <div className="w-7 h-7 rounded-lg bg-green-500/10 border border-green-500/20 flex items-center justify-center" title="Approved">
          <ShieldCheck className="w-4 h-4 text-green-500" />
        </div>
      )
    }
    return (
      <div className="w-7 h-7 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center" title="Rejected">
        <ShieldX className="w-4 h-4 text-red-500" />
      </div>
    )
  }

  if (!selectedAsset || loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <ShieldCheck className="w-16 h-16 text-cyan-400 mx-auto mb-4 animate-pulse" />
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
              <SlidersHorizontal className="w-5 h-5 text-cyan-500" />
              {filterOpen && <span className="font-semibold text-sm">Filters</span>}
            </div>
            {filterOpen && (
              <button
                onClick={() => setFilters({ dateRange: 'all', status: 'all', search: '' })}
                className="text-xs text-slate-400 hover:text-cyan-500 transition-colors"
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
                    placeholder="Search reports or post ID..."
                    value={filters.search}
                    onChange={(e) => setFilters(f => ({ ...f, search: e.target.value }))}
                    className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg pl-9 pr-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/20"
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
                          ? 'bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                      )}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Status Filter */}
              <div>
                <label className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                  <ShieldCheck className="w-3.5 h-3.5" /> Status
                </label>
                <div className="space-y-1.5">
                  {[
                    ['all', 'All Reports', null, Layers],
                    ['approved', 'Approved', 'text-green-500', ShieldCheck],
                    ['rejected', 'Rejected', 'text-red-500', ShieldX],
                    ['manually_overridden', 'Overridden', 'text-orange-500', RefreshCw],
                  ].map(([value, label, color, Icon]) => (
                    <button
                      key={value as string}
                      onClick={() => setFilters(f => ({ ...f, status: value as StatusFilter }))}
                      className={cn(
                        "w-full px-3 py-2 rounded-md text-xs font-medium transition-all flex items-center gap-2",
                        filters.status === value
                          ? 'bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                      )}
                    >
                      {Icon && <Icon className={cn("w-3.5 h-3.5", color as string)} />}
                      {label as string}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Active Filters Count */}
          {!filterOpen && activeFiltersCount > 0 && (
            <div className="p-3 border-t border-slate-200 dark:border-slate-800">
              <div className="w-6 h-6 bg-cyan-500 rounded-full flex items-center justify-center text-xs font-bold text-white mx-auto">
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
            <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Verifier Reports</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400">Content safety verification results</p>
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
                <ShieldCheck className="w-4 h-4 text-green-500" />
                <span className="text-sm font-semibold text-green-600 dark:text-green-400">{stats.approved}</span>
              </div>
              <div className="flex items-center gap-2">
                <ShieldX className="w-4 h-4 text-red-500" />
                <span className="text-sm font-semibold text-red-600 dark:text-red-400">{stats.rejected}</span>
              </div>
              {stats.overridden > 0 && (
                <div className="flex items-center gap-2">
                  <RefreshCw className="w-4 h-4 text-orange-500" />
                  <span className="text-sm font-semibold text-orange-600 dark:text-orange-400">{stats.overridden}</span>
                </div>
              )}
              {stats.total > 0 && (
                <>
                  <div className="w-px h-8 bg-slate-200 dark:bg-slate-700" />
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                      {((stats.approved / stats.total) * 100).toFixed(0)}%
                    </span>
                    <span className="text-xs text-slate-500 dark:text-slate-400">approval</span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Reports Table */}
        <div className="bg-white dark:bg-slate-900/50 backdrop-blur border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm">
          {/* Table Header */}
          <div className="grid grid-cols-12 gap-4 px-4 py-3 bg-slate-50 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            <div className="col-span-1">Status</div>
            <div className="col-span-2">Post ID</div>
            <div className="col-span-2">Time</div>
            <div className="col-span-4">Summary</div>
            <div className="col-span-2 text-center">Checks</div>
            <div className="col-span-1"></div>
          </div>

          {/* Table Body */}
          <div className="divide-y divide-slate-100 dark:divide-slate-800/50">
            {sortedReports.map((report) => {
              const post = postCache[report.completed_post_id]
              const isHighlighted = report.completed_post_id === highlightPostId

              return (
                <div key={report.id}>
                  {/* Row */}
                  <div
                    className={cn(
                      "grid grid-cols-12 gap-4 px-4 py-3 items-center cursor-pointer transition-all hover:bg-slate-50 dark:hover:bg-slate-800/30",
                      expandedRow === report.id && 'bg-slate-50 dark:bg-slate-800/50',
                      isHighlighted && 'ring-2 ring-cyan-500 ring-inset'
                    )}
                    onClick={() => setExpandedRow(expandedRow === report.id ? null : report.id)}
                  >
                    {/* Status */}
                    <div className="col-span-1">
                      {getStatusBadge(report)}
                    </div>

                    {/* Post ID - Prominent */}
                    <div className="col-span-2">
                      <div className="flex items-center gap-2">
                        <span className="inline-flex items-center gap-1 text-xs font-mono bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2 py-1.5 rounded border border-slate-200 dark:border-slate-700">
                          <Hash className="w-3 h-3 text-slate-400" />
                          {report.completed_post_id.slice(0, 8)}
                        </span>
                        {post && (
                          <span className={cn(
                            "flex items-center justify-center w-6 h-6 rounded",
                            post.platform === 'facebook'
                              ? "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400"
                              : "bg-pink-100 text-pink-600 dark:bg-pink-900/30 dark:text-pink-400"
                          )}>
                            {post.platform === 'facebook' ? (
                              <Facebook className="w-3.5 h-3.5" />
                            ) : (
                              <Instagram className="w-3.5 h-3.5" />
                            )}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Time */}
                    <div className="col-span-2">
                      <div className="text-sm font-medium">{formatRelativeTime(report.created_at)}</div>
                      <div className="text-xs text-slate-400">{formatDateTime(report.created_at)}</div>
                    </div>

                    {/* Summary */}
                    <div className="col-span-4">
                      <p className="text-sm text-slate-700 dark:text-slate-300 line-clamp-1">{report.reasoning}</p>
                    </div>

                    {/* Checks */}
                    <div className="col-span-2 flex items-center justify-center gap-2">
                      <span className={cn(
                        "inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded border",
                        report.has_no_offensive_content
                          ? "text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800"
                          : "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800"
                      )}>
                        {report.has_no_offensive_content ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}
                        Safe
                      </span>
                      {report.has_no_misinformation !== null && (
                        <span className={cn(
                          "inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded border",
                          report.has_no_misinformation
                            ? "text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800"
                            : "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800"
                        )}>
                          {report.has_no_misinformation ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}
                          Fact
                        </span>
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
                      <div className="grid grid-cols-2 gap-4 pt-4">
                        {/* Left Column */}
                        <div className="space-y-4">
                          {/* Overall Result */}
                          <div className={cn(
                            "p-4 rounded-lg border",
                            report.is_manually_overridden
                              ? "bg-orange-50/50 dark:bg-orange-900/10 border-orange-200 dark:border-orange-800"
                              : report.is_approved
                                ? "bg-green-50/50 dark:bg-green-900/10 border-green-200 dark:border-green-800"
                                : "bg-red-50/50 dark:bg-red-900/10 border-red-200 dark:border-red-800"
                          )}>
                            <div className="flex items-center gap-3">
                              <div className={cn(
                                "p-2 rounded-full",
                                report.is_manually_overridden
                                  ? "bg-orange-100 dark:bg-orange-900/30 text-orange-600"
                                  : report.is_approved
                                    ? "bg-green-100 dark:bg-green-900/30 text-green-600"
                                    : "bg-red-100 dark:bg-red-900/30 text-red-600"
                              )}>
                                {report.is_manually_overridden ? (
                                  <RefreshCw className="w-6 h-6" />
                                ) : report.is_approved ? (
                                  <ShieldCheck className="w-6 h-6" />
                                ) : (
                                  <ShieldX className="w-6 h-6" />
                                )}
                              </div>
                              <div>
                                <h4 className={cn(
                                  "text-base font-bold",
                                  report.is_manually_overridden
                                    ? "text-orange-900 dark:text-orange-100"
                                    : report.is_approved
                                      ? "text-green-900 dark:text-green-100"
                                      : "text-red-900 dark:text-red-100"
                                )}>
                                  {report.is_manually_overridden
                                    ? 'Manually Overridden'
                                    : report.is_approved
                                      ? 'Post Approved'
                                      : 'Post Rejected'}
                                </h4>
                                <p className={cn(
                                  "text-xs mt-0.5",
                                  report.is_manually_overridden
                                    ? "text-orange-700 dark:text-orange-300"
                                    : report.is_approved
                                      ? "text-green-700 dark:text-green-300"
                                      : "text-red-700 dark:text-red-300"
                                )}>
                                  {report.is_manually_overridden
                                    ? 'Initially rejected but manually approved for publishing.'
                                    : report.is_approved
                                      ? 'All safety and fact-check protocols passed.'
                                      : 'Violations detected during verification.'}
                                </p>
                              </div>
                            </div>
                          </div>

                          {/* Safety Checks */}
                          <div className="bg-white dark:bg-slate-800/50 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
                            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Safety Checks</h4>
                            <div className="grid grid-cols-2 gap-2">
                              <div className={cn(
                                "flex items-center gap-2 p-2 rounded border",
                                report.has_no_offensive_content
                                  ? "bg-green-50 dark:bg-green-900/10 border-green-200 dark:border-green-800 text-green-700 dark:text-green-300"
                                  : "bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-800 text-red-700 dark:text-red-300"
                              )}>
                                {report.has_no_offensive_content ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                                <span className="text-xs font-medium">No Offensive Content</span>
                              </div>
                              <div className={cn(
                                "flex items-center gap-2 p-2 rounded border",
                                report.has_no_misinformation === null
                                  ? "bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-400"
                                  : report.has_no_misinformation
                                    ? "bg-green-50 dark:bg-green-900/10 border-green-200 dark:border-green-800 text-green-700 dark:text-green-300"
                                    : "bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-800 text-red-700 dark:text-red-300"
                              )}>
                                {report.has_no_misinformation === null ? (
                                  <MinusCircle className="w-4 h-4" />
                                ) : report.has_no_misinformation ? (
                                  <CheckCircle2 className="w-4 h-4" />
                                ) : (
                                  <XCircle className="w-4 h-4" />
                                )}
                                <span className="text-xs font-medium">No Misinformation</span>
                              </div>
                            </div>
                          </div>

                          {/* Reasoning */}
                          <div className="bg-white dark:bg-slate-800/50 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
                            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Analysis</h4>
                            <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">{report.reasoning}</p>
                          </div>

                          {/* Issues Found */}
                          {report.issues_found && report.issues_found.length > 0 && (
                            <div className="bg-amber-50/50 dark:bg-amber-900/10 rounded-lg p-4 border border-amber-200 dark:border-amber-800/50">
                              <h4 className="text-xs font-bold text-amber-700 dark:text-amber-300 uppercase tracking-wider mb-2 flex items-center gap-2">
                                <AlertTriangle className="w-3.5 h-3.5" />
                                Issues Found ({report.issues_found.length})
                              </h4>
                              <ul className="space-y-1">
                                {report.issues_found.map((issue, i) => (
                                  <li key={i} className="flex items-start gap-2 text-sm text-amber-800 dark:text-amber-200/80">
                                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-2 flex-shrink-0" />
                                    {issue}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>

                        {/* Right Column - Post Preview */}
                        <div>
                          {post && (
                            <div className="bg-white dark:bg-slate-800/50 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
                              <div className="flex items-center justify-between mb-3">
                                <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
                                  <Sparkles className="w-3 h-3" /> Target Content
                                </h4>
                                <Link
                                  href={`/${post.platform}?post=${post.id}`}
                                  className="text-xs font-medium text-cyan-600 dark:text-cyan-400 hover:underline flex items-center gap-1"
                                >
                                  View <ExternalLink className="w-3 h-3" />
                                </Link>
                              </div>

                              <div className="space-y-3">
                                {/* Post ID - Prominent */}
                                <div className="bg-slate-50 dark:bg-slate-900/50 rounded-lg p-3 border border-slate-200 dark:border-slate-700">
                                  <div className="flex items-center justify-between">
                                    <span className="text-xs text-slate-500 uppercase tracking-wider">Post ID</span>
                                    <span className="font-mono text-sm text-slate-700 dark:text-slate-300">{post.id}</span>
                                  </div>
                                </div>

                                {/* Platform & Type */}
                                <div className="flex items-center gap-2">
                                  <span className={cn(
                                    "text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wide",
                                    post.platform === 'facebook'
                                      ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300"
                                      : "bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-300"
                                  )}>
                                    {post.platform}
                                  </span>
                                  <span className="text-[10px] bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300 px-2 py-0.5 rounded-full font-bold uppercase tracking-wide">
                                    {post.post_type.replace(/_/g, ' ')}
                                  </span>
                                  <span className={cn(
                                    "text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wide",
                                    post.verification_status === 'verified'
                                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300"
                                      : post.verification_status === 'manually_overridden'
                                        ? "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300"
                                        : post.verification_status === 'rejected'
                                          ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300"
                                          : "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                                  )}>
                                    {post.verification_status.replace(/_/g, ' ')}
                                  </span>
                                </div>

                                {/* Post Text */}
                                <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-4 italic border-l-2 border-slate-300 dark:border-slate-600 pl-3">
                                  "{post.text}"
                                </p>

                                {/* Media Preview */}
                                {post.media_urls && post.media_urls.length > 0 && (
                                  <div className="flex gap-2">
                                    {post.media_urls.slice(0, 3).map((url, i) => (
                                      <div key={i} className="w-16 h-16 rounded-lg bg-slate-200 dark:bg-slate-700 overflow-hidden">
                                        <img src={url} alt="" className="w-full h-full object-cover" />
                                      </div>
                                    ))}
                                    {post.media_urls.length > 3 && (
                                      <div className="w-16 h-16 rounded-lg bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-xs font-bold text-slate-500">
                                        +{post.media_urls.length - 3}
                                      </div>
                                    )}
                                  </div>
                                )}
                              </div>
                            </div>
                          )}

                          {/* Metadata */}
                          <div className="mt-4 flex items-center justify-between text-xs text-slate-500 px-1">
                            <span>Model: <span className="text-slate-700 dark:text-slate-400 font-mono">{report.model}</span></span>
                            <span>ID: <span className="text-slate-700 dark:text-slate-400 font-mono">{report.id.slice(0, 8)}</span></span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {/* Empty State */}
          {sortedReports.length === 0 && (
            <div className="py-16 text-center">
              <ShieldAlert className="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
              <p className="text-slate-600 dark:text-slate-400 font-medium">
                {filters.status === 'all' ? 'No verifier reports found' : `No ${filters.status} reports found`}
              </p>
              <button
                onClick={() => setFilters({ dateRange: 'all', status: 'all', search: '' })}
                className="mt-2 text-sm text-cyan-500 hover:text-cyan-400"
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

export default function VerifierPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <ShieldCheck className="w-16 h-16 text-cyan-400 mx-auto mb-4 animate-pulse" />
          <p className="text-lg text-slate-600 dark:text-slate-400">Loading...</p>
        </div>
      </div>
    }>
      <VerifierPageContent />
    </Suspense>
  )
}
