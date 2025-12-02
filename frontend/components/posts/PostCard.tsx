// frontend/components/posts/PostCard.tsx

'use client'

import ExpandableCard from '@/components/common/ExpandableCard'
import { formatDateTime, formatRelativeTime, getStatusColor, getPlatformIcon, cn } from '@/lib/utils'
import { ExternalLink, Image as ImageIcon, Film, Sparkles, ShieldCheck, ShieldX, ShieldAlert, Play } from 'lucide-react'
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
          <span className="flex items-center gap-1.5 bg-green-50/50 dark:bg-green-900/20 text-green-700 dark:text-green-300 px-2.5 py-1 rounded-full text-xs font-medium border border-green-100 dark:border-green-800">
            <ShieldCheck className="w-3.5 h-3.5" />
            Verified
          </span>
        )
      case 'rejected':
        return (
          <span className="flex items-center gap-1.5 bg-red-50/50 dark:bg-red-900/20 text-red-700 dark:text-red-300 px-2.5 py-1 rounded-full text-xs font-medium border border-red-100 dark:border-red-800">
            <ShieldX className="w-3.5 h-3.5" />
            Rejected
          </span>
        )
      default:
        return (
          <span className="flex items-center gap-1.5 bg-amber-50/50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 px-2.5 py-1 rounded-full text-xs font-medium border border-amber-100 dark:border-amber-800">
            <ShieldAlert className="w-3.5 h-3.5" />
            Unverified
          </span>
        )
    }
  }

  const preview = (
    <div className="space-y-3">
      <p className="text-sm line-clamp-2 text-slate-600 dark:text-slate-300 leading-relaxed">{post.text}</p>
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2.5 py-1 rounded-full font-medium border border-slate-200 dark:border-slate-700">
          {post.post_type.replace(/_/g, ' ')}
        </span>
        {verificationStatusBadge()}
        {mediaUrls.length > 0 && (
          <span className="flex items-center gap-1.5 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 px-2.5 py-1 rounded-full font-medium border border-purple-100 dark:border-purple-800">
            {mediaUrls[0].includes('video') ? (
              <Film className="w-3.5 h-3.5" />
            ) : (
              <ImageIcon className="w-3.5 h-3.5" />
            )}
            {mediaUrls.length} media
          </span>
        )}
        {hashtags.length > 0 && (
          <span className="bg-pink-50 dark:bg-pink-900/20 text-pink-700 dark:text-pink-300 px-2.5 py-1 rounded-full font-medium border border-pink-100 dark:border-pink-800">
            {hashtags.length} hashtags
          </span>
        )}
      </div>
    </div>
  )

  const statusColors = {
    published: 'bg-green-50 text-green-700 border border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-800',
    pending: 'bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-900/20 dark:text-amber-300 dark:border-amber-800',
    failed: 'bg-red-50 text-red-700 border border-red-200 dark:bg-red-900/20 dark:text-red-300 dark:border-red-800',
  }

  return (
    <ExpandableCard
      title={`${getPlatformIcon(post.platform)} ${post.post_type.replace(/_/g, ' ')}`}
      subtitle={formatRelativeTime(post.created_at)}
      preview={preview}
      badge={
        <span className={cn('text-xs px-2.5 py-1 rounded-full font-bold uppercase tracking-wider', statusColors[post.status])}>
          {post.status}
        </span>
      }
    >
      <div className="space-y-8 p-2">
        {/* Full Text */}
        <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-50/50 to-indigo-50/50 dark:from-blue-900/10 dark:to-indigo-900/10 border border-blue-100 dark:border-blue-800/50">
          <h4 className="text-xs font-bold text-blue-900 dark:text-blue-100 uppercase tracking-wider mb-3 flex items-center gap-2">
            <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
            Caption
          </h4>
          <p className="text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line text-base">{post.text}</p>
        </div>

        {/* Media */}
        {mediaUrls.length > 0 && (
          <div>
            <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              Media Gallery
              <span className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded-full text-[10px]">
                {mediaUrls.length}
              </span>
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
                  className="group relative aspect-video bg-slate-100 dark:bg-slate-800 rounded-xl overflow-hidden hover:shadow-lg hover:shadow-purple-500/10 transition-all border border-slate-200 dark:border-slate-700"
                >
                  {url.includes('video') ? (
                    <div className="absolute inset-0 flex items-center justify-center bg-slate-900/5">
                      <div className="relative z-10 w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Play className="w-8 h-8 text-white fill-white" />
                      </div>
                      <video src={url} className="absolute inset-0 w-full h-full object-cover opacity-80 group-hover:opacity-60 transition-opacity" muted />
                    </div>
                  ) : (
                    <Image
                      src={url}
                      alt={`Media ${i + 1}`}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                  )}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
                    <span className="text-white text-xs font-medium backdrop-blur-md px-3 py-1.5 rounded-full bg-white/10">
                      View Full Size
                    </span>
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Hashtags */}
        {hashtags.length > 0 && (
          <div>
            <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">
              Hashtags
            </h4>
            <div className="flex flex-wrap gap-2">
              {hashtags.map((tag, i) => (
                <span key={i} className="text-sm bg-white dark:bg-slate-800 text-pink-600 dark:text-pink-400 px-3 py-1.5 rounded-lg border border-pink-100 dark:border-pink-900/30 shadow-sm hover:shadow-md transition-all cursor-default font-medium">
                  #{tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Metadata Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-slate-100 dark:border-slate-800">
          {post.platform_post_url && (
            <a
              href={post.platform_post_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700 hover:border-primary-300 dark:hover:border-primary-700 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 bg-white dark:bg-slate-700 rounded-lg shadow-sm group-hover:text-primary-500 transition-colors">
                  <ExternalLink className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-500 dark:text-slate-400">Live Post</p>
                  <p className="text-sm font-bold text-slate-900 dark:text-white">View on {post.platform}</p>
                </div>
              </div>
            </a>
          )}

          {/* Content Seed Info */}
          {(post as any).content_seed_id && (
            <Link
              href={`/content-seeds?seed=${(post as any).content_seed_id}&type=${(post as any).content_seed_type}`}
              className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-br from-cyan-50 to-blue-50 dark:from-cyan-900/10 dark:to-blue-900/10 border border-cyan-100 dark:border-cyan-800/30 hover:border-cyan-300 dark:hover:border-cyan-600 transition-colors group"
            >
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="p-2 bg-white/80 dark:bg-cyan-900/30 rounded-lg shadow-sm text-cyan-600 dark:text-cyan-400">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-medium text-cyan-700 dark:text-cyan-300">Generated From</p>
                  <p className="text-sm font-bold text-slate-900 dark:text-white truncate">
                    {(post as any).seed_name || 'Seed Idea'}
                  </p>
                </div>
              </div>
            </Link>
          )}
        </div>

        {/* Error Message */}
        {post.error_message && (
          <div className="p-4 bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-xl flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 shrink-0" />
            <div>
              <h4 className="text-sm font-bold text-red-900 dark:text-red-100">Error Reported</h4>
              <p className="text-sm text-red-700 dark:text-red-300 mt-1 leading-relaxed">{post.error_message}</p>
            </div>
          </div>
        )}
      </div>
    </ExpandableCard>
  )
}
