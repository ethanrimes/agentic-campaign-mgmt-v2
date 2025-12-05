// frontend/app/scheduled-posts/page.tsx

'use client'

import { useState, useEffect } from 'react'
import { getCompletedPosts } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'
import { Calendar, Instagram } from 'lucide-react'
import ScheduledPostsCalendar from '@/components/posts/ScheduledPostsCalendar'
import ExpandableFacebookPosts from '@/components/posts/ExpandableFacebookPosts'
import InstagramPostGrid from '@/components/posts/InstagramPostGrid'
import { CompletedPost } from '@/types'

// Helper function to get the relevant date for a post
function getPostDate(post: CompletedPost): Date {
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

// Helper function to format date as YYYY-MM-DD
function formatDateKey(date: Date): string {
  return date.toISOString().split('T')[0]
}

// Helper function to format date for display
function formatDateDisplay(dateStr: string): string {
  const date = new Date(dateStr)
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)

  const dateKey = formatDateKey(date)
  const todayKey = formatDateKey(today)
  const tomorrowKey = formatDateKey(tomorrow)

  if (dateKey === todayKey) return 'Today'
  if (dateKey === tomorrowKey) return 'Tomorrow'

  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined
  })
}

// Group posts by date
interface PostsByDate {
  [dateKey: string]: {
    date: Date
    facebook: CompletedPost[]
    instagram: CompletedPost[]
  }
}

export default function ScheduledPostsPage() {
  const { selectedAsset } = useBusinessAsset()
  const [posts, setPosts] = useState<CompletedPost[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadPosts() {
      if (!selectedAsset) return

      try {
        setLoading(true)
        const data = await getCompletedPosts(selectedAsset.id)
        setPosts(data)
      } catch (error) {
        console.error('Failed to load posts:', error)
      } finally {
        setLoading(false)
      }
    }

    loadPosts()
  }, [selectedAsset])

  if (!selectedAsset || loading) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="text-center py-16">
          <Calendar className="w-16 h-16 text-cyan-400 mx-auto mb-4 animate-pulse" />
          <p className="text-lg text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // Separate posts by platform for counts
  const facebookPosts = posts.filter(p => p.platform === 'facebook')
  const instagramPosts = posts.filter(p => p.platform === 'instagram')

  // Group posts by date, then by platform
  const postsByDate: PostsByDate = {}

  posts.forEach(post => {
    const date = getPostDate(post)
    const dateKey = formatDateKey(date)

    if (!postsByDate[dateKey]) {
      postsByDate[dateKey] = {
        date,
        facebook: [],
        instagram: []
      }
    }

    if (post.platform === 'facebook') {
      postsByDate[dateKey].facebook.push(post)
    } else {
      postsByDate[dateKey].instagram.push(post)
    }
  })

  // Sort dates (newest first for past posts, earliest first for future posts)
  const now = new Date()
  const sortedDateKeys = Object.keys(postsByDate).sort((a, b) => {
    const dateA = postsByDate[a].date
    const dateB = postsByDate[b].date

    // If both dates are in the future, sort ascending (earliest first)
    if (dateA >= now && dateB >= now) {
      return dateA.getTime() - dateB.getTime()
    }
    // If both dates are in the past, sort descending (most recent first)
    if (dateA < now && dateB < now) {
      return dateB.getTime() - dateA.getTime()
    }
    // If one is future and one is past, future comes first
    return dateA >= now ? -1 : 1
  })

  return (
    <div className="max-w-7xl mx-auto animate-fade-in pt-20">
      {/* Header */}
      <div className="relative mb-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-100/30 via-blue-100/20 to-slate-100/30 rounded-3xl blur-3xl"></div>
        <div className="relative bg-white rounded-2xl p-8 border border-slate-200 shadow-xl">
          <div className="flex items-center gap-4 mb-3">
            <div className="relative">
              <div className="w-12 h-12 bg-gradient-to-br from-cyan-600 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
                <Calendar className="w-6 h-6 text-white" />
              </div>
              <div className="absolute inset-0 bg-cyan-500 rounded-2xl blur-xl opacity-30"></div>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">
                Scheduled Posts
              </h1>
              <p className="text-sm text-slate-600 mt-1">
                View all created and published posts across platforms
              </p>
            </div>
          </div>
          <div className="mt-6 flex items-center gap-3 flex-wrap">
            <div className="bg-slate-100 px-4 py-2 rounded-full border border-slate-200">
              <span className="text-sm font-bold text-slate-900">{posts.length}</span>
              <span className="text-sm text-slate-600 ml-1">total posts</span>
            </div>
            <div className="bg-blue-50 px-4 py-2 rounded-full border border-blue-200">
              <span className="text-sm font-bold text-blue-900">{facebookPosts.length}</span>
              <span className="text-sm text-blue-700 ml-1">Facebook</span>
            </div>
            <div className="bg-pink-50 px-4 py-2 rounded-full border border-pink-200">
              <span className="text-sm font-bold text-pink-900">{instagramPosts.length}</span>
              <span className="text-sm text-pink-700 ml-1">Instagram</span>
            </div>
          </div>
        </div>
      </div>

      {posts.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-slate-200 shadow-xl">
          <div className="relative inline-block mb-6">
            <Calendar className="w-16 h-16 text-slate-400 mx-auto" />
            <div className="absolute inset-0 bg-slate-500 blur-2xl opacity-20"></div>
          </div>
          <p className="text-lg font-semibold text-slate-900 mb-2">No scheduled posts found</p>
          <p className="text-sm text-slate-600 max-w-md mx-auto">
            Run the content creator agent to generate and schedule posts
          </p>
        </div>
      ) : (
        <div className="space-y-12">
          {/* Calendar View */}
          <section className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xl">
            <h2 className="text-2xl font-bold text-slate-900 mb-6">Calendar View</h2>
            <ScheduledPostsCalendar posts={posts} />
          </section>

          {/* List View Header */}
          <section className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xl">
            <h2 className="text-2xl font-bold text-slate-900">List View</h2>
            <p className="text-slate-600 mt-1">Posts organized by date</p>
          </section>

          {/* Posts organized by date */}
          <div className="space-y-8">
            {sortedDateKeys.map(dateKey => {
              const dayData = postsByDate[dateKey]
              const hasFacebook = dayData.facebook.length > 0
              const hasInstagram = dayData.instagram.length > 0

              return (
                <div key={dateKey} className="space-y-6">
                  {/* Date Header */}
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-100/30 via-blue-100/20 to-slate-100/30 rounded-2xl blur-2xl"></div>
                    <div className="relative bg-white rounded-xl p-4 border border-slate-200 shadow-lg">
                      <h3 className="text-xl font-bold text-slate-900">
                        {formatDateDisplay(dateKey)}
                      </h3>
                      <p className="text-sm text-slate-600 mt-1">
                        {dayData.date.toLocaleDateString('en-US', {
                          month: 'long',
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </p>
                      <div className="flex items-center gap-3 mt-3">
                        {hasFacebook && (
                          <div className="bg-blue-50 px-3 py-1 rounded-full border border-blue-200">
                            <span className="text-xs font-bold text-blue-900">{dayData.facebook.length}</span>
                            <span className="text-xs text-blue-700 ml-1">Facebook</span>
                          </div>
                        )}
                        {hasInstagram && (
                          <div className="bg-pink-50 px-3 py-1 rounded-full border border-pink-200">
                            <span className="text-xs font-bold text-pink-900">{dayData.instagram.length}</span>
                            <span className="text-xs text-pink-700 ml-1">Instagram</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Facebook Posts for this day */}
                  {hasFacebook && (
                    <ExpandableFacebookPosts posts={dayData.facebook} />
                  )}

                  {/* Instagram Posts for this day */}
                  {hasInstagram && (
                    <section>
                      <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 bg-gradient-to-br from-pink-600 to-rose-600 rounded-xl flex items-center justify-center shadow-lg">
                          <Instagram className="w-5 h-5 text-white" />
                        </div>
                        <h2 className="text-2xl font-bold text-slate-900">Instagram Posts</h2>
                        <span className="text-sm bg-pink-100 text-pink-700 px-3 py-1 rounded-full font-medium">
                          {dayData.instagram.length}
                        </span>
                      </div>
                      <InstagramPostGrid posts={dayData.instagram} />
                    </section>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
