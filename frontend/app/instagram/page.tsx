// frontend/app/instagram/page.tsx

import { getCompletedPosts } from '@/lib/api'
import PostCard from '@/components/posts/PostCard'
import { Instagram } from 'lucide-react'

export const dynamic = 'force-dynamic'

export default async function InstagramPage() {
  const posts = await getCompletedPosts('instagram')

  const statusCounts = {
    published: posts.filter(p => p.status === 'published').length,
    pending: posts.filter(p => p.status === 'pending').length,
    failed: posts.filter(p => p.status === 'failed').length,
  }

  return (
    <div className="max-w-6xl mx-auto animate-fade-in">
      <div className="relative mb-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-pink-100/50 via-rose-100/30 to-pink-100/50 rounded-3xl blur-3xl"></div>
        <div className="relative glass rounded-2xl p-8 border border-white/50 shadow-soft">
          <div className="flex items-center gap-4 mb-3">
            <div className="relative">
              <div className="w-14 h-14 bg-gradient-to-br from-pink-600 to-rose-600 rounded-2xl flex items-center justify-center shadow-lg">
                <Instagram className="w-7 h-7 text-white" />
              </div>
              <div className="absolute inset-0 bg-pink-600 rounded-2xl blur-xl opacity-30"></div>
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
                Instagram Posts
              </h1>
              <p className="text-gray-600 mt-1">
                All Instagram content sorted by most recent first
              </p>
            </div>
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <div className="glass px-4 py-2 rounded-full border border-white/30">
              <span className="text-sm font-bold text-gray-900">{posts.length}</span>
              <span className="text-sm text-gray-600 ml-1">total posts</span>
            </div>
            <div className="glass px-3 py-2 rounded-full border border-white/30 text-sm">
              <span className="text-green-600 font-medium">✓ {statusCounts.published}</span>
              <span className="text-gray-500 ml-1">published</span>
            </div>
            <div className="glass px-3 py-2 rounded-full border border-white/30 text-sm">
              <span className="text-amber-600 font-medium">⏳ {statusCounts.pending}</span>
              <span className="text-gray-500 ml-1">pending</span>
            </div>
            {statusCounts.failed > 0 && (
              <div className="glass px-3 py-2 rounded-full border border-red-200 text-sm">
                <span className="text-red-600 font-medium">✗ {statusCounts.failed}</span>
                <span className="text-gray-500 ml-1">failed</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {posts.length === 0 ? (
        <div className="text-center py-16 glass rounded-2xl border border-white/50 shadow-soft">
          <div className="relative inline-block mb-6">
            <Instagram className="w-16 h-16 text-pink-400 mx-auto" />
            <div className="absolute inset-0 bg-pink-500 blur-2xl opacity-20"></div>
          </div>
          <p className="text-lg font-semibold text-gray-900 mb-2">No Instagram posts found</p>
          <p className="text-sm text-gray-600 max-w-md mx-auto">
            Content will appear here after the content creation agent runs
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {posts.map((post, index) => (
            <div key={post.id} className="animate-slide-up" style={{ animationDelay: `${index * 50}ms` }}>
              <PostCard post={post} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
