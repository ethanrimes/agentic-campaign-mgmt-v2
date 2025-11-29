// frontend/components/verifier/VerifierReportCard.tsx

'use client'

import { useEffect, useState } from 'react'
import ExpandableCard from '@/components/common/ExpandableCard'
import { formatDateTime, formatRelativeTime, cn } from '@/lib/utils'
import { ShieldCheck, ShieldX, ShieldAlert, CheckCircle2, XCircle, MinusCircle, ExternalLink, Sparkles } from 'lucide-react'
import type { VerifierResponse, CompletedPost } from '@/types'
import Link from 'next/link'
import { getCompletedPost } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'

interface VerifierReportCardProps {
  report: VerifierResponse
  defaultExpanded?: boolean
}

export default function VerifierReportCard({ report, defaultExpanded = false }: VerifierReportCardProps) {
  const { selectedAsset } = useBusinessAsset()
  const [post, setPost] = useState<CompletedPost | null>(null)

  useEffect(() => {
    async function loadPost() {
      if (!selectedAsset) return
      try {
        const postData = await getCompletedPost(report.completed_post_id, selectedAsset.id)
        setPost(postData)
      } catch (error) {
        console.error('Failed to load post:', error)
      }
    }
    loadPost()
  }, [report.completed_post_id, selectedAsset])

  const ChecklistItem = ({ label, value }: { label: string; value: boolean | null }) => {
    if (value === null) {
      return (
        <div className="flex items-center gap-2 text-gray-400">
          <MinusCircle className="w-4 h-4" />
          <span className="text-sm">{label}: N/A</span>
        </div>
      )
    }
    return (
      <div className={cn(
        "flex items-center gap-2",
        value ? "text-green-600" : "text-red-600"
      )}>
        {value ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
        <span className="text-sm">{label}: {value ? 'Pass' : 'Fail'}</span>
      </div>
    )
  }

  const preview = (
    <div className="space-y-3">
      <p className="text-sm text-gray-700 leading-relaxed line-clamp-2">{report.reasoning}</p>
      <div className="flex flex-wrap items-center gap-2">
        <ChecklistItem label="Source Links" value={report.has_source_link_if_news} />
        <ChecklistItem label="No Offensive Content" value={report.has_no_offensive_content} />
        <ChecklistItem label="No Misinformation" value={report.has_no_misinformation} />
      </div>
    </div>
  )

  const statusBadge = report.is_approved ? (
    <span className="text-xs bg-gradient-to-r from-green-50 to-emerald-50 text-green-700 px-3 py-1.5 rounded-full flex items-center gap-1.5 font-medium border border-green-200">
      <ShieldCheck className="w-3.5 h-3.5" />
      Approved
    </span>
  ) : (
    <span className="text-xs bg-gradient-to-r from-red-50 to-rose-50 text-red-700 px-3 py-1.5 rounded-full flex items-center gap-1.5 font-medium border border-red-200">
      <ShieldX className="w-3.5 h-3.5" />
      Rejected
    </span>
  )

  return (
    <ExpandableCard
      title={`Verification Report`}
      subtitle={`Verified ${formatRelativeTime(report.created_at)} • ${report.model}`}
      preview={preview}
      badge={statusBadge}
      defaultExpanded={defaultExpanded}
    >
      <div className="space-y-6">
        {/* Overall Result */}
        <div className={cn(
          "p-4 rounded-xl border",
          report.is_approved
            ? "bg-gradient-to-br from-green-50 to-emerald-50 border-green-200"
            : "bg-gradient-to-br from-red-50 to-rose-50 border-red-200"
        )}>
          <div className="flex items-center gap-3">
            {report.is_approved ? (
              <ShieldCheck className="w-8 h-8 text-green-600" />
            ) : (
              <ShieldX className="w-8 h-8 text-red-600" />
            )}
            <div>
              <h4 className={cn(
                "text-lg font-bold",
                report.is_approved ? "text-green-900" : "text-red-900"
              )}>
                {report.is_approved ? 'Post Approved' : 'Post Rejected'}
              </h4>
              <p className={cn(
                "text-sm",
                report.is_approved ? "text-green-700" : "text-red-700"
              )}>
                {report.is_approved
                  ? 'This post passed all verification checks'
                  : 'This post failed one or more verification checks'
                }
              </p>
            </div>
          </div>
        </div>

        {/* Checklist Details */}
        <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-soft">
          <h4 className="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
            <div className="w-1 h-4 bg-gradient-to-b from-blue-500 to-purple-500 rounded-full"></div>
            Verification Checklist
          </h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">Source Links Included (News)</span>
              {report.has_source_link_if_news === null ? (
                <span className="text-xs bg-gray-100 text-gray-500 px-2 py-1 rounded-full">N/A</span>
              ) : report.has_source_link_if_news ? (
                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Pass
                </span>
              ) : (
                <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full flex items-center gap-1">
                  <XCircle className="w-3 h-3" /> Fail
                </span>
              )}
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">No Offensive Content</span>
              {report.has_no_offensive_content ? (
                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Pass
                </span>
              ) : (
                <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full flex items-center gap-1">
                  <XCircle className="w-3 h-3" /> Fail
                </span>
              )}
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">No Misinformation (News)</span>
              {report.has_no_misinformation === null ? (
                <span className="text-xs bg-gray-100 text-gray-500 px-2 py-1 rounded-full">N/A</span>
              ) : report.has_no_misinformation ? (
                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Pass
                </span>
              ) : (
                <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full flex items-center gap-1">
                  <XCircle className="w-3 h-3" /> Fail
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Reasoning */}
        <div className="p-4 bg-gradient-to-br from-blue-50/50 to-purple-50/50 rounded-xl border border-blue-100/50">
          <h4 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
            <div className="w-1 h-4 bg-gradient-to-b from-blue-500 to-purple-500 rounded-full"></div>
            Verification Reasoning
          </h4>
          <p className="text-gray-700 leading-relaxed whitespace-pre-line">{report.reasoning}</p>
        </div>

        {/* Issues Found */}
        {report.issues_found && report.issues_found.length > 0 && (
          <div className="p-4 bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl border border-amber-200">
            <h4 className="text-sm font-bold text-amber-900 mb-3 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-600" />
              Issues Found ({report.issues_found.length})
            </h4>
            <ul className="space-y-2">
              {report.issues_found.map((issue, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-amber-800">
                  <span className="text-amber-500 mt-0.5">•</span>
                  {issue}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Post Preview */}
        {post && (
          <div className="p-4 bg-gradient-to-br from-slate-50 to-gray-50 rounded-xl border border-slate-200">
            <h4 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-slate-600" />
              Verified Post
            </h4>
            <div className="bg-white p-3 rounded-lg border border-gray-200">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded-full capitalize">
                  {post.platform}
                </span>
                <span className="text-xs bg-purple-50 text-purple-700 px-2 py-1 rounded-full">
                  {post.post_type.replace(/_/g, ' ')}
                </span>
                <span className={cn(
                  "text-xs px-2 py-1 rounded-full",
                  post.status === 'published' ? "bg-green-50 text-green-700" :
                  post.status === 'pending' ? "bg-amber-50 text-amber-700" :
                  "bg-red-50 text-red-700"
                )}>
                  {post.status}
                </span>
              </div>
              <p className="text-sm text-gray-700 line-clamp-3">{post.text}</p>
            </div>
          </div>
        )}

        {/* Metadata */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-soft">
            <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Verified At</h4>
            <p className="text-sm text-gray-900 font-medium">{formatDateTime(report.created_at)}</p>
          </div>
          <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-100 shadow-soft">
            <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">AI Model</h4>
            <p className="text-sm text-purple-900 font-medium">{report.model}</p>
          </div>
        </div>
      </div>
    </ExpandableCard>
  )
}
