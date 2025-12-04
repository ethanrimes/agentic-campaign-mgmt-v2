// frontend/app/instagram/page.tsx

'use client'

import { useState, useEffect, useMemo } from 'react'
import { getCompletedPosts, getCachedInsights, refreshInsights } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'
import { Instagram, RefreshCw, Users, UserPlus, Heart, Eye, Image } from 'lucide-react'
import InstagramPostGrid from '@/components/posts/InstagramPostGrid'
import type { CompletedPost, InstagramAccountInsights, InstagramMediaInsights } from '@/types'
import { formatRelativeTime } from '@/lib/utils'

export default function InstagramPage() {
  const { selectedAsset } = useBusinessAsset()
  const [posts, setPosts] = useState<CompletedPost[]>([])
  const [loading, setLoading] = useState(true)
  const [accountInsights, setAccountInsights] = useState<InstagramAccountInsights | null>(null)
  const [mediaInsights, setMediaInsights] = useState<InstagramMediaInsights[]>([])
  const [isRefreshing, setIsRefreshing] = useState(false)

  useEffect(() => {
    async function loadData() {
      if (!selectedAsset) return

      try {
        setLoading(true)

        // Load posts and insights in parallel
        const [postsData, insightsData] = await Promise.all([
          getCompletedPosts(selectedAsset.id, 'instagram'),
          getCachedInsights(selectedAsset.id, 'instagram'),
        ])

        setPosts(postsData)
        setAccountInsights(insightsData.instagram_account || null)
        setMediaInsights(insightsData.instagram_media || [])
      } catch (error) {
        console.error('Failed to load Instagram data:', error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [selectedAsset])

  const handleRefreshInsights = async () => {
    if (!selectedAsset || isRefreshing) return

    setIsRefreshing(true)
    try {
      const result = await refreshInsights(selectedAsset.id, 'all')

      if (result.status === 'ok') {
        // Wait a moment for the refresh to complete, then reload insights
        await new Promise(resolve => setTimeout(resolve, 2000))
        const insightsData = await getCachedInsights(selectedAsset.id, 'instagram')
        setAccountInsights(insightsData.instagram_account || null)
        setMediaInsights(insightsData.instagram_media || [])
      } else if (result.seconds_until_allowed) {
        alert(`Rate limited. Please wait ${result.seconds_until_allowed} seconds before refreshing again.`)
      } else {
        console.error('Refresh failed:', result.message)
      }
    } catch (error) {
      console.error('Failed to refresh insights:', error)
    } finally {
      setIsRefreshing(false)
    }
  }

  // Calculate total interactions from all media insights (must be before early return)
  const totalInteractions = useMemo(() => {
    return mediaInsights.reduce((sum, media) => {
      return sum +
        (media.likes || 0) +
        (media.comments || 0) +
        (media.saved || 0) +
        (media.shares || 0) +
        (media.views || 0)
    }, 0)
  }, [mediaInsights])

  if (!selectedAsset || loading) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="text-center py-16">
          <Instagram className="w-16 h-16 text-pink-400 mx-auto mb-4 animate-pulse" />
          <p className="text-lg text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  const statusCounts = {
    published: posts.filter(p => p.status === 'published').length,
    pending: posts.filter(p => p.status === 'pending').length,
    failed: posts.filter(p => p.status === 'failed').length,
  }

  const formatNumber = (num: number | null | undefined): string => {
    if (num === null || num === undefined) return '--'
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
    return num.toString()
  }

  return (
    <div className="max-w-7xl mx-auto animate-fade-in">
      {/* Header Section with Integrated Insights */}
      <div className="relative mb-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-100/30 via-blue-100/20 to-slate-100/30 rounded-3xl blur-3xl"></div>
        <div className="relative bg-white rounded-2xl p-8 border border-slate-200 shadow-xl">
          {/* Top row: Profile, Title, Refresh */}
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="relative">
                {accountInsights?.profile_picture_url ? (
                  <img
                    src={accountInsights.profile_picture_url}
                    alt={accountInsights.username || 'Instagram Account'}
                    className="w-16 h-16 rounded-2xl object-cover shadow-lg border-2 border-white"
                  />
                ) : (
                  <div className="w-16 h-16 bg-gradient-to-br from-pink-600 to-rose-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <Instagram className="w-8 h-8 text-white" />
                  </div>
                )}
                <div className="absolute inset-0 bg-pink-600 rounded-2xl blur-xl opacity-30"></div>
              </div>
              <div>
                <h1 className="text-4xl font-bold text-slate-900">
                  Instagram Posts
                </h1>
                <p className="text-slate-600 mt-1">
                  {accountInsights?.username ? `@${accountInsights.username}` : selectedAsset?.name || 'Instagram Account'}
                </p>
              </div>
            </div>
            {/* Refresh button with last updated */}
            <div className="flex flex-col items-end gap-1">
              <button
                onClick={handleRefreshInsights}
                disabled={isRefreshing}
                className="inline-flex items-center gap-2 px-3 py-1.5 text-sm bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 disabled:opacity-50 transition-colors"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
                {isRefreshing ? 'Refreshing...' : 'Refresh'}
              </button>
              {accountInsights?.metrics_fetched_at && (
                <p className="text-xs text-slate-500">
                  Last updated: {formatRelativeTime(accountInsights.metrics_fetched_at)}
                </p>
              )}
            </div>
          </div>

          {/* Post counts row */}
          <div className="flex flex-wrap items-center gap-3 mb-6">
            <div className="bg-slate-100 px-4 py-2 rounded-full border border-slate-200">
              <span className="text-sm font-bold text-slate-900">{posts.length}</span>
              <span className="text-sm text-slate-600 ml-1">total posts</span>
            </div>
            <div className="bg-green-50 px-3 py-2 rounded-full border border-green-200 text-sm">
              <span className="text-green-700 font-medium">{statusCounts.published}</span>
              <span className="text-green-600 ml-1">published</span>
            </div>
            <div className="bg-amber-50 px-3 py-2 rounded-full border border-amber-200 text-sm">
              <span className="text-amber-700 font-medium">{statusCounts.pending}</span>
              <span className="text-amber-600 ml-1">pending</span>
            </div>
            {statusCounts.failed > 0 && (
              <div className="bg-red-50 px-3 py-2 rounded-full border border-red-200 text-sm">
                <span className="text-red-700 font-medium">{statusCounts.failed}</span>
                <span className="text-red-600 ml-1">failed</span>
              </div>
            )}
          </div>

          {/* Account Insights Row 1: Posts, Followers, Following, Total Interactions */}
          <div className="grid grid-cols-4 gap-4 mb-4">
            {/* Posts */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                  <Image className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Posts</p>
                  <p className="text-2xl font-bold text-slate-900">{formatNumber(accountInsights?.media_count)}</p>
                </div>
              </div>
            </div>

            {/* Followers */}
            <div className="bg-gradient-to-br from-pink-50 to-rose-50 rounded-xl p-4 border border-pink-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center">
                  <Users className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Followers</p>
                  <p className="text-2xl font-bold text-slate-900">{formatNumber(accountInsights?.followers_count)}</p>
                </div>
              </div>
            </div>

            {/* Following */}
            <div className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl p-4 border border-purple-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center">
                  <UserPlus className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Following</p>
                  <p className="text-2xl font-bold text-slate-900">{formatNumber(accountInsights?.follows_count)}</p>
                </div>
              </div>
            </div>

            {/* Total Interactions */}
            <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-4 border border-amber-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
                  <Heart className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Total Interactions</p>
                  <p className="text-2xl font-bold text-slate-900">{formatNumber(totalInteractions)}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Account Insights Row 2: Reach (Day, Week, Month) */}
          <div className="grid grid-cols-3 gap-4">
            {/* Reach (Day) */}
            <div className="bg-gradient-to-br from-cyan-50 to-teal-50 rounded-xl p-4 border border-cyan-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center">
                  <Eye className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Reach (Day)</p>
                  <p className="text-2xl font-bold text-slate-900">{formatNumber(accountInsights?.reach_day)}</p>
                </div>
              </div>
            </div>

            {/* Reach (Week) */}
            <div className="bg-gradient-to-br from-emerald-50 to-green-50 rounded-xl p-4 border border-emerald-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center">
                  <Eye className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Reach (Week)</p>
                  <p className="text-2xl font-bold text-slate-900">{formatNumber(accountInsights?.reach_week)}</p>
                </div>
              </div>
            </div>

            {/* Reach (Month) */}
            <div className="bg-gradient-to-br from-sky-50 to-blue-50 rounded-xl p-4 border border-sky-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-sky-500 to-blue-600 flex items-center justify-center">
                  <Eye className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Reach (Month)</p>
                  <p className="text-2xl font-bold text-slate-900">{formatNumber(accountInsights?.reach_days_28)}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Posts Grid */}
      {posts.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-slate-200 shadow-xl">
          <div className="relative inline-block mb-6">
            <Instagram className="w-16 h-16 text-slate-400 mx-auto" />
            <div className="absolute inset-0 bg-slate-500 blur-2xl opacity-20"></div>
          </div>
          <p className="text-lg font-semibold text-slate-900 mb-2">No Instagram posts found</p>
          <p className="text-sm text-slate-600 max-w-md mx-auto">
            Content will appear here after the content creation agent runs
          </p>
        </div>
      ) : (
        <InstagramPostGrid
          posts={posts}
          accountName={accountInsights?.username || selectedAsset.name}
          accountProfilePictureUrl={accountInsights?.profile_picture_url}
          mediaInsights={mediaInsights}
        />
      )}
    </div>
  )
}
