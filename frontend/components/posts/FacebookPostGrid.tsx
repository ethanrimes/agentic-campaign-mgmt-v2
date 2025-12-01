// frontend/components/posts/FacebookPostGrid.tsx

'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, ChevronLeft, ChevronRight, Calendar, ExternalLink, Sparkles } from 'lucide-react'
import type { CompletedPost } from '@/types'
import { formatDateTime } from '@/lib/utils'
import Image from 'next/image'
import Link from 'next/link'
import VerificationStatusBadge from '@/components/common/VerificationStatusBadge'

interface FacebookPostGridProps {
  posts: CompletedPost[]
}

export default function FacebookPostGrid({ posts }: FacebookPostGridProps) {
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
      {/* Grid View */}
      <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
        {posts.map((post) => {
          const previewMedia = post.media_urls && post.media_urls.length > 0 ? post.media_urls[0] : null
          const isVideo = previewMedia && (previewMedia.includes('.mp4') || previewMedia.includes('video'))

          return (
            <div
              key={post.id}
              className="relative aspect-square bg-slate-100 rounded-lg overflow-hidden cursor-pointer group hover:opacity-90 transition-opacity"
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
                      className="w-full h-full object-cover"
                    />
                  )}
                </>
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-blue-100 p-4">
                  <p className="text-xs text-slate-600 line-clamp-6 text-center">
                    {post.text}
                  </p>
                </div>
              )}
              {/* Media count badge */}
              {post.media_urls && post.media_urls.length > 1 && (
                <div className="absolute top-2 right-2 bg-slate-900/80 text-white text-xs px-2 py-1 rounded-full">
                  {post.media_urls.length}
                </div>
              )}
              {/* Status indicator */}
              <div className="absolute bottom-2 left-2">
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                  post.status === 'published'
                    ? 'bg-green-500/90 text-white'
                    : post.status === 'pending'
                    ? 'bg-amber-500/90 text-white'
                    : 'bg-red-500/90 text-white'
                }`}>
                  {post.status}
                </span>
              </div>
              {/* Verification status indicator */}
              <div className="absolute bottom-2 right-2">
                <VerificationStatusBadge
                  status={post.verification_status || 'unverified'}
                  postId={post.id}
                  size="sm"
                />
              </div>
            </div>
          )
        })}
      </div>

      {/* Modal */}
      <AnimatePresence>
        {selectedPost && (
          <motion.div
            className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
          >
            <motion.div
              className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col md:flex-row"
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Media Section */}
              <div className="md:w-2/3 bg-black relative flex items-center justify-center">
                {selectedPost.media_urls && selectedPost.media_urls.length > 0 ? (
                  <>
                    {selectedPost.media_urls[currentMediaIndex].includes('.mp4') ||
                     selectedPost.media_urls[currentMediaIndex].includes('video') ? (
                      <video
                        src={selectedPost.media_urls[currentMediaIndex]}
                        controls
                        className="max-w-full max-h-[60vh] object-contain"
                      />
                    ) : (
                      <img
                        src={selectedPost.media_urls[currentMediaIndex]}
                        alt="Post media"
                        className="max-w-full max-h-[60vh] object-contain"
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
                        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-white text-sm bg-black/50 px-3 py-1 rounded-full">
                          {currentMediaIndex + 1} / {selectedPost.media_urls.length}
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

              {/* Content Section */}
              <div className="md:w-1/3 p-6 overflow-y-auto">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap mb-3">
                      <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${
                        selectedPost.status === 'published'
                          ? 'bg-green-100 text-green-700'
                          : selectedPost.status === 'pending'
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-red-100 text-red-700'
                      }`}>
                        {selectedPost.status}
                      </div>
                      <VerificationStatusBadge
                        status={selectedPost.verification_status || 'unverified'}
                        postId={selectedPost.id}
                        size="md"
                      />
                    </div>
                  </div>
                  <button
                    onClick={handleClose}
                    className="text-slate-400 hover:text-slate-600 transition-colors"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                {/* Post Text */}
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-slate-900 mb-2">Caption</h3>
                  <p className="text-slate-700 whitespace-pre-line leading-relaxed">
                    {selectedPost.text}
                  </p>
                </div>

                {/* Hashtags */}
                {selectedPost.hashtags && selectedPost.hashtags.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-sm font-semibold text-slate-900 mb-2">Hashtags</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedPost.hashtags.map((tag, i) => (
                        <span
                          key={i}
                          className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded-full"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Location */}
                {selectedPost.location && (
                  <div className="mb-6">
                    <h3 className="text-sm font-semibold text-slate-900 mb-2">Location</h3>
                    <p className="text-slate-600 text-sm">{selectedPost.location}</p>
                  </div>
                )}

                {/* Published Info */}
                <div className="pt-4 border-t border-slate-200 space-y-3">
                  <div className="flex items-center gap-2 text-sm">
                    <Calendar className="w-4 h-4 text-slate-400" />
                    <span className="text-slate-600">
                      {selectedPost.published_at
                        ? formatDateTime(selectedPost.published_at)
                        : formatDateTime(selectedPost.created_at)}
                    </span>
                  </div>
                  {selectedPost.platform_post_url && (
                    <a
                      href={selectedPost.platform_post_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                      <ExternalLink className="w-4 h-4" />
                      View on Facebook
                    </a>
                  )}
                  {/* Content Seed Link */}
                  {(selectedPost as any).content_seed_id && (
                    <Link
                      href={`/content-seeds?seed=${(selectedPost as any).content_seed_id}&type=${(selectedPost as any).content_seed_type}`}
                      className="block p-3 bg-gradient-to-br from-cyan-50 to-blue-50 rounded-lg border border-cyan-200 hover:border-cyan-300 hover:shadow-md transition-all"
                      onClick={handleClose}
                    >
                      <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 mb-1">
                        <Sparkles className="w-3.5 h-3.5 text-cyan-600" />
                        Content Seed
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <span className="text-xs bg-white text-cyan-700 px-2 py-1 rounded border border-cyan-200 inline-block mb-1">
                            {(selectedPost as any).content_seed_type?.replace(/_/g, ' ') || 'Unknown'}
                          </span>
                          {(selectedPost as any).seed_name && (
                            <p className="text-xs text-slate-700 line-clamp-1">
                              {(selectedPost as any).seed_name}
                            </p>
                          )}
                        </div>
                        <ExternalLink className="w-3.5 h-3.5 text-cyan-600 flex-shrink-0" />
                      </div>
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
