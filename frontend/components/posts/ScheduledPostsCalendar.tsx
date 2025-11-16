// frontend/components/posts/ScheduledPostsCalendar.tsx

'use client'

import { useState, useMemo } from 'react'
import { ChevronLeft, ChevronRight, Facebook, Instagram, X, ExternalLink, Calendar as CalendarIcon } from 'lucide-react'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, startOfWeek, endOfWeek } from 'date-fns'
import { motion, AnimatePresence } from 'framer-motion'
import type { CompletedPost } from '@/types'
import { formatDateTime } from '@/lib/utils'

interface ScheduledPostsCalendarProps {
  posts: CompletedPost[]
}

export default function ScheduledPostsCalendar({ posts }: ScheduledPostsCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [selectedPost, setSelectedPost] = useState<CompletedPost | null>(null)
  const [currentMediaIndex, setCurrentMediaIndex] = useState(0)

  // Group posts by date
  const postsByDate = useMemo(() => {
    const grouped: Record<string, CompletedPost[]> = {}
    posts.forEach(post => {
      const date = format(new Date(post.published_at || post.created_at), 'yyyy-MM-dd')
      if (!grouped[date]) {
        grouped[date] = []
      }
      grouped[date].push(post)
    })
    return grouped
  }, [posts])

  // Get calendar days
  const monthStart = startOfMonth(currentDate)
  const monthEnd = endOfMonth(currentDate)
  const calendarStart = startOfWeek(monthStart)
  const calendarEnd = endOfWeek(monthEnd)
  const calendarDays = eachDayOfInterval({ start: calendarStart, end: calendarEnd })

  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

  const handlePrevMonth = () => setCurrentDate(subMonths(currentDate, 1))
  const handleNextMonth = () => setCurrentDate(addMonths(currentDate, 1))
  const handleToday = () => setCurrentDate(new Date())

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
    <div className="space-y-4">
      {/* Calendar Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-slate-900">
          {format(currentDate, 'MMMM yyyy')}
        </h3>
        <div className="flex items-center gap-2">
          <button
            onClick={handleToday}
            className="px-3 py-1 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
          >
            Today
          </button>
          <button
            onClick={handlePrevMonth}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-slate-600" />
          </button>
          <button
            onClick={handleNextMonth}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <ChevronRight className="w-5 h-5 text-slate-600" />
          </button>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-2">
        {/* Week day headers */}
        {weekDays.map(day => (
          <div key={day} className="text-center text-sm font-semibold text-slate-600 py-2">
            {day}
          </div>
        ))}

        {/* Calendar days */}
        {calendarDays.map(day => {
          const dateKey = format(day, 'yyyy-MM-dd')
          const dayPosts = postsByDate[dateKey] || []
          const isCurrentMonth = isSameMonth(day, currentDate)
          const isToday = isSameDay(day, new Date())

          return (
            <div
              key={dateKey}
              className={`min-h-[100px] p-2 rounded-lg border transition-all ${
                isCurrentMonth
                  ? 'bg-white border-slate-200'
                  : 'bg-slate-50 border-slate-100'
              } ${isToday ? 'ring-2 ring-cyan-500' : ''}`}
            >
              <div className={`text-sm font-medium mb-2 ${
                isCurrentMonth ? 'text-slate-900' : 'text-slate-400'
              } ${isToday ? 'text-cyan-600 font-bold' : ''}`}>
                {format(day, 'd')}
              </div>
              <div className="space-y-1">
                {dayPosts.map(post => (
                  <div
                    key={post.id}
                    className={`text-xs px-2 py-1 rounded flex items-center gap-1 cursor-pointer transition-all hover:shadow-md ${
                      post.platform === 'facebook'
                        ? 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                        : 'bg-pink-100 text-pink-700 hover:bg-pink-200'
                    }`}
                    title={post.text.substring(0, 100)}
                    onClick={() => handlePostClick(post)}
                  >
                    {post.platform === 'facebook' ? (
                      <Facebook className="w-3 h-3 flex-shrink-0" />
                    ) : (
                      <Instagram className="w-3 h-3 flex-shrink-0" />
                    )}
                    <span className="truncate flex-1">
                      {post.text.substring(0, 20)}...
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 pt-4 border-t border-slate-200">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-100 rounded"></div>
          <span className="text-sm text-slate-600">Facebook</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-pink-100 rounded"></div>
          <span className="text-sm text-slate-600">Instagram</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-cyan-500 rounded"></div>
          <span className="text-sm text-slate-600">Today</span>
        </div>
      </div>

      {/* Modal for Post Details */}
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
                    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium mb-3 ${
                      selectedPost.status === 'published'
                        ? 'bg-green-100 text-green-700'
                        : selectedPost.status === 'pending'
                        ? 'bg-amber-100 text-amber-700'
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {selectedPost.platform === 'facebook' ? (
                        <Facebook className="w-3 h-3" />
                      ) : (
                        <Instagram className="w-3 h-3" />
                      )}
                      {selectedPost.status}
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
                  <p className="text-slate-700 whitespace-pre-line leading-relaxed text-sm">
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
                    <CalendarIcon className="w-4 h-4 text-slate-400" />
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
                      View on {selectedPost.platform}
                    </a>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
