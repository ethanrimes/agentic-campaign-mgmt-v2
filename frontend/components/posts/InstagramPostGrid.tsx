// frontend/components/posts/InstagramPostGrid.tsx

'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, ChevronLeft, ChevronRight, Calendar, ExternalLink, Play } from 'lucide-react'
import type { CompletedPost } from '@/types'
import { formatDateTime } from '@/lib/utils'

interface InstagramPostGridProps {
  posts: CompletedPost[]
}

export default function InstagramPostGrid({ posts }: InstagramPostGridProps) {
  const [selectedPost, setSelectedPost] = useState<CompletedPost | null>(null)
  const [currentMediaIndex, setCurrentMediaIndex] = useState(0)

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

  return (
    <>
      {/* Grid View - Instagram profile style */}
      <div className="grid grid-cols-3 gap-1">
        {posts.map((post) => {
          const previewMedia = post.media_urls && post.media_urls.length > 0 ? post.media_urls[0] : null
          const isReel = post.post_type === 'instagram_reel' ||
                         (previewMedia && (previewMedia.includes('.mp4') || previewMedia.includes('video')))

          return (
            <div
              key={post.id}
              className="relative aspect-square bg-slate-100 overflow-hidden cursor-pointer group"
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
                      className="w-full h-full object-cover"
                    />
                  )}
                </>
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-pink-50 to-rose-100 p-4">
                  <p className="text-xs text-slate-600 line-clamp-6 text-center">
                    {post.text}
                  </p>
                </div>
              )}

              {/* Hover overlay */}
              <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <div className="text-white text-center space-y-1">
                  {post.media_urls && post.media_urls.length > 1 && (
                    <div className="text-sm font-medium">
                      {post.media_urls.length} items
                    </div>
                  )}
                </div>
              </div>

              {/* Media count indicator for carousels */}
              {post.media_urls && post.media_urls.length > 1 && (
                <div className="absolute top-2 right-2">
                  <svg className="w-5 h-5 text-white drop-shadow-lg" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M22 8c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8zm-2 0l-8 5-8-5h16zm0 12H4V10l8 5 8-5v10z"/>
                  </svg>
                </div>
              )}

              {/* Status badge */}
              <div className="absolute bottom-2 left-2">
                <div className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                  post.status === 'published'
                    ? 'bg-green-500 text-white'
                    : post.status === 'pending'
                    ? 'bg-amber-500 text-white'
                    : 'bg-red-500 text-white'
                }`}>
                  {post.status}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Modal - Instagram post style */}
      <AnimatePresence>
        {selectedPost && (
          <motion.div
            className="fixed inset-0 bg-black/95 flex items-center justify-center z-50 p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
          >
            <motion.div
              className="bg-white rounded-lg shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col md:flex-row"
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Media Section - Instagram style */}
              <div className="md:w-3/5 bg-black relative flex items-center justify-center">
                {selectedPost.media_urls && selectedPost.media_urls.length > 0 ? (
                  <>
                    {selectedPost.media_urls[currentMediaIndex].includes('.mp4') ||
                     selectedPost.media_urls[currentMediaIndex].includes('video') ? (
                      <video
                        src={selectedPost.media_urls[currentMediaIndex]}
                        controls
                        className="max-w-full max-h-[85vh] object-contain"
                      />
                    ) : (
                      <img
                        src={selectedPost.media_urls[currentMediaIndex]}
                        alt="Post media"
                        className="max-w-full max-h-[85vh] object-contain"
                      />
                    )}

                    {/* Media navigation */}
                    {selectedPost.media_urls.length > 1 && (
                      <>
                        {currentMediaIndex > 0 && (
                          <button
                            onClick={handlePrevMedia}
                            className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full p-2 transition-colors"
                          >
                            <ChevronLeft className="w-6 h-6 text-white" />
                          </button>
                        )}
                        {currentMediaIndex < selectedPost.media_urls.length - 1 && (
                          <button
                            onClick={handleNextMedia}
                            className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full p-2 transition-colors"
                          >
                            <ChevronRight className="w-6 h-6 text-white" />
                          </button>
                        )}

                        {/* Carousel dots */}
                        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-1.5">
                          {selectedPost.media_urls.map((_, index) => (
                            <button
                              key={index}
                              onClick={() => setCurrentMediaIndex(index)}
                              className={`w-1.5 h-1.5 rounded-full transition-all ${
                                index === currentMediaIndex
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
                  <div className="p-8 text-white text-center">
                    <p>No media available</p>
                  </div>
                )}
              </div>

              {/* Content Section - Instagram comment style */}
              <div className="md:w-2/5 flex flex-col">
                {/* Header */}
                <div className="p-4 border-b border-slate-200 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-pink-500 to-rose-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                      P
                    </div>
                    <span className="font-semibold text-sm">Penn Daily Buzz</span>
                  </div>
                  <button
                    onClick={handleClose}
                    className="text-slate-400 hover:text-slate-600 transition-colors"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                {/* Caption and details */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {/* Caption */}
                  <div className="flex gap-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-pink-500 to-rose-500 rounded-full flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                      P
                    </div>
                    <div className="flex-1">
                      <p className="text-sm">
                        <span className="font-semibold mr-2">Penn Daily Buzz</span>
                        <span className="text-slate-700 whitespace-pre-line">{selectedPost.text}</span>
                      </p>
                    </div>
                  </div>

                  {/* Hashtags */}
                  {selectedPost.hashtags && selectedPost.hashtags.length > 0 && (
                    <div className="pl-11">
                      <div className="flex flex-wrap gap-1">
                        {selectedPost.hashtags.map((tag, i) => (
                          <span
                            key={i}
                            className="text-sm text-blue-600"
                          >
                            #{tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Location */}
                  {selectedPost.location && (
                    <div className="pl-11 text-sm text-slate-600">
                      {selectedPost.location}
                    </div>
                  )}

                  {/* Music */}
                  {selectedPost.music && (
                    <div className="pl-11 text-sm text-slate-600">
                      Original audio - {selectedPost.music}
                    </div>
                  )}
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-slate-200 space-y-2">
                  <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${
                    selectedPost.status === 'published'
                      ? 'bg-green-100 text-green-700'
                      : selectedPost.status === 'pending'
                      ? 'bg-amber-100 text-amber-700'
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {selectedPost.status}
                  </div>
                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <Calendar className="w-3.5 h-3.5" />
                    {selectedPost.published_at
                      ? formatDateTime(selectedPost.published_at)
                      : formatDateTime(selectedPost.created_at)}
                  </div>
                  {selectedPost.platform_post_url && (
                    <a
                      href={selectedPost.platform_post_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-xs text-pink-600 hover:text-pink-700 font-medium"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                      View on Instagram
                    </a>
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
