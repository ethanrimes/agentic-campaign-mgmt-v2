// frontend/components/posts/FacebookPostGrid.tsx

'use client'

import { useState, useEffect, useMemo } from 'react'
import { useSearchParams } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { X, ChevronLeft, ChevronRight, ExternalLink, Sparkles, MessageCircle, ThumbsUp, Share2, Eye, Clock, Play } from 'lucide-react'
import type { CompletedPost, FacebookPostInsights, FacebookVideoInsights } from '@/types'
import { formatDateTime, formatRelativeTime } from '@/lib/utils'
import Link from 'next/link'
import VerificationStatusBadge from '@/components/common/VerificationStatusBadge'

interface FacebookPostGridProps {
  posts: CompletedPost[]
  postInsights?: FacebookPostInsights[]
  videoInsights?: FacebookVideoInsights[]
  pageName?: string | null
  pagePictureUrl?: string | null
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

export default function FacebookPostGrid({ posts, postInsights = [], videoInsights = [], pageName, pagePictureUrl }: FacebookPostGridProps) {
  const [selectedPost, setSelectedPost] = useState<CompletedPost | null>(null)
  const [currentMediaIndex, setCurrentMediaIndex] = useState(0)
  const searchParams = useSearchParams()
  const highlightPostId = searchParams.get('post')

  // Create lookup maps for insights
  const postInsightsMap = useMemo(() => {
    const map = new Map<string, FacebookPostInsights>()
    postInsights.forEach(insight => {
      map.set(insight.platform_post_id, insight)
    })
    return map
  }, [postInsights])

  const videoInsightsMap = useMemo(() => {
    const map = new Map<string, FacebookVideoInsights>()
    videoInsights.forEach(insight => {
      map.set(insight.video_id, insight)
    })
    return map
  }, [videoInsights])

  // Get insights for a specific post
  const getPostMetrics = (post: CompletedPost) => {
    if (!post.platform_post_id) return null
    return postInsightsMap.get(post.platform_post_id) || null
  }

  const getVideoMetrics = (post: CompletedPost) => {
    if (!post.platform_post_id) return null
    return videoInsightsMap.get(post.platform_post_id) || null
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

  const selectedPostMetrics = selectedPost ? getPostMetrics(selectedPost) : null
  const selectedVideoMetrics = selectedPost ? getVideoMetrics(selectedPost) : null

  return (
    <>
      {/* Grid View */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {posts.map((post, index) => {
          const previewMedia = post.media_urls && post.media_urls.length > 0 ? post.media_urls[0] : null
          const isVideo = previewMedia && (previewMedia.includes('.mp4') || previewMedia.includes('video'))
          const metrics = getPostMetrics(post)

          return (
            <motion.div
              key={post.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="group relative aspect-[4/5] bg-slate-100 dark:bg-slate-800 rounded-xl overflow-hidden cursor-pointer shadow-sm hover:shadow-lg hover:shadow-blue-500/10 transition-all duration-300 border border-slate-200 dark:border-slate-700"
              onClick={() => handlePostClick(post)}
            >
              {previewMedia ? (
                <>
                  {isVideo ? (
                    <video
                      src={previewMedia}
                      className="w-full h-full object-cover"
                      muted
                    />
                  ) : (
                    <img
                      src={previewMedia}
                      alt={post.text.substring(0, 50)}
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                    />
                  )}
                </>
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-6">
                  <p className="text-xs text-slate-600 dark:text-slate-300 line-clamp-6 text-center font-medium leading-relaxed">
                    {post.text}
                  </p>
                </div>
              )}

              {/* Overlay Gradient */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

              {/* Media count badge */}
              {post.media_urls && post.media_urls.length > 1 && (
                <div className="absolute top-3 right-3 bg-black/50 backdrop-blur-sm text-white text-xs px-2.5 py-1 rounded-full font-medium">
                  {post.media_urls.length}
                </div>
              )}

              {/* Hover Stats Overlay */}
              {metrics && (
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                  <div className="text-white text-center space-y-2">
                    <div className="flex items-center gap-4 justify-center">
                      <div className="flex items-center gap-1">
                        <ThumbsUp className="w-4 h-4" />
                        <span className="font-semibold">{formatNumber(metrics.reactions_total)}</span>
                      </div>
                      {metrics.post_media_view !== null && metrics.post_media_view !== undefined && (
                        <div className="flex items-center gap-1">
                          <Play className="w-4 h-4" />
                          <span className="font-semibold">{formatNumber(metrics.post_media_view)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Bottom Info */}
              <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between translate-y-4 group-hover:translate-y-0 opacity-0 group-hover:opacity-100 transition-all duration-300">
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium backdrop-blur-md ${post.status === 'published'
                  ? 'bg-green-500/80 text-white'
                  : post.status === 'pending'
                    ? 'bg-amber-500/80 text-white'
                    : 'bg-red-500/80 text-white'
                  }`}>
                  {post.status}
                </span>

                <VerificationStatusBadge
                  status={post.verification_status || 'unverified'}
                  postId={post.id}
                  size="sm"
                  className="backdrop-blur-md bg-white/90 dark:bg-slate-900/90"
                />
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Modal */}
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
              {/* Media Section */}
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
                            className="bg-black/50 hover:bg-black/70 text-white p-2 rounded-full backdrop-blur-sm disabled:opacity-30 transition-all"
                          >
                            <ChevronLeft className="w-6 h-6" />
                          </button>
                          <button
                            onClick={handleNextMedia}
                            disabled={currentMediaIndex === selectedPost.media_urls.length - 1}
                            className="bg-black/50 hover:bg-black/70 text-white p-2 rounded-full backdrop-blur-sm disabled:opacity-30 transition-all"
                          >
                            <ChevronRight className="w-6 h-6" />
                          </button>
                        </div>

                        <div className="absolute bottom-6 left-1/2 -translate-x-1/2">
                          <div className="flex gap-2">
                            {selectedPost.media_urls.map((_, idx) => (
                              <div
                                key={idx}
                                className={`w-2 h-2 rounded-full transition-all ${idx === currentMediaIndex ? 'bg-white scale-125' : 'bg-white/40'
                                  }`}
                              />
                            ))}
                          </div>
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

              {/* Content Section */}
              <div className="md:w-[40%] flex flex-col bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl">
                {/* Header */}
                <div className="p-4 border-b border-slate-200/60 dark:border-slate-700/60 flex items-start justify-between bg-white/50 dark:bg-slate-900/50">
                  <div className="flex items-center gap-3">
                    {pagePictureUrl ? (
                      <img
                        src={pagePictureUrl}
                        alt={pageName || 'Facebook Page'}
                        className="w-10 h-10 rounded-full object-cover shadow-md"
                      />
                    ) : (
                      <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center shadow-md">
                        <svg className="w-6 h-6 text-white fill-current" viewBox="0 0 24 24">
                          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.962.925-1.962 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                        </svg>
                      </div>
                    )}
                    <div>
                      <h3 className="font-bold text-slate-900 dark:text-white">{pageName || 'Facebook Post'}</h3>
                      <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                        <span className="capitalize">{selectedPost.status}</span>
                        <span>•</span>
                        <span>{formatDateTime(selectedPost.created_at)}</span>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={handleClose}
                    className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Scrollable Body */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                  {/* Caption */}
                  <div>
                    <p className="text-slate-800 dark:text-slate-200 whitespace-pre-line leading-relaxed text-[15px]">
                      {selectedPost.text}
                    </p>
                  </div>

                  {/* Hashtags */}
                  {selectedPost.hashtags && selectedPost.hashtags.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {selectedPost.hashtags.map((tag, i) => (
                        <span
                          key={i}
                          className="text-sm text-blue-600 dark:text-blue-400 hover:underline cursor-pointer"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Engagement Metrics - Post Level */}
                  {selectedPostMetrics && (
                    <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4 space-y-3">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300">Engagement Metrics</h4>
                        {selectedPostMetrics.metrics_fetched_at && (
                          <span className="text-xs text-slate-500">
                            {formatRelativeTime(selectedPostMetrics.metrics_fetched_at)}
                          </span>
                        )}
                      </div>

                      <div className="grid grid-cols-3 gap-3">
                        <div className="text-center p-2 bg-white dark:bg-slate-900 rounded-lg">
                          <div className="flex items-center justify-center gap-1 text-blue-600 mb-1">
                            <ThumbsUp className="w-4 h-4" />
                          </div>
                          <p className="text-lg font-bold text-slate-900 dark:text-white">
                            {formatNumber(selectedPostMetrics.reactions_total)}
                          </p>
                          <p className="text-xs text-slate-500">Reactions</p>
                        </div>
                        <div className="text-center p-2 bg-white dark:bg-slate-900 rounded-lg">
                          <div className="flex items-center justify-center gap-1 text-green-600 mb-1">
                            <MessageCircle className="w-4 h-4" />
                          </div>
                          <p className="text-lg font-bold text-slate-900 dark:text-white">
                            {formatNumber(selectedPostMetrics.comments)}
                          </p>
                          <p className="text-xs text-slate-500">Comments</p>
                        </div>
                        <div className="text-center p-2 bg-white dark:bg-slate-900 rounded-lg">
                          <div className="flex items-center justify-center gap-1 text-purple-600 mb-1">
                            <Share2 className="w-4 h-4" />
                          </div>
                          <p className="text-lg font-bold text-slate-900 dark:text-white">
                            {formatNumber(selectedPostMetrics.shares)}
                          </p>
                          <p className="text-xs text-slate-500">Shares</p>
                        </div>
                      </div>

                      <div className="pt-2 border-t border-slate-200 dark:border-slate-700">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-slate-600 dark:text-slate-400 flex items-center gap-1">
                            <Eye className="w-4 h-4" />
                            Reach (Unique)
                          </span>
                          <span className="font-semibold text-slate-900 dark:text-white">
                            {formatNumber(selectedPostMetrics.post_impressions_unique)}
                          </span>
                        </div>
                        <div className="flex items-center justify-between text-sm mt-1">
                          <span className="text-slate-600 dark:text-slate-400">Total Impressions</span>
                          <span className="font-semibold text-slate-900 dark:text-white">
                            {formatNumber(selectedPostMetrics.post_impressions)}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Video Metrics */}
                  {selectedVideoMetrics && (
                    <div className="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4 space-y-3">
                      <div className="flex items-center gap-2 mb-2">
                        <Play className="w-4 h-4 text-purple-600" />
                        <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300">Video Metrics</h4>
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div className="text-center p-2 bg-white dark:bg-slate-900 rounded-lg">
                          <p className="text-lg font-bold text-slate-900 dark:text-white">
                            {formatNumber(selectedVideoMetrics.post_video_views)}
                          </p>
                          <p className="text-xs text-slate-500">Total Views</p>
                        </div>
                        <div className="text-center p-2 bg-white dark:bg-slate-900 rounded-lg">
                          <p className="text-lg font-bold text-slate-900 dark:text-white">
                            {formatNumber(selectedVideoMetrics.post_video_views_unique)}
                          </p>
                          <p className="text-xs text-slate-500">Unique Views</p>
                        </div>
                      </div>

                      <div className="pt-2 border-t border-purple-200 dark:border-purple-800">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-slate-600 dark:text-slate-400 flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            Avg Watch Time
                          </span>
                          <span className="font-semibold text-slate-900 dark:text-white">
                            {formatDuration(selectedVideoMetrics.post_video_avg_time_watched_ms)}
                          </span>
                        </div>
                        {selectedVideoMetrics.video_length_ms && (
                          <div className="flex items-center justify-between text-sm mt-1">
                            <span className="text-slate-600 dark:text-slate-400">Video Length</span>
                            <span className="font-semibold text-slate-900 dark:text-white">
                              {formatDuration(selectedVideoMetrics.video_length_ms)}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* No metrics available */}
                  {!selectedPostMetrics && !selectedVideoMetrics && selectedPost.status === 'published' && (
                    <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4 text-center">
                      <p className="text-sm text-slate-500">
                        No engagement metrics cached yet.
                      </p>
                      <p className="text-xs text-slate-400 mt-1">
                        Metrics are refreshed automatically every 24 hours.
                      </p>
                    </div>
                  )}

                  {/* Metadata Cards */}
                  <div className="grid grid-cols-2 gap-3">
                    {selectedPost.location && (
                      <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg border border-slate-100 dark:border-slate-700">
                        <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Location</span>
                        <p className="text-sm font-medium text-slate-900 dark:text-white truncate">{selectedPost.location}</p>
                      </div>
                    )}
                    <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg border border-slate-100 dark:border-slate-700">
                      <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Verification</span>
                      <div className="mt-1">
                        <VerificationStatusBadge
                          status={selectedPost.verification_status || 'unverified'}
                          postId={selectedPost.id}
                          size="sm"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Seed Link */}
                  {(selectedPost as any).content_seed_id && (
                    <Link
                      href={`/content-seeds?seed=${(selectedPost as any).content_seed_id}&type=${(selectedPost as any).content_seed_type}`}
                      className="block p-4 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-100 dark:border-blue-800 hover:border-blue-300 dark:hover:border-blue-600 transition-colors group"
                      onClick={handleClose}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold text-blue-600 dark:text-blue-400 flex items-center gap-1.5">
                          <Sparkles className="w-3 h-3" />
                          Generated From Content Seed
                        </span>
                        <ExternalLink className="w-3 h-3 text-blue-400 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                      </div>
                      <div className="text-sm font-medium text-slate-900 dark:text-white line-clamp-1">
                        {(selectedPost as any).seed_name || 'Unknown Seed'}
                      </div>
                    </Link>
                  )}
                </div>

                {/* Footer Actions */}
                <div className="p-4 border-t border-slate-200/60 dark:border-slate-700/60 bg-white/50 dark:bg-slate-900/50 backdrop-blur-md flex gap-3">
                  {selectedPost.platform_post_url ? (
                    <a
                      href={selectedPost.platform_post_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-lg font-medium transition-colors shadow-lg shadow-blue-600/20"
                    >
                      <ExternalLink className="w-4 h-4" />
                      View on Facebook
                    </a>
                  ) : (
                    <div className="flex-1 flex items-center justify-center gap-2 bg-slate-100 dark:bg-slate-800 text-slate-400 py-2.5 rounded-lg font-medium cursor-not-allowed">
                      Not Published Yet
                    </div>
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
