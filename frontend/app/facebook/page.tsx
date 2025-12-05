// frontend/app/facebook/page.tsx

'use client'

import { useState, useEffect } from 'react'
import { getCompletedPosts, getCachedInsights, refreshInsights } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'
import { Facebook, RefreshCw, Users, Heart, Play, Share2, ChevronDown } from 'lucide-react'
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
  const [pendingExpanded, setPendingExpanded] = useState(true)
  const [publishedExpanded, setPublishedExpanded] = useState(true)

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
    <div className="max-w-7xl mx-auto animate-fade-in pt-20">
      {/* Header Section with Integrated Insights */}
      <div className="relative mb-12">
        {/* Background Decorative Elements */}
        <div className="absolute inset-0 bg-gradient-to-b from-blue-50/50 to-transparent rounded-3xl -z-10"></div>
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-100/30 rounded-full blur-3xl -z-10 translate-x-1/3 -translate-y-1/3"></div>

        <div className="relative bg-white/80 backdrop-blur-sm rounded-3xl p-8 border border-slate-100 shadow-sm">
          {/* Top row: Profile, Title, Refresh */}
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 mb-8">
            <div className="flex items-center gap-5">
              <div className="relative group">
                <div className="absolute inset-0 bg-blue-600 rounded-2xl blur-lg opacity-20 group-hover:opacity-30 transition-opacity"></div>
                {pageInsights?.page_picture_url ? (
                  <img
                    src={pageInsights.page_picture_url}
                    alt={pageInsights.page_name || 'Facebook Page'}
                    className="relative w-16 h-16 rounded-2xl object-cover shadow-md border-4 border-white"
                  />
                ) : (
                  <div className="relative w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center shadow-md border-4 border-white">
                    <Facebook className="w-8 h-8 text-white" />
                  </div>
                )}
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                  Facebook Overview
                </h1>
                <div className="flex items-center gap-2 mt-1.5">
                  <p className="text-slate-500 font-medium">
                    {pageInsights?.page_name || selectedAsset?.name || 'Facebook Page'}
                  </p>
                  <span className="w-1 h-1 rounded-full bg-slate-300"></span>
                  <div className="flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-100">
                    <Users className="w-3 h-3" />
                    {formatNumber(pageInsights?.page_follows)} followers
                  </div>
                </div>
              </div>
            </div>

            {/* Refresh Action */}
            <div className="flex items-center gap-3">
              {pageInsights?.metrics_fetched_at && (
                <span className="text-xs text-slate-400 font-medium">
                  Updated {formatRelativeTime(pageInsights.metrics_fetched_at)}
                </span>
              )}
              <button
                onClick={handleRefreshInsights}
                disabled={isRefreshing}
                className="inline-flex items-center justify-center w-10 h-10 bg-white text-slate-600 rounded-xl border border-slate-200 hover:border-blue-300 hover:text-blue-600 hover:shadow-md disabled:opacity-50 disabled:hover:shadow-none transition-all duration-200"
                title="Refresh Insights"
              >
                <RefreshCw className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Total Posts */}
            <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)] transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center text-slate-600">
                  <Share2 className="w-5 h-5" />
                </div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Posts</span>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-slate-900">{posts.length}</span>
                <span className="text-sm text-slate-500 font-medium">posts</span>
              </div>
              <div className="mt-3 flex gap-2">
                <div className="flex items-center gap-1 text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded-md">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                  {statusCounts.published} published
                </div>
                <div className="flex items-center gap-1 text-xs font-medium text-amber-600 bg-amber-50 px-2 py-1 rounded-md">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                  {statusCounts.pending} pending
                </div>
              </div>
            </div>

            {/* Engagements */}
            <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)] transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-xl bg-pink-50 flex items-center justify-center text-pink-600">
                  <Heart className="w-5 h-5" />
                </div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Engagement</span>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-slate-900">{formatNumber(pageInsights?.page_post_engagements_days_28)}</span>
                <span className="text-sm text-slate-500 font-medium">last 28 days</span>
              </div>
              <div className="mt-3 text-xs text-slate-400 font-medium">
                The number of times people have engaged with your posts through reactions, comments, shares and more.
              </div>
            </div>

            {/* Media Views */}
            <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)] transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center text-purple-600">
                  <Play className="w-5 h-5" />
                </div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Media Views</span>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-slate-900">{formatNumber(pageInsights?.page_media_view_days_28)}</span>
                <span className="text-sm text-slate-500 font-medium">last 28 days</span>
              </div>
              <div className="mt-3 text-xs text-slate-400 font-medium">
                The number of times your content was played or displayed. Content includes videos, posts, stories and ads.
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Posts Content */}
      {posts.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-3xl border border-dashed border-slate-300">
          <div className="relative inline-block mb-6">
            <Facebook className="w-16 h-16 text-slate-300 mx-auto" />
          </div>
          <p className="text-lg font-semibold text-slate-900 mb-2">No Facebook posts found</p>
          <p className="text-sm text-slate-500 max-w-md mx-auto">
            Content will appear here after the content creation agent runs
          </p>
        </div>
      ) : (
        <div className="space-y-12">
          {/* Pending Posts Section */}
          {posts.some(p => p.status === 'pending' || p.status === 'failed') && (
            <section>
              <button
                onClick={() => setPendingExpanded(!pendingExpanded)}
                className="w-full flex items-center gap-3 mb-6 group cursor-pointer"
              >
                <h2 className="text-xl font-bold text-slate-800">Pending & Scheduled</h2>
                <div className="h-px flex-1 bg-slate-200"></div>
                <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                  {posts.filter(p => p.status === 'pending' || p.status === 'failed').length} posts
                </span>
                <ChevronDown className={`w-5 h-5 text-slate-400 transition-transform duration-200 ${pendingExpanded ? '' : '-rotate-90'}`} />
              </button>
              {pendingExpanded && (
                <FacebookPostGrid
                  posts={posts.filter(p => p.status === 'pending' || p.status === 'failed')}
                  postInsights={postInsights}
                  videoInsights={videoInsights}
                  pageName={pageInsights?.page_name}
                  pagePictureUrl={pageInsights?.page_picture_url}
                />
              )}
            </section>
          )}

          {/* Published Posts Section */}
          {posts.some(p => p.status === 'published') && (
            <section>
              <button
                onClick={() => setPublishedExpanded(!publishedExpanded)}
                className="w-full flex items-center gap-3 mb-6 group cursor-pointer"
              >
                <h2 className="text-xl font-bold text-slate-800">Published History</h2>
                <div className="h-px flex-1 bg-slate-200"></div>
                <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                  {posts.filter(p => p.status === 'published').length} posts
                </span>
                <ChevronDown className={`w-5 h-5 text-slate-400 transition-transform duration-200 ${publishedExpanded ? '' : '-rotate-90'}`} />
              </button>
              {publishedExpanded && (
                <FacebookPostGrid
                  posts={posts.filter(p => p.status === 'published')}
                  postInsights={postInsights}
                  videoInsights={videoInsights}
                  pageName={pageInsights?.page_name}
                  pagePictureUrl={pageInsights?.page_picture_url}
                />
              )}
            </section>
          )}
        </div>
      )}
    </div>
  )
}
