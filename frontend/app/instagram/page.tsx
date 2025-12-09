// frontend/app/instagram/page.tsx

'use client'

import { useState, useEffect, useMemo } from 'react'
import { getCompletedPosts, getCachedInsights, refreshInsights } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'
import { Instagram, RefreshCw, Users, UserPlus, Heart, Eye, Image, ChevronDown, AlertCircle, Play, Film, Layers } from 'lucide-react'
import InstagramPostGrid from '@/components/posts/InstagramPostGrid'
import MetricTooltip from '@/components/common/MetricTooltip'
import type { CompletedPost, InstagramAccountInsights, InstagramMediaInsights } from '@/types'
import { formatRelativeTime } from '@/lib/utils'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

// Instagram post type definitions
const INSTAGRAM_POST_TYPES = [
  { id: 'all', label: 'All', icon: Image },
  { id: 'instagram_image', label: 'Image', icon: Image },
  { id: 'instagram_carousel', label: 'Carousel', icon: Layers },
  { id: 'instagram_reel', label: 'Reel', icon: Film },
] as const

type InstagramPostType = typeof INSTAGRAM_POST_TYPES[number]['id']

export default function InstagramPage() {
  const { selectedAsset } = useBusinessAsset()
  const [posts, setPosts] = useState<CompletedPost[]>([])
  const [loading, setLoading] = useState(true)
  const [accountInsights, setAccountInsights] = useState<InstagramAccountInsights | null>(null)
  const [mediaInsights, setMediaInsights] = useState<InstagramMediaInsights[]>([])
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [pendingExpanded, setPendingExpanded] = useState(true)
  const [publishedExpanded, setPublishedExpanded] = useState(true)
  const [failedExpanded, setFailedExpanded] = useState(true)
  const [selectedPostType, setSelectedPostType] = useState<InstagramPostType>('all')

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

  // Calculate total interactions from all media insights (likes + comments + saves + shares, NOT views)
  const totalInteractions = useMemo(() => {
    return mediaInsights.reduce((sum, media) => {
      return sum +
        (media.likes || 0) +
        (media.comments || 0) +
        (media.saved || 0) +
        (media.shares || 0)
    }, 0)
  }, [mediaInsights])

  // Calculate total views from all media insights
  const totalViews = useMemo(() => {
    return mediaInsights.reduce((sum, media) => sum + (media.views || 0), 0)
  }, [mediaInsights])

  // Filter posts by selected type
  const filteredPosts = useMemo(() => {
    if (selectedPostType === 'all') return posts
    return posts.filter(p => p.post_type === selectedPostType)
  }, [posts, selectedPostType])

  // Get counts by post type for display
  const postTypeCounts = useMemo(() => {
    const counts: Record<string, number> = { all: posts.length }
    posts.forEach(p => {
      counts[p.post_type] = (counts[p.post_type] || 0) + 1
    })
    return counts
  }, [posts])

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
    <div className="max-w-7xl mx-auto animate-fade-in pt-20">
      {/* Header Section with Integrated Insights */}
      <div className="relative mb-12">
        {/* Background Decorative Elements */}
        <div className="absolute inset-0 bg-gradient-to-b from-pink-50/50 to-transparent rounded-3xl -z-10"></div>
        <div className="absolute top-0 right-0 w-64 h-64 bg-pink-100/30 rounded-full blur-3xl -z-10 translate-x-1/3 -translate-y-1/3"></div>

        <div className="relative bg-white/80 backdrop-blur-sm rounded-3xl p-8 border border-slate-100 shadow-sm">
          {/* Top row: Profile, Title, Refresh */}
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 mb-8">
            <div className="flex items-center gap-5">
              <div className="relative group">
                <div className="absolute inset-0 bg-pink-600 rounded-2xl blur-lg opacity-20 group-hover:opacity-30 transition-opacity"></div>
                {accountInsights?.profile_picture_url ? (
                  <img
                    src={accountInsights.profile_picture_url}
                    alt={accountInsights.username || 'Instagram Account'}
                    className="relative w-16 h-16 rounded-2xl object-cover shadow-md border-4 border-white"
                  />
                ) : (
                  <div className="relative w-16 h-16 bg-gradient-to-br from-pink-600 to-rose-600 rounded-2xl flex items-center justify-center shadow-md border-4 border-white">
                    <Instagram className="w-8 h-8 text-white" />
                  </div>
                )}
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                  Instagram Overview
                </h1>
                <div className="flex items-center gap-2 mt-1.5">
                  <p className="text-slate-500 font-medium">
                    {accountInsights?.username ? `@${accountInsights.username}` : selectedAsset?.name || 'Instagram Account'}
                  </p>
                  <span className="w-1 h-1 rounded-full bg-slate-300"></span>
                  <div className="flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-pink-50 text-pink-700 border border-pink-100">
                    <Users className="w-3 h-3" />
                    {formatNumber(accountInsights?.followers_count)} followers
                  </div>
                </div>
              </div>
            </div>

            {/* Refresh Action */}
            <div className="flex items-center gap-3">
              {accountInsights?.metrics_fetched_at && (
                <span className="text-xs text-slate-400 font-medium">
                  Updated {formatRelativeTime(accountInsights.metrics_fetched_at)}
                </span>
              )}
              <button
                onClick={handleRefreshInsights}
                disabled={isRefreshing}
                className="inline-flex items-center justify-center w-10 h-10 bg-white text-slate-600 rounded-xl border border-slate-200 hover:border-pink-300 hover:text-pink-600 hover:shadow-md disabled:opacity-50 disabled:hover:shadow-none transition-all duration-200"
                title="Refresh Insights"
              >
                <RefreshCw className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-stretch">
            {/* Posts */}
            <MetricTooltip metricKey="posts" metricType="account" position="bottom">
              <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)] transition-shadow cursor-help h-full flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600">
                    <Image className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Posts</span>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-slate-900">{statusCounts.published}</span>
                  <span className="text-xs text-slate-500 font-medium">published</span>
                </div>
                <div className="mt-auto pt-2 flex flex-wrap gap-2">
                  <div className="flex items-center gap-1 text-xs font-medium text-amber-600 bg-amber-50 px-2 py-1 rounded-md">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                    {statusCounts.pending} pending
                  </div>
                  {statusCounts.failed > 0 && (
                    <div className="flex items-center gap-1 text-xs font-medium text-red-600 bg-red-50 px-2 py-1 rounded-md">
                      <AlertCircle className="w-3 h-3" />
                      {statusCounts.failed} failed
                    </div>
                  )}
                </div>
              </div>
            </MetricTooltip>

            {/* Reach */}
            <MetricTooltip metricKey="reach" metricType="account" position="bottom">
              <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)] transition-shadow cursor-help h-full flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-sky-50 flex items-center justify-center text-sky-600">
                    <Users className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Reach</span>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-slate-900">{formatNumber(accountInsights?.reach_day)}</span>
                  <span className="text-xs text-slate-500 font-medium">28 days</span>
                </div>
                <div className="mt-auto pt-2 text-xs text-slate-400 font-medium">
                  Unique accounts reached
                </div>
              </div>
            </MetricTooltip>

            {/* Total Views */}
            <MetricTooltip metricKey="views" metricType="account" position="bottom">
              <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)] transition-shadow cursor-help h-full flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center text-purple-600">
                    <Play className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Views</span>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-slate-900">{formatNumber(totalViews)}</span>
                  <span className="text-xs text-slate-500 font-medium">total</span>
                </div>
                <div className="mt-auto pt-2 text-xs text-slate-400 font-medium">
                  Total post views
                </div>
              </div>
            </MetricTooltip>

            {/* Total Interactions */}
            <MetricTooltip metricKey="interactions" metricType="account" position="bottom">
              <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)] transition-shadow cursor-help h-full flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center text-amber-600">
                    <Heart className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Interactions</span>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-slate-900">{formatNumber(totalInteractions)}</span>
                  <span className="text-xs text-slate-500 font-medium">total</span>
                </div>
                <div className="mt-auto pt-2 text-xs text-slate-400 font-medium">
                  Likes, comments, saves, shares
                </div>
              </div>
            </MetricTooltip>

            {/* Followers */}
            <MetricTooltip metricKey="followers" metricType="account" position="bottom">
              <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)] transition-shadow cursor-help h-full flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-pink-50 flex items-center justify-center text-pink-600">
                    <Users className="w-5 h-5" />
                  </div>
                  <div className="flex items-center gap-1 text-xs font-medium text-slate-400">
                    <UserPlus className="w-3 h-3" />
                    {formatNumber(accountInsights?.follows_count)} following
                  </div>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-slate-900">{formatNumber(accountInsights?.followers_count)}</span>
                  <span className="text-xs text-slate-500 font-medium">followers</span>
                </div>
                <div className="mt-auto pt-2 text-xs text-slate-400 font-medium">
                  Accounts following you
                </div>
              </div>
            </MetricTooltip>
          </div>
        </div>
      </div>

      {/* Media Format Filter Chips */}
      {posts.length > 0 && (
        <div className="mb-8">
          <div className="flex flex-wrap gap-3 justify-center">
            {INSTAGRAM_POST_TYPES.map((type) => {
              const isActive = selectedPostType === type.id
              const count = postTypeCounts[type.id] || 0
              const Icon = type.icon

              return (
                <motion.button
                  key={type.id}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setSelectedPostType(type.id)}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-full border-2 transition-all duration-300 shadow-sm",
                    isActive
                      ? "bg-pink-500 border-pink-500 text-white shadow-lg shadow-pink-500/30"
                      : "bg-white border-slate-200 text-slate-600 hover:border-slate-300"
                  )}
                >
                  <Icon className={cn("w-4 h-4", isActive ? "text-white" : "text-pink-500")} />
                  <span className="font-bold text-sm">{type.label}</span>
                  <span className={cn(
                    "text-xs px-2 py-0.5 rounded-full font-mono",
                    isActive ? "bg-white/20 text-white" : "bg-slate-100 text-slate-500"
                  )}>
                    {count}
                  </span>
                </motion.button>
              )
            })}
          </div>
        </div>
      )}

      {/* Posts Content */}
      {filteredPosts.length === 0 && posts.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-3xl border border-dashed border-slate-300">
          <div className="relative inline-block mb-6">
            <Instagram className="w-16 h-16 text-slate-300 mx-auto" />
          </div>
          <p className="text-lg font-semibold text-slate-900 mb-2">No Instagram posts found</p>
          <p className="text-sm text-slate-500 max-w-md mx-auto">
            Content will appear here after the content creation agent runs
          </p>
        </div>
      ) : filteredPosts.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-3xl border border-dashed border-slate-300">
          <div className="relative inline-block mb-6">
            <Instagram className="w-16 h-16 text-slate-300 mx-auto" />
          </div>
          <p className="text-lg font-semibold text-slate-900 mb-2">No posts match this filter</p>
          <p className="text-sm text-slate-500 max-w-md mx-auto">
            Try selecting a different media format
          </p>
        </div>
      ) : (
        <div className="space-y-12">
          {/* Pending Posts Section */}
          {filteredPosts.some(p => p.status === 'pending') && (
            <section>
              <button
                onClick={() => setPendingExpanded(!pendingExpanded)}
                className="w-full flex items-center gap-3 mb-6 group cursor-pointer"
              >
                <h2 className="text-xl font-bold text-slate-800">Pending & Scheduled</h2>
                <div className="h-px flex-1 bg-slate-200"></div>
                <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                  {filteredPosts.filter(p => p.status === 'pending').length} posts
                </span>
                <ChevronDown className={`w-5 h-5 text-slate-400 transition-transform duration-200 ${pendingExpanded ? '' : '-rotate-90'}`} />
              </button>
              {pendingExpanded && (
                <InstagramPostGrid
                  posts={filteredPosts.filter(p => p.status === 'pending')}
                  accountName={accountInsights?.username || selectedAsset.name}
                  accountProfilePictureUrl={accountInsights?.profile_picture_url}
                  mediaInsights={mediaInsights}
                />
              )}
            </section>
          )}

          {/* Published Posts Section */}
          {filteredPosts.some(p => p.status === 'published') && (
            <section>
              <button
                onClick={() => setPublishedExpanded(!publishedExpanded)}
                className="w-full flex items-center gap-3 mb-6 group cursor-pointer"
              >
                <h2 className="text-xl font-bold text-slate-800">Published History</h2>
                <div className="h-px flex-1 bg-slate-200"></div>
                <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                  {filteredPosts.filter(p => p.status === 'published').length} posts
                </span>
                <ChevronDown className={`w-5 h-5 text-slate-400 transition-transform duration-200 ${publishedExpanded ? '' : '-rotate-90'}`} />
              </button>
              {publishedExpanded && (
                <InstagramPostGrid
                  posts={filteredPosts.filter(p => p.status === 'published')}
                  accountName={accountInsights?.username || selectedAsset.name}
                  accountProfilePictureUrl={accountInsights?.profile_picture_url}
                  mediaInsights={mediaInsights}
                />
              )}
            </section>
          )}

          {/* Failed Posts Section */}
          {filteredPosts.some(p => p.status === 'failed') && (
            <section>
              <button
                onClick={() => setFailedExpanded(!failedExpanded)}
                className="w-full flex items-center gap-3 mb-6 group cursor-pointer"
              >
                <h2 className="text-xl font-bold text-red-700">Failed</h2>
                <div className="h-px flex-1 bg-red-200"></div>
                <span className="text-xs font-medium text-red-500 uppercase tracking-wider">
                  {filteredPosts.filter(p => p.status === 'failed').length} posts
                </span>
                <ChevronDown className={`w-5 h-5 text-red-400 transition-transform duration-200 ${failedExpanded ? '' : '-rotate-90'}`} />
              </button>
              {failedExpanded && (
                <InstagramPostGrid
                  posts={filteredPosts.filter(p => p.status === 'failed')}
                  accountName={accountInsights?.username || selectedAsset.name}
                  accountProfilePictureUrl={accountInsights?.profile_picture_url}
                  mediaInsights={mediaInsights}
                />
              )}
            </section>
          )}
        </div>
      )}
    </div>
  )
}
