// frontend/components/verifier/VerifierReportCard.tsx

'use client'

import { useEffect, useState } from 'react'
import ExpandableCard from '@/components/common/ExpandableCard'
import { formatDateTime, formatRelativeTime, cn } from '@/lib/utils'
import { ShieldCheck, ShieldX, ShieldAlert, CheckCircle2, XCircle, MinusCircle, ExternalLink, Sparkles, AlertTriangle, Check, X } from 'lucide-react'
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
        <div className="flex items-center gap-2.5 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50 text-slate-400 dark:text-slate-500">
          <MinusCircle className="w-5 h-5 opacity-70" />
          <span className="text-sm font-medium">{label}: N/A</span>
        </div>
      )
    }
    return (
      <div className={cn(
        "flex items-center gap-2.5 p-3 rounded-lg border transition-colors",
        value
          ? "bg-green-50/50 dark:bg-green-900/10 border-green-100 dark:border-green-800/50 text-green-700 dark:text-green-300"
          : "bg-red-50/50 dark:bg-red-900/10 border-red-100 dark:border-red-800/50 text-red-700 dark:text-red-300"
      )}>
        {value ? <CheckCircle2 className="w-5 h-5 shrink-0" /> : <XCircle className="w-5 h-5 shrink-0" />}
        <span className="text-sm font-medium">{label}: {value ? 'Pass' : 'Fail'}</span>
      </div>
    )
  }

  const preview = (
    <div className="space-y-3">
      <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed line-clamp-2">{report.reasoning}</p>
      <div className="flex flex-wrap items-center gap-2">
        {report.has_no_offensive_content ? (
          <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded border border-green-100 dark:border-green-800">
            <Check className="w-3 h-3" /> Safe
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 px-2 py-1 rounded border border-red-100 dark:border-red-800">
            <X className="w-3 h-3" /> Unsafe
          </span>
        )}

        {report.has_no_misinformation !== null && (
          report.has_no_misinformation ? (
            <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded border border-green-100 dark:border-green-800">
              <Check className="w-3 h-3" /> Factual
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 px-2 py-1 rounded border border-red-100 dark:border-red-800">
              <X className="w-3 h-3" /> Misinfo
            </span>
          )
        )}
      </div>
    </div>
  )

  const statusBadge = report.is_approved ? (
    <span className="text-xs bg-gradient-to-r from-green-500 to-emerald-500 text-white px-2.5 py-1 rounded-full flex items-center gap-1.5 font-bold shadow-sm">
      <ShieldCheck className="w-3 h-3" />
      Approved
    </span>
  ) : (
    <span className="text-xs bg-gradient-to-r from-red-500 to-rose-500 text-white px-2.5 py-1 rounded-full flex items-center gap-1.5 font-bold shadow-sm">
      <ShieldX className="w-3 h-3" />
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
      <div className="space-y-6 p-2">
        {/* Overall Result */}
        <div className={cn(
          "p-6 rounded-2xl border transition-all",
          report.is_approved
            ? "bg-green-50/50 dark:bg-green-900/10 border-green-100 dark:border-green-800"
            : "bg-red-50/50 dark:bg-red-900/10 border-red-100 dark:border-red-800"
        )}>
          <div className="flex items-center gap-4">
            <div className={cn(
              "p-3 rounded-full shadow-sm",
              report.is_approved ? "bg-white dark:bg-green-900/30 text-green-600" : "bg-white dark:bg-red-900/30 text-red-600"
            )}>
              {report.is_approved ? (
                <ShieldCheck className="w-8 h-8" />
              ) : (
                <ShieldX className="w-8 h-8" />
              )}
            </div>
            <div>
              <h4 className={cn(
                "text-lg font-bold",
                report.is_approved ? "text-green-900 dark:text-green-100" : "text-red-900 dark:text-red-100"
              )}>
                {report.is_approved ? 'Post Approved' : 'Post Rejected'}
              </h4>
              <p className={cn(
                "text-sm font-medium mt-1",
                report.is_approved ? "text-green-700 dark:text-green-300" : "text-red-700 dark:text-red-300"
              )}>
                {report.is_approved
                  ? 'All safety and fact-check protocols passed.'
                  : 'Violations detected during verification.'
                }
              </p>
            </div>
          </div>
        </div>

        {/* Checklist Details */}
        <div>
          <h4 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-3 ml-1">
            Safety Checks
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <ChecklistItem label="No Offensive Content" value={report.has_no_offensive_content} />
            <ChecklistItem label="No Misinformation" value={report.has_no_misinformation} />
          </div>
        </div>

        {/* Reasoning */}
        <div className="glass-panel p-6 bg-white/40 dark:bg-slate-900/40">
          <h4 className="text-sm font-bold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
            <div className="w-1 h-4 bg-blue-500 rounded-full"></div>
            Analysis
          </h4>
          <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-sm">{report.reasoning}</p>
        </div>

        {/* Issues Found */}
        {report.issues_found && report.issues_found.length > 0 && (
          <div className="p-5 rounded-xl bg-amber-50/50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-800/50">
            <h4 className="text-sm font-bold text-amber-900 dark:text-amber-100 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
              Issues Identified ({report.issues_found.length})
            </h4>
            <ul className="space-y-2">
              {report.issues_found.map((issue, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-amber-800 dark:text-amber-200/80">
                  <span className="text-amber-500 mt-1.5 w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0" />
                  {issue}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Post Preview */}
        {post && (
          <div className="mt-2 pt-6 border-t border-slate-200 dark:border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-3 h-3" /> Target Content
              </h4>
              <Link
                href={`/${post.platform === 'facebook' ? 'facebook' : 'instagram'}?post=${post.id}`}
                className="text-xs font-medium text-primary-600 dark:text-primary-400 hover:underline flex items-center gap-1"
              >
                View full post <ExternalLink className="w-3 h-3" />
              </Link>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-2 mb-3">
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
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-2 italic">"{post.text}"</p>
            </div>
          </div>
        )}
      </div>
    </ExpandableCard>
  )
}
