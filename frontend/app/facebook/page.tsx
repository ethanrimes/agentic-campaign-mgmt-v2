// frontend/app/facebook/page.tsx

'use client'

import { useState, useEffect } from 'react'
import { getCompletedPosts, getCachedInsights, refreshInsights } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'
import { Facebook, RefreshCw, Users, Heart, Play } from 'lucide-react'
import FacebookPostGrid from '@/components/posts/FacebookPostGrid'
import type { CompletedPost, FacebookPageInsights, FacebookPostInsights, FacebookVideoInsights } from '@/types'
import { formatRelativeTime } from '@/lib/utils'

export default function FacebookPage() {
  const { selectedAsset } = useBusinessAsset()
  const [posts, setPosts] = useState<CompletedPost[]>([])
  const [loading, setLoading] = useState(true)
  const [pageInsights, setPageInsights] = useState<FacebookPageInsights | null>(null)
  const [postInsights, setPostInsights] = useState<FacebookPostInsights[]>([])
  const [videoInsights, setVideoInsights] = useState<FacebookVideoInsights[]>([])
  const [isRefreshing, setIsRefreshing] = useState(false)

  useEffect(() => {
    async function loadData() {
      if (!selectedAsset) return

      try {
        setLoading(true)

        // Load posts and insights in parallel
        const [postsData, insightsData] = await Promise.all([
          getCompletedPosts(selectedAsset.id, 'facebook'),
          getCachedInsights(selectedAsset.id, 'facebook'),
        ])

        setPosts(postsData)
        setPageInsights(insightsData.facebook_page || null)
        setPostInsights(insightsData.facebook_posts || [])
        setVideoInsights(insightsData.facebook_videos || [])
      } catch (error) {
        console.error('Failed to load Facebook data:', error)
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
        const insightsData = await getCachedInsights(selectedAsset.id, 'facebook')
        setPageInsights(insightsData.facebook_page || null)
        setPostInsights(insightsData.facebook_posts || [])
        setVideoInsights(insightsData.facebook_videos || [])
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

  if (!selectedAsset || loading) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="text-center py-16">
          <Facebook className="w-16 h-16 text-blue-400 mx-auto mb-4 animate-pulse" />
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
                {pageInsights?.page_picture_url ? (
                  <img
                    src={pageInsights.page_picture_url}
                    alt={pageInsights.page_name || 'Facebook Page'}
                    className="w-16 h-16 rounded-2xl object-cover shadow-lg border-2 border-white"
                  />
                ) : (
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl flex items-center justify-center shadow-lg">
                    <Facebook className="w-8 h-8 text-white" />
                  </div>
                )}
                <div className="absolute inset-0 bg-blue-600 rounded-2xl blur-xl opacity-30"></div>
              </div>
              <div>
                <h1 className="text-4xl font-bold text-slate-900">
                  Facebook Posts
                </h1>
                <p className="text-slate-600 mt-1">
                  {pageInsights?.page_name || selectedAsset?.name || 'Facebook Page'}
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
              {pageInsights?.metrics_fetched_at && (
                <p className="text-xs text-slate-500">
                  Last updated: {formatRelativeTime(pageInsights.metrics_fetched_at)}
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

          {/* Page Insights Metrics Row */}
          <div className="grid grid-cols-3 gap-4">
            {/* Page Follows */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 border border-green-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                  <Users className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Page Follows</p>
                  <p className="text-2xl font-bold text-slate-900">{formatNumber(pageInsights?.page_follows)}</p>
                </div>
              </div>
            </div>

            {/* Post Engagements (Past Month) */}
            <div className="bg-gradient-to-br from-pink-50 to-rose-50 rounded-xl p-4 border border-pink-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center">
                  <Heart className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Engagements (Month)</p>
                  <p className="text-2xl font-bold text-slate-900">{formatNumber(pageInsights?.page_post_engagements_days_28)}</p>
                </div>
              </div>
            </div>

            {/* Media Views (Past Month) */}
            <div className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl p-4 border border-purple-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center">
                  <Play className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Media Views (Month)</p>
                  <p className="text-2xl font-bold text-slate-900">{formatNumber(pageInsights?.page_media_view_days_28)}</p>
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
            <Facebook className="w-16 h-16 text-slate-400 mx-auto" />
            <div className="absolute inset-0 bg-slate-500 blur-2xl opacity-20"></div>
          </div>
          <p className="text-lg font-semibold text-slate-900 mb-2">No Facebook posts found</p>
          <p className="text-sm text-slate-600 max-w-md mx-auto">
            Content will appear here after the content creation agent runs
          </p>
        </div>
      ) : (
        <FacebookPostGrid
          posts={posts}
          postInsights={postInsights}
          videoInsights={videoInsights}
          pageName={pageInsights?.page_name}
          pagePictureUrl={pageInsights?.page_picture_url}
        />
      )}
    </div>
  )
}
