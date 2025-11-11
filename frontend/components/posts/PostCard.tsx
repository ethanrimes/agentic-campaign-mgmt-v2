// frontend/components/posts/PostCard.tsx

'use client'

import ExpandableCard from '@/components/common/ExpandableCard'
import { formatDateTime, formatRelativeTime, getStatusColor, getPlatformIcon, cn } from '@/lib/utils'
import { ExternalLink, Image as ImageIcon, Film } from 'lucide-react'
import type { CompletedPost } from '@/types'
import Image from 'next/image'

interface PostCardProps {
  post: CompletedPost
}

export default function PostCard({ post }: PostCardProps) {
  const preview = (
    <div className="space-y-2">
      <p className="text-sm line-clamp-3">{post.text}</p>
      <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500">
        <span>{post.post_type.replace(/_/g, ' ')}</span>
        {post.media_urls.length > 0 && (
          <span className="flex items-center gap-1">
            {post.media_urls[0].includes('video') ? (
              <Film className="w-3 h-3" />
            ) : (
              <ImageIcon className="w-3 h-3" />
            )}
            {post.media_urls.length} media
          </span>
        )}
        {post.hashtags.length > 0 && <span>{post.hashtags.length} hashtags</span>}
      </div>
    </div>
  )

  return (
    <ExpandableCard
      title={`${getPlatformIcon(post.platform)} ${post.post_type.replace(/_/g, ' ')}`}
      subtitle={formatRelativeTime(post.created_at)}
      preview={preview}
      badge={
        <span className={cn('text-xs px-2 py-1 rounded-full', getStatusColor(post.status))}>
          {post.status}
        </span>
      }
    >
      <div className="space-y-6">
        {/* Full Text */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Caption</h4>
          <p className="text-gray-700 whitespace-pre-line">{post.text}</p>
        </div>

        {/* Media */}
        {post.media_urls.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3">
              Media ({post.media_urls.length})
            </h4>
            <div className="grid grid-cols-2 gap-4">
              {post.media_urls.map((url, i) => (
                <a
                  key={i}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="relative aspect-square bg-gray-100 rounded-md overflow-hidden hover:opacity-90 transition-opacity"
                >
                  {url.includes('video') ? (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Film className="w-12 h-12 text-gray-400" />
                    </div>
                  ) : (
                    <Image
                      src={url}
                      alt={`Media ${i + 1}`}
                      fill
                      className="object-cover"
                    />
                  )}
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Hashtags */}
        {post.hashtags.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-2">Hashtags</h4>
            <div className="flex flex-wrap gap-2">
              {post.hashtags.map((tag, i) => (
                <span key={i} className="text-sm text-gray-600">
                  #{tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Metadata */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
          <div>
            <h4 className="text-xs font-semibold text-gray-500 mb-1">Created</h4>
            <p className="text-sm text-gray-900">{formatDateTime(post.created_at)}</p>
          </div>
          {post.published_at && (
            <div>
              <h4 className="text-xs font-semibold text-gray-500 mb-1">Published</h4>
              <p className="text-sm text-gray-900">{formatDateTime(post.published_at)}</p>
            </div>
          )}
          {post.location && (
            <div>
              <h4 className="text-xs font-semibold text-gray-500 mb-1">Location</h4>
              <p className="text-sm text-gray-900">{post.location}</p>
            </div>
          )}
          {post.platform_post_url && (
            <div>
              <h4 className="text-xs font-semibold text-gray-500 mb-1">Link</h4>
              <a
                href={post.platform_post_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
              >
                View on {post.platform} <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          )}
        </div>

        {/* Error Message */}
        {post.error_message && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <h4 className="text-sm font-semibold text-red-900 mb-1">Error</h4>
            <p className="text-sm text-red-700">{post.error_message}</p>
          </div>
        )}

        {/* Content Seed Info */}
        <div className="pt-4 border-t border-gray-100">
          <h4 className="text-xs font-semibold text-gray-500 mb-2">Content Seed</h4>
          <div className="flex items-center gap-2">
            <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-full">
              {post.content_seed_type.replace(/_/g, ' ')}
            </span>
            <span className="text-xs text-gray-500">ID: {post.content_seed_id.slice(0, 8)}...</span>
          </div>
        </div>
      </div>
    </ExpandableCard>
  )
}
