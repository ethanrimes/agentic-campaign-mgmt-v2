// frontend/app/verifier/page.tsx

'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { getVerifierResponses } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'
import VerifierReportCard from '@/components/verifier/VerifierReportCard'
import { ShieldCheck, ShieldX, ShieldAlert, Filter } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { VerifierResponse } from '@/types'

type FilterType = 'all' | 'approved' | 'rejected'

function VerifierPageContent() {
  const { selectedAsset } = useBusinessAsset()
  const searchParams = useSearchParams()
  const highlightPostId = searchParams.get('post')

  const [reports, setReports] = useState<VerifierResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<FilterType>('all')

  useEffect(() => {
    async function loadReports() {
      if (!selectedAsset) return

      try {
        setLoading(true)
        const data = await getVerifierResponses(selectedAsset.id)
        setReports(data)
      } catch (error) {
        console.error('Failed to load verifier reports:', error)
      } finally {
        setLoading(false)
      }
    }

    loadReports()
  }, [selectedAsset])

  // Calculate stats
  const stats = {
    total: reports.length,
    approved: reports.filter(r => r.is_approved).length,
    rejected: reports.filter(r => !r.is_approved).length,
  }

  // Filter reports
  const filteredReports = reports.filter(r => {
    if (filter === 'approved') return r.is_approved
    if (filter === 'rejected') return !r.is_approved
    return true
  })

  // Sort reports to put highlighted one first
  const sortedReports = [...filteredReports].sort((a, b) => {
    if (highlightPostId) {
      if (a.completed_post_id === highlightPostId) return -1
      if (b.completed_post_id === highlightPostId) return 1
    }
    return 0
  })

  if (!selectedAsset || loading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="text-center py-16">
          <ShieldCheck className="w-16 h-16 text-cyan-400 mx-auto mb-4 animate-pulse" />
          <p className="text-lg text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="relative mb-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-100/30 via-blue-100/20 to-slate-100/30 rounded-3xl blur-3xl"></div>
        <div className="relative bg-white rounded-2xl p-8 border border-slate-200 shadow-xl">
          <div className="flex items-center gap-4 mb-3">
            <div className="relative">
              <div className="w-14 h-14 bg-gradient-to-br from-cyan-600 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
                <ShieldCheck className="w-7 h-7 text-primary-600 dark:text-white" />
              </div>
              <div className="absolute inset-0 bg-cyan-500 rounded-2xl blur-xl opacity-30"></div>
            </div>
            <div>
              <h1 className="text-4xl font-bold text-slate-900">
                Verifier Reports
              </h1>
              <p className="text-slate-600 mt-1">
                Content safety verification results from the AI verifier agent
              </p>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-6 flex items-center gap-3">
            <div className="bg-slate-100 px-4 py-2 rounded-full border border-slate-200">
              <span className="text-sm font-bold text-slate-900">{stats.total}</span>
              <span className="text-sm text-slate-600 ml-1">total</span>
            </div>
            <div className="bg-green-50 px-4 py-2 rounded-full border border-green-200">
              <span className="text-sm font-bold text-green-700">{stats.approved}</span>
              <span className="text-sm text-green-600 ml-1">approved</span>
            </div>
            <div className="bg-red-50 px-4 py-2 rounded-full border border-red-200">
              <span className="text-sm font-bold text-red-700">{stats.rejected}</span>
              <span className="text-sm text-red-600 ml-1">rejected</span>
            </div>
            {stats.total > 0 && (
              <div className="bg-blue-50 px-4 py-2 rounded-full border border-blue-200">
                <span className="text-sm font-bold text-blue-700">
                  {((stats.approved / stats.total) * 100).toFixed(0)}%
                </span>
                <span className="text-sm text-blue-600 ml-1">approval rate</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 mb-6">
        <Filter className="w-4 h-4 text-gray-500" />
        <button
          onClick={() => setFilter('all')}
          className={cn(
            "px-4 py-2 rounded-full text-sm font-medium transition-all",
            filter === 'all'
              ? "bg-slate-900 text-white shadow-lg"
              : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
          )}
        >
          All ({stats.total})
        </button>
        <button
          onClick={() => setFilter('approved')}
          className={cn(
            "px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-1.5",
            filter === 'approved'
              ? "bg-green-600 text-white shadow-lg"
              : "bg-white text-green-600 border border-green-200 hover:bg-green-50"
          )}
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          Approved ({stats.approved})
        </button>
        <button
          onClick={() => setFilter('rejected')}
          className={cn(
            "px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-1.5",
            filter === 'rejected'
              ? "bg-red-600 text-white shadow-lg"
              : "bg-white text-red-600 border border-red-200 hover:bg-red-50"
          )}
        >
          <ShieldX className="w-3.5 h-3.5" />
          Rejected ({stats.rejected})
        </button>
      </div>

      {/* Reports List */}
      {sortedReports.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-slate-200 shadow-xl">
          <div className="relative inline-block mb-6">
            <ShieldAlert className="w-16 h-16 text-slate-400 mx-auto" />
            <div className="absolute inset-0 bg-slate-500 blur-2xl opacity-20"></div>
          </div>
          <p className="text-lg font-semibold text-slate-900 mb-2">
            {filter === 'all' ? 'No verifier reports found' : `No ${filter} reports found`}
          </p>
          <p className="text-sm text-slate-600 max-w-md mx-auto">
            {filter === 'all'
              ? 'Run the content creation agent to generate and verify posts'
              : 'Try changing the filter to see other reports'
            }
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {sortedReports.map((report, index) => (
            <div
              key={report.id}
              className="animate-slide-up"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <VerifierReportCard
                report={report}
                defaultExpanded={report.completed_post_id === highlightPostId}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function VerifierPage() {
  return (
    <Suspense fallback={
      <div className="max-w-6xl mx-auto">
        <div className="text-center py-16">
          <ShieldCheck className="w-16 h-16 text-cyan-400 mx-auto mb-4 animate-pulse" />
          <p className="text-lg text-gray-600">Loading...</p>
        </div>
      </div>
    }>
      <VerifierPageContent />
    </Suspense>
  )
}
