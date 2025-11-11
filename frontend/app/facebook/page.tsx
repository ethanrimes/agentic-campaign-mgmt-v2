// frontend/app/facebook/page.tsx

import { getCompletedPosts } from '@/lib/api'
import PostCard from '@/components/posts/PostCard'
import { Facebook } from 'lucide-react'

export const dynamic = 'force-dynamic'

export default async function FacebookPage() {
  const posts = await getCompletedPosts('facebook')

  const statusCounts = {
    published: posts.filter(p => p.status === 'published').length,
    pending: posts.filter(p => p.status === 'pending').length,
    failed: posts.filter(p => p.status === 'failed').length,
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Facebook className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Facebook Posts</h1>
        </div>
        <p className="text-gray-600">
          All Facebook content sorted by most recent first
        </p>
        <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
          <span className="font-medium">{posts.length} total posts</span>
          <span>✅ {statusCounts.published} published</span>
          <span>⏳ {statusCounts.pending} pending</span>
          {statusCounts.failed > 0 && <span>❌ {statusCounts.failed} failed</span>}
        </div>
      </div>

      {posts.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <Facebook className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No Facebook posts found</p>
          <p className="text-sm text-gray-500 mt-2">
            Content will appear here after the content creation agent runs
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  )
}
