// frontend/components/posts/ScheduledPostsCalendar.tsx

'use client'

import { useState, useMemo } from 'react'
import { ChevronLeft, ChevronRight, Facebook, Instagram, X, ExternalLink, Calendar as CalendarIcon, Clock, MapPin, Hash } from 'lucide-react'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, startOfWeek, endOfWeek } from 'date-fns'
import { motion, AnimatePresence } from 'framer-motion'
import type { CompletedPost } from '@/types'
import { formatDateTime } from '@/lib/utils'
import VerificationStatusBadge from '@/components/common/VerificationStatusBadge'

interface ScheduledPostsCalendarProps {
  posts: CompletedPost[]
}

export default function ScheduledPostsCalendar({ posts }: ScheduledPostsCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [selectedPost, setSelectedPost] = useState<CompletedPost | null>(null)
  const [currentMediaIndex, setCurrentMediaIndex] = useState(0)
  const [direction, setDirection] = useState(0)

  // Helper function to get the relevant date for a post
  const getPostDate = (post: CompletedPost): Date => {
    // If published, use published_at. If scheduled but not posted, use scheduled_posting_time
    if (post.published_at) {
      return new Date(post.published_at)
    }
    if (post.scheduled_posting_time) {
      return new Date(post.scheduled_posting_time)
    }
    // Fallback to created_at if neither are set
    return new Date(post.created_at)
  }

  // Group posts by date
  const postsByDate = useMemo(() => {
    const grouped: Record<string, CompletedPost[]> = {}
    posts.forEach(post => {
      const date = format(getPostDate(post), 'yyyy-MM-dd')
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

  const handlePrevMonth = () => {
    setDirection(-1)
    setCurrentDate(subMonths(currentDate, 1))
  }

  const handleNextMonth = () => {
    setDirection(1)
    setCurrentDate(addMonths(currentDate, 1))
  }

  const handleToday = () => {
    setDirection(currentDate > new Date() ? -1 : 1)
    setCurrentDate(new Date())
  }

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

  const variants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 50 : -50,
      opacity: 0
    }),
    center: {
      x: 0,
      opacity: 1
    },
    exit: (direction: number) => ({
      x: direction < 0 ? 50 : -50,
      opacity: 0
    })
  }

  return (
    <div className="space-y-6">
      {/* Calendar Header */}
      <div className="flex items-center justify-between mb-6 px-2">
        <div className="flex items-center gap-4">
          <h3 className="text-2xl font-bold text-slate-900 dark:text-white">
            {format(currentDate, 'MMMM yyyy')}
          </h3>
          <div className="flex gap-1">
            <button
              onClick={handlePrevMonth}
              className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors"
            >
              <ChevronLeft className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            </button>
            <button
              onClick={handleNextMonth}
              className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors"
            >
              <ChevronRight className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            </button>
          </div>
        </div>
        <button
          onClick={handleToday}
          className="px-4 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 dark:text-primary-400 dark:hover:bg-primary-900/20 rounded-full transition-colors"
        >
          Today
        </button>
      </div>

      {/* Calendar Grid */}
      <div className="glass-panel p-6 bg-white/60 dark:bg-slate-900/60">
        <div className="grid grid-cols-7 gap-4 mb-4">
          {weekDays.map(day => (
            <div key={day} className="text-center text-sm font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
              {day}
            </div>
          ))}
        </div>

        <AnimatePresence mode='wait' custom={direction}>
          <motion.div
            key={currentDate.toISOString()}
            custom={direction}
            variants={variants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.2 }}
            className="grid grid-cols-7 gap-2"
          >
            {calendarDays.map(day => {
              const dateKey = format(day, 'yyyy-MM-dd')
              const dayPosts = postsByDate[dateKey] || []
              const isCurrentMonth = isSameMonth(day, currentDate)
              const isToday = isSameDay(day, new Date())

              return (
                <div
                  key={dateKey}
                  className={`min-h-[120px] p-3 rounded-2xl border transition-all duration-300 ${isCurrentMonth
                      ? 'bg-white border-slate-100 shadow-sm hover:shadow-md hover:border-slate-200'
                      : 'bg-slate-50/50 border-transparent opacity-40'
                    } ${isToday ? 'ring-2 ring-primary-500 ring-offset-2 dark:ring-offset-slate-900 z-10 relative' : ''}`}
                >
                  <div className={`text-sm font-medium mb-3 ${isToday
                      ? 'text-primary-600 font-bold'
                      : 'text-slate-700'
                    }`}>
                    {format(day, 'd')}
                  </div>

                  <div className="space-y-1.5">
                    {dayPosts.map(post => (
                      <motion.div
                        key={post.id}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className={`text-xs px-2 py-1.5 rounded-lg flex items-center gap-2 cursor-pointer shadow-sm border border-transparent hover:border-slate-200 transition-colors ${post.platform === 'facebook'
                            ? 'bg-blue-50 text-blue-700'
                            : 'bg-pink-50 text-pink-700'
                          }`}
                        onClick={() => handlePostClick(post)}
                      >
                        {post.platform === 'facebook' ? (
                          <Facebook className="w-3 h-3 flex-shrink-0" />
                        ) : (
                          <Instagram className="w-3 h-3 flex-shrink-0" />
                        )}
                        <span className="truncate font-medium">
                          {post.text || 'No text'}
                        </span>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )
            })}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 pt-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
          <span className="text-sm text-slate-600 dark:text-slate-400">Facebook</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-pink-500 rounded-full"></div>
          <span className="text-sm text-slate-600 dark:text-slate-400">Instagram</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 border-2 border-primary-500 rounded-full"></div>
          <span className="text-sm text-slate-600 dark:text-slate-400">Today</span>
        </div>
      </div>

      {/* Modal for Post Details */}
      <AnimatePresence>
        {selectedPost && (
          <motion.div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
          >
            <motion.div
              className="glass-panel w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col md:flex-row shadow-2xl"
              initial={{ scale: 0.95, y: 20, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              exit={{ scale: 0.95, y: 20, opacity: 0 }}
              transition={{ type: "spring", duration: 0.5 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Media Section */}
              <div className="md:w-[60%] bg-black/95 relative flex items-center justify-center group">
                {selectedPost.media_urls && selectedPost.media_urls.length > 0 ? (
                  <>
                    {selectedPost.media_urls[currentMediaIndex].includes('.mp4') ||
                      selectedPost.media_urls[currentMediaIndex].includes('video') ? (
                      <video
                        src={selectedPost.media_urls[currentMediaIndex]}
                        controls
                        className="max-w-full max-h-[50vh] md:max-h-[80vh] object-contain"
                      />
                    ) : (
                      <img
                        src={selectedPost.media_urls[currentMediaIndex]}
                        alt="Post media"
                        className="max-w-full max-h-[50vh] md:max-h-[80vh] object-contain"
                      />
                    )}

                    {/* Media navigation */}
                    {selectedPost.media_urls.length > 1 && (
                      <>
                        <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 flex justify-between px-4 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={handlePrevMedia}
                            disabled={currentMediaIndex === 0}
                            className="bg-white/10 hover:bg-white/20 text-white p-2 rounded-full backdrop-blur-md disabled:opacity-30 transition-all"
                          >
                            <ChevronLeft className="w-6 h-6" />
                          </button>
                          <button
                            onClick={handleNextMedia}
                            disabled={currentMediaIndex === selectedPost.media_urls.length - 1}
                            className="bg-white/10 hover:bg-white/20 text-white p-2 rounded-full backdrop-blur-md disabled:opacity-30 transition-all"
                          >
                            <ChevronRight className="w-6 h-6" />
                          </button>
                        </div>

                        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
                          {selectedPost.media_urls.map((_, idx) => (
                            <div
                              key={idx}
                              className={`w-1.5 h-1.5 rounded-full transition-all ${idx === currentMediaIndex ? 'bg-white w-2.5' : 'bg-white/40'
                                }`}
                            />
                          ))}
                        </div>
                      </>
                    )}
                  </>
                ) : (
                  <div className="p-8 text-white/50 text-center flex flex-col items-center">
                    <CalendarIcon className="w-12 h-12 mb-3 opacity-50" />
                    <p>No media content</p>
                  </div>
                )}
              </div>

              {/* Content Section */}
              <div className="md:w-[40%] flex flex-col bg-white dark:bg-slate-900">
                <div className="p-5 border-b border-slate-100 dark:border-slate-800 flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2.5 rounded-xl ${selectedPost.platform === 'facebook'
                        ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
                        : 'bg-pink-50 text-pink-600 dark:bg-pink-900/20 dark:text-pink-400'
                      }`}>
                      {selectedPost.platform === 'facebook' ? <Facebook className="w-5 h-5" /> : <Instagram className="w-5 h-5" />}
                    </div>
                    <div>
                      <h3 className="font-bold text-slate-900 dark:text-white text-sm">
                        {selectedPost.platform === 'facebook' ? 'Facebook Post' : 'Instagram Post'}
                      </h3>
                      <div className={`text-xs font-medium px-2 py-0.5 rounded-full inline-block mt-1 ${selectedPost.status === 'published' ? 'bg-green-100 text-green-700' :
                          selectedPost.status === 'pending' ? 'bg-amber-100 text-amber-700' :
                            'bg-red-100 text-red-700'
                        }`}>
                        {selectedPost.status}
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

                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                  <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Caption</h4>
                    <p className="text-slate-700 dark:text-slate-300 whitespace-pre-line leading-relaxed text-sm">
                      {selectedPost.text}
                    </p>
                  </div>

                  {selectedPost.hashtags && selectedPost.hashtags.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                        <Hash className="w-3 h-3" /> Hashtags
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedPost.hashtags.map((tag, i) => (
                          <span
                            key={i}
                            className="text-xs bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 px-2.5 py-1 rounded-full"
                          >
                            #{tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4">
                    {selectedPost.location && (
                      <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl">
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1">
                          <MapPin className="w-3 h-3" /> Location
                        </h4>
                        <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                          {selectedPost.location}
                        </p>
                      </div>
                    )}
                    <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1">
                        <Clock className="w-3 h-3" /> Scheduled
                      </h4>
                      <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                        {formatDateTime(selectedPost.scheduled_posting_time || selectedPost.created_at)}
                      </p>
                    </div>
                  </div>

                  <div className="pt-2">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Verification</h4>
                    <VerificationStatusBadge
                      status={selectedPost.verification_status || 'unverified'}
                      postId={selectedPost.id}
                      size="md"
                    />
                  </div>
                </div>

                {selectedPost.platform_post_url && (
                  <div className="p-5 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
                    <a
                      href={selectedPost.platform_post_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-center gap-2 w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-primary-500 text-slate-700 dark:text-slate-300 hover:text-primary-600 dark:hover:text-primary-400 py-2.5 rounded-xl font-medium transition-all shadow-sm hover:shadow-md"
                    >
                      <ExternalLink className="w-4 h-4" />
                      View Live Post
                    </a>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

