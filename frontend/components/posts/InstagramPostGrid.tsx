// frontend/components/posts/InstagramPostGrid.tsx

'use client'

import { useState, useEffect, useMemo } from 'react'
import { useSearchParams } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { X, ChevronLeft, ChevronRight, ExternalLink, Play, Sparkles, Heart, MessageCircle, Send, Bookmark, Eye, Clock, Share2, Users, Info } from 'lucide-react'
import type { CompletedPost, InstagramMediaInsights } from '@/types'
import { formatDateTime, formatRelativeTime } from '@/lib/utils'
import Link from 'next/link'
import VerificationStatusBadge from '@/components/common/VerificationStatusBadge'
import MetricTooltip from '@/components/common/MetricTooltip'

interface InstagramPostGridProps {
  posts: CompletedPost[]
  accountName?: string
  accountProfilePictureUrl?: string | null
  mediaInsights?: InstagramMediaInsights[]
}

function formatNumber(num: number | null | undefined): string {
  if (num === null || num === undefined) return '--'
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}

function formatDuration(ms: number | null | undefined): string {
  if (ms === null || ms === undefined) return '--'
  const seconds = Math.floor(ms / 1000)
  if (seconds < 60) return `${seconds}s`
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

export default function InstagramPostGrid({ posts, accountName = 'Instagram Account', accountProfilePictureUrl, mediaInsights = [] }: InstagramPostGridProps) {
  const [selectedPost, setSelectedPost] = useState<CompletedPost | null>(null)
  const [currentMediaIndex, setCurrentMediaIndex] = useState(0)
  const searchParams = useSearchParams()
  const highlightPostId = searchParams.get('post')

  // Create lookup map for insights
  const mediaInsightsMap = useMemo(() => {
    const map = new Map<string, InstagramMediaInsights>()
    mediaInsights.forEach(insight => {
      map.set(insight.platform_media_id, insight)
    })
    return map
  }, [mediaInsights])

  // Get insights for a specific post
  const getMediaMetrics = (post: CompletedPost) => {
    if (!post.platform_post_id) return null
    return mediaInsightsMap.get(post.platform_post_id) || null
  }

  useEffect(() => {
    if (highlightPostId && posts.length > 0) {
      const postToHighlight = posts.find(p => p.id === highlightPostId)
      if (postToHighlight) {
        setSelectedPost(postToHighlight)
      }
    }
  }, [highlightPostId, posts])

  const handlePostClick = (post: CompletedPost) => {
    setSelectedPost(post)
    setCurrentMediaIndex(0)
  }

  const handleClose = () => {
    setSelectedPost(null)
    setCurrentMediaIndex(0)
  }

  const handleNextMedia = () => {
    if (selectedPost?.media_urls && currentMediaIndex < selectedPost.media_urls.length - 1) {
      setCurrentMediaIndex(currentMediaIndex + 1)
    }
  }

  const handlePrevMedia = () => {
    if (currentMediaIndex > 0) {
      setCurrentMediaIndex(currentMediaIndex - 1)
    }
  }

  const selectedMediaMetrics = selectedPost ? getMediaMetrics(selectedPost) : null

  return (
    <>
      {/* Grid View - Instagram profile style */}
      <div className="grid grid-cols-3 gap-1 md:gap-2 lg:gap-4">
        {posts.map((post, index) => {
          const previewMedia = post.media_urls && post.media_urls.length > 0 ? post.media_urls[0] : null
          const isReel = post.post_type === 'instagram_reel' ||
            (previewMedia && (previewMedia.includes('.mp4') || previewMedia.includes('video')))
          const metrics = getMediaMetrics(post)

          return (
            <motion.div
              key={post.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
              className="relative aspect-square bg-slate-100 dark:bg-slate-800 overflow-hidden cursor-pointer group"
              onClick={() => handlePostClick(post)}
            >
              {previewMedia ? (
                <>
                  {isReel ? (
                    <div className="relative w-full h-full">
                      <video
                        src={previewMedia}
                        className="w-full h-full object-cover"
                        muted
                      />
                      {/* Reel indicator */}
                      <div className="absolute top-2 right-2">
                        <Play className="w-6 h-6 text-white drop-shadow-lg" fill="white" />
                      </div>
                    </div>
                  ) : (
                    <img
                      src={previewMedia}
                      alt={post.text.substring(0, 50)}
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                    />
                  )}
                </>
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-pink-50 to-rose-100 dark:from-pink-900/20 dark:to-rose-900/20 p-4">
                  <p className="text-xs text-slate-600 dark:text-slate-300 line-clamp-6 text-center font-medium">
                    {post.text}
                  </p>
                </div>
              )}

              {/* Hover overlay with metrics */}
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center backdrop-blur-[2px]">
                <div className="text-white text-center space-y-3 flex flex-col items-center">
                  <div className="flex items-center gap-4">
                    <div className="flex flex-col items-center gap-0.5">
                      <Heart className="w-5 h-5 fill-white" />
                      <span className="font-bold text-sm">{metrics ? formatNumber(metrics.likes) : '--'}</span>
                    </div>
                    <div className="flex flex-col items-center gap-0.5">
                      <MessageCircle className="w-5 h-5 fill-white" />
                      <span className="font-bold text-sm">{metrics ? formatNumber(metrics.comments) : '--'}</span>
                    </div>
                  </div>

                  {metrics?.views && (
                    <div className="flex items-center gap-1.5 text-xs font-medium bg-black/30 px-2 py-1 rounded-full">
                      <Eye className="w-3.5 h-3.5" />
                      <span>{formatNumber(metrics.views)}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Media count indicator for carousels */}
              {post.media_urls && post.media_urls.length > 1 && (
                <div className="absolute top-2 right-2">
                  <svg className="w-5 h-5 text-white drop-shadow-lg" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M22 8c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8zm-2 0l-8 5-8-5h16zm0 12H4V10l8 5 8-5v10z" />
                  </svg>
                </div>
              )}

              {/* Status badge */}
              <div className="absolute bottom-2 left-2 z-10">
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wide backdrop-blur-md ${post.status === 'published'
                  ? 'bg-green-500/80 text-white'
                  : post.status === 'pending'
                    ? 'bg-amber-500/80 text-white'
                    : 'bg-red-500/80 text-white'
                  }`}>
                  {post.status}
                </span>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Modal - Instagram post style */}
      <AnimatePresence>
        {selectedPost && (
          <motion.div
            className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
          >
            <motion.div
              className="glass-panel w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col md:flex-row shadow-2xl border-0 ring-1 ring-white/20"
              initial={{ scale: 0.9, y: 20, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              exit={{ scale: 0.9, y: 20, opacity: 0 }}
              transition={{ type: "spring", duration: 0.5 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Media Section - Instagram style */}
              <div className="md:w-[60%] bg-black relative flex items-center justify-center group">
                {selectedPost.media_urls && selectedPost.media_urls.length > 0 ? (
                  <>
                    {selectedPost.media_urls[currentMediaIndex].includes('.mp4') ||
                      selectedPost.media_urls[currentMediaIndex].includes('video') ? (
                      <video
                        src={selectedPost.media_urls[currentMediaIndex]}
                        controls
                        className="max-w-full max-h-[60vh] md:max-h-[90vh] object-contain"
                      />
                    ) : (
                      <img
                        src={selectedPost.media_urls[currentMediaIndex]}
                        alt="Post media"
                        className="max-w-full max-h-[60vh] md:max-h-[90vh] object-contain"
                      />
                    )}

                    {/* Media navigation */}
                    {selectedPost.media_urls.length > 1 && (
                      <>
                        <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 flex justify-between px-4 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={handlePrevMedia}
                            disabled={currentMediaIndex === 0}
                            className="bg-white/80 hover:bg-white text-black p-2 rounded-full backdrop-blur-sm disabled:opacity-30 transition-all shadow-lg"
                          >
                            <ChevronLeft className="w-5 h-5" />
                          </button>
                          <button
                            onClick={handleNextMedia}
                            disabled={currentMediaIndex === selectedPost.media_urls.length - 1}
                            className="bg-white/80 hover:bg-white text-black p-2 rounded-full backdrop-blur-sm disabled:opacity-30 transition-all shadow-lg"
                          >
                            <ChevronRight className="w-5 h-5" />
                          </button>
                        </div>

                        {/* Carousel dots */}
                        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-1.5">
                          {selectedPost.media_urls.map((_, index) => (
                            <button
                              key={index}
                              onClick={() => setCurrentMediaIndex(index)}
                              className={`w-1.5 h-1.5 rounded-full transition-all shadow-sm ${index === currentMediaIndex
                                ? 'bg-white w-2 h-2'
                                : 'bg-white/50'
                                }`}
                            />
                          ))}
                        </div>
                      </>
                    )}
                  </>
                ) : (
                  <div className="p-8 text-white/50 text-center">
                    <p>No media available</p>
                  </div>
                )}
              </div>

              {/* Content Section - Instagram comment style */}
              <div className="md:w-[40%] flex flex-col bg-white dark:bg-black">
                {/* Header */}
                <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-gradient-to-tr from-yellow-400 via-red-500 to-purple-600 p-[2px] rounded-full">
                      <div className="w-full h-full bg-white dark:bg-black rounded-full flex items-center justify-center overflow-hidden border border-white dark:border-black">
                        {accountProfilePictureUrl ? (
                          <img src={accountProfilePictureUrl} alt={accountName} className="w-full h-full object-cover" />
                        ) : (
                          <span className="font-bold text-xs">{accountName.charAt(0).toUpperCase()}</span>
                        )}
                      </div>
                    </div>
                    <span className="font-semibold text-sm text-slate-900 dark:text-white">{accountName}</span>
                  </div>
                  <button
                    onClick={handleClose}
                    className="text-slate-900 dark:text-white hover:text-slate-600 transition-colors"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                {/* Caption and details */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                  {/* Caption */}
                  <div className="flex gap-3">
                    <div className="w-8 h-8 bg-gradient-to-tr from-yellow-400 via-red-500 to-purple-600 p-[2px] rounded-full flex-shrink-0">
                      <div className="w-full h-full bg-white dark:bg-black rounded-full flex items-center justify-center overflow-hidden border border-white dark:border-black">
                        {accountProfilePictureUrl ? (
                          <img src={accountProfilePictureUrl} alt={accountName} className="w-full h-full object-cover" />
                        ) : (
                          <span className="font-bold text-xs">{accountName.charAt(0).toUpperCase()}</span>
                        )}
                      </div>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm leading-relaxed">
                        <span className="font-semibold mr-2 text-slate-900 dark:text-white">{accountName}</span>
                        <span className="text-slate-800 dark:text-slate-200 whitespace-pre-line">{selectedPost.text}</span>
                      </p>

                      {/* Hashtags */}
                      {selectedPost.hashtags && selectedPost.hashtags.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {selectedPost.hashtags.map((tag, i) => (
                            <span
                              key={i}
                              className="text-sm text-blue-900 dark:text-blue-100 font-medium cursor-pointer hover:underline"
                            >
                              #{tag}
                            </span>
                          ))}
                        </div>
                      )}

                      <p className="text-xs text-slate-500 mt-2 uppercase">{formatRelativeTime(selectedPost.created_at)}</p>
                    </div>
                  </div>

                  {/* Location */}
                  {selectedPost.location && (
                    <div className="pl-11 text-xs font-medium text-slate-900 dark:text-white">
                      📍 {selectedPost.location}
                    </div>
                  )}

                  {/* Engagement Metrics */}
                  {selectedMediaMetrics && (
                    <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-5 space-y-4">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">Engagement Overview</h4>
                        {selectedMediaMetrics.metrics_fetched_at && (
                          <span className="text-[10px] uppercase tracking-wider font-medium text-slate-400 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded-md">
                            Updated {formatRelativeTime(selectedMediaMetrics.metrics_fetched_at)}
                          </span>
                        )}
                      </div>

                      <div className="grid grid-cols-4 gap-3">
                        <MetricTooltip metricKey="likes" position="bottom">
                          <div className="flex flex-col items-center justify-center p-3 bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800 cursor-help hover:border-pink-200 dark:hover:border-pink-800 transition-colors">
                            <Heart className="w-5 h-5 text-pink-500 mb-1" fill="currentColor" />
                            <p className="text-lg font-bold text-slate-900 dark:text-white">
                              {formatNumber(selectedMediaMetrics.likes)}
                            </p>
                            <p className="text-[10px] font-medium text-slate-500 uppercase tracking-wide">Likes</p>
                          </div>
                        </MetricTooltip>
                        <MetricTooltip metricKey="comments" position="bottom">
                          <div className="flex flex-col items-center justify-center p-3 bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800 cursor-help hover:border-blue-200 dark:hover:border-blue-800 transition-colors">
                            <MessageCircle className="w-5 h-5 text-blue-500 mb-1" />
                            <p className="text-lg font-bold text-slate-900 dark:text-white">
                              {formatNumber(selectedMediaMetrics.comments)}
                            </p>
                            <p className="text-[10px] font-medium text-slate-500 uppercase tracking-wide">Comments</p>
                          </div>
                        </MetricTooltip>
                        <MetricTooltip metricKey="saved" position="bottom">
                          <div className="flex flex-col items-center justify-center p-3 bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800 cursor-help hover:border-amber-200 dark:hover:border-amber-800 transition-colors">
                            <Bookmark className="w-5 h-5 text-amber-500 mb-1" />
                            <p className="text-lg font-bold text-slate-900 dark:text-white">
                              {formatNumber(selectedMediaMetrics.saved)}
                            </p>
                            <p className="text-[10px] font-medium text-slate-500 uppercase tracking-wide">Saves</p>
                          </div>
                        </MetricTooltip>
                        <MetricTooltip metricKey="shares" position="bottom">
                          <div className="flex flex-col items-center justify-center p-3 bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800 cursor-help hover:border-green-200 dark:hover:border-green-800 transition-colors">
                            <Share2 className="w-5 h-5 text-green-500 mb-1" />
                            <p className="text-lg font-bold text-slate-900 dark:text-white">
                              {formatNumber(selectedMediaMetrics.shares)}
                            </p>
                            <p className="text-[10px] font-medium text-slate-500 uppercase tracking-wide">Shares</p>
                          </div>
                        </MetricTooltip>
                      </div>

                      <div className="space-y-2 pt-2 border-t border-slate-200 dark:border-slate-700">
                        <MetricTooltip metricKey="views" position="left">
                          <div className="flex items-center justify-between p-2 rounded-lg hover:bg-white dark:hover:bg-slate-900 transition-colors cursor-help">
                            <div className="flex items-center gap-2">
                              <div className="p-1.5 bg-white dark:bg-slate-800 rounded-md shadow-sm">
                                <Eye className="w-4 h-4 text-slate-500" />
                              </div>
                              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Total Views</span>
                            </div>
                            <span className="font-bold text-slate-900 dark:text-white">
                              {formatNumber(selectedMediaMetrics.views)}
                            </span>
                          </div>
                        </MetricTooltip>
                        <MetricTooltip metricKey="reach" position="left">
                          <div className="flex items-center justify-between p-2 rounded-lg hover:bg-white dark:hover:bg-slate-900 transition-colors cursor-help">
                            <div className="flex items-center gap-2">
                              <div className="p-1.5 bg-white dark:bg-slate-800 rounded-md shadow-sm">
                                <Users className="w-4 h-4 text-slate-500" />
                              </div>
                              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Reach</span>
                            </div>
                            <span className="font-bold text-slate-900 dark:text-white">
                              {formatNumber(selectedMediaMetrics.reach)}
                            </span>
                          </div>
                        </MetricTooltip>
                      </div>

                      {/* Reels-specific metrics */}
                      {(selectedMediaMetrics.ig_reels_avg_watch_time_ms || selectedMediaMetrics.ig_reels_video_view_total_time_ms) && (
                        <div className="pt-3 border-t border-slate-200 dark:border-slate-700">
                          <div className="flex items-center gap-2 mb-3">
                            <Play className="w-4 h-4 text-purple-600" />
                            <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">Reel Performance</span>
                          </div>
                          <MetricTooltip metricKey="ig_reels_avg_watch_time_ms" position="left">
                            <div className="flex items-center justify-between p-3 bg-purple-50/50 dark:bg-purple-900/10 rounded-xl border border-purple-100 dark:border-purple-900/30 cursor-help hover:border-purple-200 dark:hover:border-purple-800 transition-colors">
                              <span className="text-sm font-medium text-slate-600 dark:text-slate-400 flex items-center gap-2">
                                <Clock className="w-4 h-4" />
                                Avg Watch Time
                              </span>
                              <span className="font-bold text-slate-900 dark:text-white">
                                {formatDuration(selectedMediaMetrics.ig_reels_avg_watch_time_ms)}
                              </span>
                            </div>
                          </MetricTooltip>
                        </div>
                      )}
                    </div>
                  )}

                  {/* No metrics available */}
                  {!selectedMediaMetrics && selectedPost.status === 'published' && (
                    <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4 text-center">
                      <p className="text-sm text-slate-500">
                        No engagement metrics cached yet.
                      </p>
                      <p className="text-xs text-slate-400 mt-1">
                        Metrics are refreshed automatically every 24 hours.
                      </p>
                    </div>
                  )}

                  {/* Verification Status */}
                  <div className="pt-3 border-t border-slate-100 dark:border-slate-800">
                    <VerificationStatusBadge
                      status={selectedPost.verification_status || 'unverified'}
                      postId={selectedPost.id}
                      size="sm"
                      fullWidth
                    />
                  </div>
                </div>

                {/* Footer Actions */}
                <div className="border-t border-slate-100 dark:border-slate-800 p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Heart className="w-6 h-6 cursor-pointer hover:text-slate-500 transition-colors" />
                      <MessageCircle className="w-6 h-6 cursor-pointer hover:text-slate-500 transition-colors" />
                      <Send className="w-6 h-6 cursor-pointer hover:text-slate-500 transition-colors" />
                    </div>
                    <Bookmark className="w-6 h-6 cursor-pointer hover:text-slate-500 transition-colors" />
                  </div>

                  <div className="text-xs text-slate-500 uppercase font-medium">
                    {selectedPost.published_at
                      ? formatDateTime(selectedPost.published_at)
                      : formatDateTime(selectedPost.created_at)}
                  </div>

                  {/* View on Instagram button */}
                  {selectedMediaMetrics?.permalink && (
                    <a
                      href={selectedMediaMetrics.permalink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block w-full text-center py-2 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-lg font-medium hover:from-pink-600 hover:to-rose-600 transition-all"
                    >
                      <ExternalLink className="w-4 h-4 inline mr-2" />
                      View on Instagram
                    </a>
                  )}

                  {/* Content Seed Link */}
                  {(selectedPost as any).content_seed_id && (
                    <Link
                      href={`/content-seeds?seed=${(selectedPost as any).content_seed_id}&type=${(selectedPost as any).content_seed_type}`}
                      className="block text-xs text-blue-500 font-semibold mt-2 hover:underline flex items-center gap-1"
                      onClick={handleClose}
                    >
                      <Sparkles className="w-3 h-3" />
                      View Original Idea
                    </Link>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
