// frontend/components/posts/PostCard.tsx

'use client'

import ExpandableCard from '@/components/common/ExpandableCard'
import { formatDateTime, formatRelativeTime, getStatusColor, getPlatformIcon, cn } from '@/lib/utils'
import { ExternalLink, Image as ImageIcon, Film, Sparkles, ShieldCheck, ShieldX, ShieldAlert } from 'lucide-react'
import type { CompletedPost } from '@/types'
import Image from 'next/image'
import Link from 'next/link'

interface PostCardProps {
  post: CompletedPost
}

export default function PostCard({ post }: PostCardProps) {
  const mediaUrls = post.media_urls || []
  const hashtags = post.hashtags || []

  const verificationStatusBadge = () => {
    const status = (post as any).verification_status || 'unverified'
    switch (status) {
      case 'verified':
        return (
          <span className="flex items-center gap-1.5 bg-green-50 text-green-700 px-3 py-1.5 rounded-full font-medium border border-green-100">
            <ShieldCheck className="w-3.5 h-3.5" />
            Verified
          </span>
        )
      case 'rejected':
        return (
          <span className="flex items-center gap-1.5 bg-red-50 text-red-700 px-3 py-1.5 rounded-full font-medium border border-red-100">
            <ShieldX className="w-3.5 h-3.5" />
            Rejected
          </span>
        )
      default:
        return (
          <span className="flex items-center gap-1.5 bg-amber-50 text-amber-700 px-3 py-1.5 rounded-full font-medium border border-amber-100">
            <ShieldAlert className="w-3.5 h-3.5" />
            Unverified
          </span>
        )
    }
  }

  const preview = (
    <div className="space-y-3">
      <p className="text-sm line-clamp-3 text-gray-700 leading-relaxed">{post.text}</p>
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="bg-gradient-to-r from-blue-50 to-purple-50 text-blue-700 px-3 py-1.5 rounded-full font-medium border border-blue-100">
          {post.post_type.replace(/_/g, ' ')}
        </span>
        {verificationStatusBadge()}
        {mediaUrls.length > 0 && (
          <span className="flex items-center gap-1.5 bg-purple-50 text-purple-700 px-3 py-1.5 rounded-full font-medium border border-purple-100">
            {mediaUrls[0].includes('video') ? (
              <Film className="w-3.5 h-3.5" />
            ) : (
              <ImageIcon className="w-3.5 h-3.5" />
            )}
            {mediaUrls.length} media
          </span>
        )}
        {hashtags.length > 0 && (
          <span className="bg-pink-50 text-pink-700 px-3 py-1.5 rounded-full font-medium border border-pink-100">
            {hashtags.length} hashtags
          </span>
        )}
      </div>
    </div>
  )

  const statusColors = {
    published: 'bg-success-50 text-success-700 border border-success-200',
    pending: 'bg-amber-50 text-amber-700 border border-amber-200',
    failed: 'bg-red-50 text-red-700 border border-red-200',
  }

  return (
    <ExpandableCard
      title={`${getPlatformIcon(post.platform)} ${post.post_type.replace(/_/g, ' ')}`}
      subtitle={formatRelativeTime(post.created_at)}
      preview={preview}
      badge={
        <span className={cn('text-xs px-3 py-1.5 rounded-full font-medium', statusColors[post.status])}>
          {post.status}
        </span>
      }
    >
      <div className="space-y-6">
        {/* Full Text */}
        <div className="p-4 bg-gradient-to-br from-blue-50/50 to-purple-50/50 rounded-xl border border-blue-100/50">
          <h4 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
            <div className="w-1 h-4 bg-gradient-to-b from-blue-500 to-purple-500 rounded-full"></div>
            Caption
          </h4>
          <p className="text-gray-700 leading-relaxed whitespace-pre-line">{post.text}</p>
        </div>

        {/* Media */}
        {mediaUrls.length > 0 && (
          <div>
            <h4 className="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center text-white text-xs font-bold">
                {mediaUrls.length}
              </div>
              Media Gallery
            </h4>
            <div className={cn(
              "grid gap-4",
              mediaUrls.length === 1 ? "grid-cols-1" : "grid-cols-2"
            )}>
              {mediaUrls.map((url, i) => (
                <a
                  key={i}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group relative aspect-square bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl overflow-hidden hover:shadow-glow transition-all hover:scale-[1.02] border-2 border-gray-200 hover:border-purple-300"
                >
                  {url.includes('video') ? (
                    <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-purple-100 to-pink-100">
                      <div className="relative">
                        <Film className="w-16 h-16 text-purple-400" />
                        <div className="absolute inset-0 bg-purple-500 blur-2xl opacity-20"></div>
                      </div>
                    </div>
                  ) : (
                    <Image
                      src={url}
                      alt={`Media ${i + 1}`}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  )}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
                    <span className="text-white text-sm font-medium">View Full Size</span>
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Hashtags */}
        {hashtags.length > 0 && (
          <div>
            <h4 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-pink-500 to-rose-500 rounded-lg flex items-center justify-center text-white text-xs">
                #
              </div>
              Hashtags ({hashtags.length})
            </h4>
            <div className="flex flex-wrap gap-2">
              {hashtags.map((tag, i) => (
                <span key={i} className="text-sm bg-gradient-to-r from-pink-50 to-rose-50 text-pink-700 px-4 py-2 rounded-full border border-pink-100 hover:shadow-lg hover:scale-105 transition-all cursor-default font-medium">
                  #{tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Metadata */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-soft">
            <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Created</h4>
            <p className="text-sm text-gray-900 font-medium">{formatDateTime(post.created_at)}</p>
          </div>
          {post.published_at && (
            <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-soft">
              <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Published</h4>
              <p className="text-sm text-gray-900 font-medium">{formatDateTime(post.published_at)}</p>
            </div>
          )}
          {post.location && (
            <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-soft">
              <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Location</h4>
              <p className="text-sm text-gray-900 font-medium">{post.location}</p>
            </div>
          )}
          {post.platform_post_url && (
            <div className="p-4 bg-gradient-to-br from-primary-50 to-secondary-50 rounded-xl border border-primary-100 shadow-soft">
              <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Link</h4>
              <a
                href={post.platform_post_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-2 font-medium group"
              >
                View on {post.platform}
                <ExternalLink className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </a>
            </div>
          )}
        </div>

        {/* Error Message */}
        {post.error_message && (
          <div className="p-4 bg-gradient-to-br from-red-50 to-rose-50 border-2 border-red-200 rounded-xl">
            <h4 className="text-sm font-bold text-red-900 mb-2 flex items-center gap-2">
              <div className="w-6 h-6 bg-red-500 rounded-lg flex items-center justify-center text-white text-xs">
                !
              </div>
              Error
            </h4>
            <p className="text-sm text-red-700 leading-relaxed">{post.error_message}</p>
          </div>
        )}

        {/* Content Seed Info */}
        <Link
          href={`/content-seeds?seed=${(post as any).content_seed_id}&type=${(post as any).content_seed_type}`}
          className="block p-4 bg-gradient-to-br from-cyan-50 to-blue-50 rounded-xl border border-cyan-200 hover:border-cyan-300 hover:shadow-lg transition-all group"
        >
          <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5 text-cyan-600" />
            Content Seed
          </h4>
          <div className="flex items-center justify-between">
            <div className="flex flex-col gap-2">
              <span className="text-xs bg-white text-cyan-700 px-3 py-2 rounded-lg border border-cyan-200 font-medium inline-block">
                {(post as any).content_seed_type?.replace(/_/g, ' ') || 'Unknown'}
              </span>
              {(post as any).seed_name && (
                <span className="text-sm text-gray-900 font-medium line-clamp-1">
                  {(post as any).seed_name}
                </span>
              )}
            </div>
            <ExternalLink className="w-4 h-4 text-cyan-600 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
          </div>
        </Link>

        {/* Verification Report Link */}
        {((post as any).verification_status === 'verified' || (post as any).verification_status === 'rejected') && (
          <Link
            href={`/verifier?post=${post.id}`}
            className={cn(
              "block p-4 rounded-xl border hover:shadow-lg transition-all group",
              (post as any).verification_status === 'verified'
                ? "bg-gradient-to-br from-green-50 to-emerald-50 border-green-200 hover:border-green-300"
                : "bg-gradient-to-br from-red-50 to-rose-50 border-red-200 hover:border-red-300"
            )}
          >
            <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
              {(post as any).verification_status === 'verified' ? (
                <ShieldCheck className="w-3.5 h-3.5 text-green-600" />
              ) : (
                <ShieldX className="w-3.5 h-3.5 text-red-600" />
              )}
              Verification Report
            </h4>
            <div className="flex items-center justify-between">
              <div className="flex flex-col gap-2">
                <span className={cn(
                  "text-xs px-3 py-2 rounded-lg font-medium inline-block",
                  (post as any).verification_status === 'verified'
                    ? "bg-white text-green-700 border border-green-200"
                    : "bg-white text-red-700 border border-red-200"
                )}>
                  {(post as any).verification_status === 'verified' ? 'Approved' : 'Rejected'}
                </span>
                <span className="text-sm text-gray-600">
                  View verification details
                </span>
              </div>
              <ExternalLink className={cn(
                "w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform",
                (post as any).verification_status === 'verified' ? "text-green-600" : "text-red-600"
              )} />
            </div>
          </Link>
        )}
      </div>
    </ExpandableCard>
  )
}
