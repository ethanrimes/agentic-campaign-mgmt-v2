// frontend/app/scheduled-posts/page.tsx

import { getCompletedPosts } from '@/lib/api'
import { Calendar } from 'lucide-react'
import ScheduledPostsCalendar from '@/components/posts/ScheduledPostsCalendar'
import ExpandableFacebookPosts from '@/components/posts/ExpandableFacebookPosts'
import InstagramPostGrid from '@/components/posts/InstagramPostGrid'

export const dynamic = 'force-dynamic'

export default async function ScheduledPostsPage() {
  const posts = await getCompletedPosts()

  // Separate posts by platform
  const facebookPosts = posts.filter(p => p.platform === 'facebook')
  const instagramPosts = posts.filter(p => p.platform === 'instagram')

  // Sort by schedule/publish date
  const sortedPosts = [...posts].sort((a, b) => {
    const dateA = new Date(a.published_at || a.created_at).getTime()
    const dateB = new Date(b.published_at || b.created_at).getTime()
    return dateB - dateA
  })

  return (
    <div className="max-w-7xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="relative mb-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-100/30 via-blue-100/20 to-slate-100/30 rounded-3xl blur-3xl"></div>
        <div className="relative bg-white rounded-2xl p-8 border border-slate-200 shadow-xl">
          <div className="flex items-center gap-4 mb-3">
            <div className="relative">
              <div className="w-14 h-14 bg-gradient-to-br from-cyan-600 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
                <Calendar className="w-7 h-7 text-white" />
              </div>
              <div className="absolute inset-0 bg-cyan-500 rounded-2xl blur-xl opacity-30"></div>
            </div>
            <div>
              <h1 className="text-4xl font-bold text-slate-900">
                Scheduled Posts
              </h1>
              <p className="text-slate-600 mt-1">
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

          {/* Facebook Posts - Expandable */}
          {facebookPosts.length > 0 && (
            <ExpandableFacebookPosts posts={facebookPosts} />
          )}

          {/* Instagram Posts - Grid */}
          {instagramPosts.length > 0 && (
            <section>
              <InstagramPostGrid posts={instagramPosts} />
            </section>
          )}
        </div>
      )}
    </div>
  )
}
