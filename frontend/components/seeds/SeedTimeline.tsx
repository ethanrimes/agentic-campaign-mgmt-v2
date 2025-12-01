// frontend/components/seeds/SeedTimeline.tsx

import { formatDateTime, getStatusColor, cn } from '@/lib/utils'
import type { ContentCreationTask, CompletedPost } from '@/types'
import VerificationStatusBadge from '@/components/common/VerificationStatusBadge'

interface SeedTimelineProps {
  tasks: ContentCreationTask[]
  posts: CompletedPost[]
  loading: boolean
}

export default function SeedTimeline({ tasks, posts, loading }: SeedTimelineProps) {
  if (loading) {
    return (
      <div className="text-center py-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
      </div>
    )
  }

  if (tasks.length === 0 && posts.length === 0) {
    return (
      <div className="text-center py-6 bg-gray-50 rounded-md border border-gray-200">
        <p className="text-sm text-gray-500">No content created from this seed yet</p>
      </div>
    )
  }

  return (
    <div>
      <h4 className="text-sm font-semibold text-gray-900 mb-3">Content Timeline</h4>
      <div className="space-y-3">
        {/* Content Creation Tasks */}
        {tasks.map((task) => (
          <div key={task.id} className="flex gap-3">
            <div className="flex-shrink-0 w-2 h-2 mt-2 rounded-full bg-blue-500" />
            <div className="flex-1 pb-3 border-b border-gray-100">
              <div className="flex items-start justify-between mb-1">
                <span className="text-sm font-medium text-gray-900">Content Creation Task</span>
                <span className={cn('text-xs px-2 py-1 rounded-full', getStatusColor(task.status))}>
                  {task.status}
                </span>
              </div>
              <p className="text-xs text-gray-500 mb-2">{formatDateTime(task.created_at)}</p>
              <div className="text-xs text-gray-600 space-y-1">
                <p>Instagram: {task.instagram_image_posts} images, {task.instagram_reel_posts} reels</p>
                <p>Facebook: {task.facebook_feed_posts} feed, {task.facebook_video_posts} videos</p>
              </div>
            </div>
          </div>
        ))}

        {/* Completed Posts */}
        {posts.map((post) => (
          <div key={post.id} className="flex gap-3">
            <div className="flex-shrink-0 w-2 h-2 mt-2 rounded-full bg-green-500" />
            <div className="flex-1 pb-3 border-b border-gray-100">
              <div className="flex items-start justify-between mb-1">
                <span className="text-sm font-medium text-gray-900">
                  {post.platform === 'facebook' ? '📘' : '📷'} {post.post_type.replace(/_/g, ' ')}
                </span>
                <div className="flex items-center gap-2">
                  <VerificationStatusBadge
                    status={post.verification_status || 'unverified'}
                    postId={post.id}
                    size="sm"
                  />
                  <span className={cn('text-xs px-2 py-1 rounded-full', getStatusColor(post.status))}>
                    {post.status}
                  </span>
                </div>
              </div>
              <p className="text-xs text-gray-500 mb-2">
                Created: {formatDateTime(post.created_at)}
                {post.published_at && ` • Published: ${formatDateTime(post.published_at)}`}
              </p>
              <p className="text-sm text-gray-700 line-clamp-2">{post.text}</p>
              {post.platform_post_url && (
                <a
                  href={post.platform_post_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-primary-600 hover:text-primary-700 mt-1 inline-block"
                >
                  View on {post.platform} →
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
