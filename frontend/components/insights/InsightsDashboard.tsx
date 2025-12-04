// frontend/components/insights/InsightsDashboard.tsx

'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { RefreshCw, Eye, Heart, MessageCircle, Share2, Users, TrendingUp, Clock, Play } from 'lucide-react'
import type { FacebookPageInsights, InstagramAccountInsights } from '@/types'
import { formatRelativeTime } from '@/lib/utils'

interface InsightsDashboardProps {
  platform: 'facebook' | 'instagram'
  pageInsights?: FacebookPageInsights | null
  accountInsights?: InstagramAccountInsights | null
  onRefresh?: () => Promise<void>
  isRefreshing?: boolean
}

function formatNumber(num: number | null | undefined): string {
  if (num === null || num === undefined) return '--'
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}

function MetricCard({
  icon: Icon,
  label,
  value,
  subValue,
  color = 'blue'
}: {
  icon: React.ElementType
  label: string
  value: string | number
  subValue?: string
  color?: 'blue' | 'pink' | 'green' | 'amber' | 'purple'
}) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600 bg-blue-50 text-blue-600',
    pink: 'from-pink-500 to-rose-600 bg-pink-50 text-pink-600',
    green: 'from-green-500 to-emerald-600 bg-green-50 text-green-600',
    amber: 'from-amber-500 to-orange-600 bg-amber-50 text-amber-600',
    purple: 'from-purple-500 to-violet-600 bg-purple-50 text-purple-600',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm hover:shadow-md transition-shadow"
    >
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${colorClasses[color].split(' ').slice(0, 2).join(' ')} flex items-center justify-center`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
          <p className="text-xl font-bold text-slate-900">{typeof value === 'number' ? formatNumber(value) : value}</p>
          {subValue && (
            <p className="text-xs text-slate-400 mt-0.5">{subValue}</p>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export default function InsightsDashboard({
  platform,
  pageInsights,
  accountInsights,
  onRefresh,
  isRefreshing = false,
}: InsightsDashboardProps) {
  const lastUpdated = platform === 'facebook'
    ? pageInsights?.metrics_fetched_at
    : accountInsights?.metrics_fetched_at

  if (platform === 'facebook') {
    if (!pageInsights) {
      return (
        <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
          <div className="text-center">
            <p className="text-slate-600 mb-4">No page insights available</p>
            {onRefresh && (
              <button
                onClick={onRefresh}
                disabled={isRefreshing}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                {isRefreshing ? 'Refreshing...' : 'Fetch Insights'}
              </button>
            )}
          </div>
        </div>
      )
    }

    return (
      <div className="space-y-4">
        {/* Header with refresh button */}
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">Page Insights</h3>
            {lastUpdated && (
              <p className="text-xs text-slate-500">
                Last updated: {formatRelativeTime(lastUpdated)}
              </p>
            )}
          </div>
          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              className="inline-flex items-center gap-2 px-3 py-1.5 text-sm bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 disabled:opacity-50 transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
              {isRefreshing ? 'Refreshing...' : 'Refresh'}
            </button>
          )}
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <MetricCard
            icon={Eye}
            label="Page Views (Today)"
            value={pageInsights.page_views_total_day ?? '--'}
            subValue={`${formatNumber(pageInsights.page_views_total_week)} this week`}
            color="blue"
          />
          <MetricCard
            icon={Heart}
            label="Engagements (Today)"
            value={pageInsights.page_post_engagements_day ?? '--'}
            subValue={`${formatNumber(pageInsights.page_post_engagements_week)} this week`}
            color="pink"
          />
          <MetricCard
            icon={Users}
            label="New Follows (Today)"
            value={pageInsights.page_follows_day ?? '--'}
            subValue={`${formatNumber(pageInsights.page_follows_week)} this week`}
            color="green"
          />
          <MetricCard
            icon={Play}
            label="Video Views (Today)"
            value={pageInsights.page_video_views_day ?? '--'}
            subValue={`${formatNumber(pageInsights.page_video_views_week)} this week`}
            color="purple"
          />
        </div>

        {/* Additional stats row */}
        {pageInsights.reactions_total !== null && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-blue-600" />
                <span className="text-sm font-medium text-slate-700">Total Reactions</span>
              </div>
              <span className="text-lg font-bold text-blue-600">
                {formatNumber(pageInsights.reactions_total)}
              </span>
            </div>
          </div>
        )}
      </div>
    )
  }

  // Instagram view
  if (!accountInsights) {
    return (
      <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
        <div className="text-center">
          <p className="text-slate-600 mb-4">No account insights available</p>
          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              className="inline-flex items-center gap-2 px-4 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700 disabled:opacity-50 transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              {isRefreshing ? 'Refreshing...' : 'Fetch Insights'}
            </button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header with refresh button */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">Account Insights</h3>
          {lastUpdated && (
            <p className="text-xs text-slate-500">
              Last updated: {formatRelativeTime(lastUpdated)}
            </p>
          )}
        </div>
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="inline-flex items-center gap-2 px-3 py-1.5 text-sm bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        )}
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard
          icon={Users}
          label="Followers"
          value={accountInsights.followers_count ?? '--'}
          subValue={`Following ${formatNumber(accountInsights.follows_count)}`}
          color="pink"
        />
        <MetricCard
          icon={Eye}
          label="Reach (Today)"
          value={accountInsights.reach_day ?? '--'}
          subValue={`${formatNumber(accountInsights.reach_week)} this week`}
          color="purple"
        />
        <MetricCard
          icon={TrendingUp}
          label="Profile Views"
          value={accountInsights.profile_views_day ?? '--'}
          subValue="Today"
          color="blue"
        />
        <MetricCard
          icon={Heart}
          label="Engaged Accounts"
          value={accountInsights.accounts_engaged_day ?? '--'}
          subValue="Today"
          color="green"
        />
      </div>

      {/* Media count */}
      {accountInsights.media_count !== null && (
        <div className="bg-gradient-to-r from-pink-50 to-rose-50 rounded-xl p-4 border border-pink-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Play className="w-5 h-5 text-pink-600" />
              <span className="text-sm font-medium text-slate-700">Total Media</span>
            </div>
            <span className="text-lg font-bold text-pink-600">
              {formatNumber(accountInsights.media_count)}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
