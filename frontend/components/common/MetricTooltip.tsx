// frontend/components/common/MetricTooltip.tsx

'use client'

import { useState, useRef, useEffect, ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Info } from 'lucide-react'

interface MetricDefinition {
  name: string
  description: string
  endpoint: string
  apiField?: string
}

// Instagram account-level metric definitions
export const INSTAGRAM_ACCOUNT_METRICS: Record<string, MetricDefinition> = {
  posts: {
    name: 'Posts',
    description: 'The number of posts tracked in your database. Published posts are live on Instagram, pending posts are scheduled, and failed posts encountered errors during publishing.',
    endpoint: 'Database: completed_posts table',
    apiField: 'status counts',
  },
  reach: {
    name: 'Reach',
    description: 'The total number of unique accounts that have seen any of your posts at least once over the past 28 days. This is a rolling sum of daily reach values.',
    endpoint: 'GET /{ig_user_id}/insights?metric=reach&period=day',
    apiField: 'reach',
  },
  views: {
    name: 'Total Views',
    description: 'The total number of times your posts have been displayed or played across all media. Includes repeat views by the same accounts.',
    endpoint: 'Aggregated from GET /{media_id}/insights?metric=views',
    apiField: 'views (summed across all media)',
  },
  interactions: {
    name: 'Interactions',
    description: 'The total number of likes, comments, saves, and shares across all your posts. Does not include views.',
    endpoint: 'Aggregated from GET /{media_id}/insights?metric=likes,comments,saved,shares',
    apiField: 'likes + comments + saved + shares',
  },
  followers: {
    name: 'Followers',
    description: 'The total number of accounts currently following your Instagram profile.',
    endpoint: 'GET /{ig_user_id}?fields=followers_count',
    apiField: 'followers_count',
  },
  following: {
    name: 'Following',
    description: 'The total number of accounts your Instagram profile is following.',
    endpoint: 'GET /{ig_user_id}?fields=follows_count',
    apiField: 'follows_count',
  },
}

// Facebook page-level metric definitions
export const FACEBOOK_PAGE_METRICS: Record<string, MetricDefinition> = {
  posts: {
    name: 'Posts',
    description: 'The number of posts tracked in your database. Published posts are live on Facebook, pending posts are scheduled, and failed posts encountered errors during publishing.',
    endpoint: 'Database: completed_posts table',
    apiField: 'status counts',
  },
  engagement: {
    name: 'Engagement',
    description: 'The number of times people have engaged with your posts through reactions, comments, shares, and more over the past 28 days.',
    endpoint: 'GET /{page_id}/insights?metric=page_post_engagements&period=days_28',
    apiField: 'page_post_engagements',
  },
  media_views: {
    name: 'Media Views',
    description: 'The number of times your content was played or displayed over the past 28 days. Content includes videos, posts, stories, and ads.',
    endpoint: 'GET /{page_id}/insights?metric=page_media_view&period=days_28',
    apiField: 'page_media_view',
  },
  followers: {
    name: 'Followers',
    description: 'The total number of people who follow your Facebook page.',
    endpoint: 'GET /{page_id}/insights?metric=page_follows',
    apiField: 'page_follows',
  },
}

// Facebook post-level metric definitions
export const FACEBOOK_POST_METRICS: Record<string, MetricDefinition> = {
  reactions: {
    name: 'Reactions',
    description: 'The total number of reactions on this post, including likes, love, wow, haha, sad, and angry.',
    endpoint: 'GET /{post_id}/insights?metric=post_reactions_by_type_total',
    apiField: 'post_reactions_by_type_total',
  },
  comments: {
    name: 'Comments',
    description: 'The number of comments on this post. Only counts top-level comments.',
    endpoint: 'GET /{post_id}?fields=comments.summary(true)',
    apiField: 'comments.summary.total_count',
  },
  shares: {
    name: 'Shares',
    description: 'The number of times this post was shared by users.',
    endpoint: 'GET /{post_id}?fields=shares',
    apiField: 'shares.count',
  },
  impressions: {
    name: 'Impressions',
    description: 'The total number of times your post was displayed on screen, including repeat views.',
    endpoint: 'GET /{post_id}/insights?metric=post_impressions',
    apiField: 'post_impressions',
  },
  reach: {
    name: 'Unique Reach',
    description: 'The number of unique accounts that saw this post at least once.',
    endpoint: 'GET /{post_id}/insights?metric=post_impressions_unique',
    apiField: 'post_impressions_unique',
  },
  media_view: {
    name: 'Media Views',
    description: 'The number of times the media in this post was viewed.',
    endpoint: 'GET /{post_id}/insights?metric=post_media_view',
    apiField: 'post_media_view',
  },
  // Video/Reel metrics
  video_views: {
    name: 'Total Views',
    description: 'The number of times your video/reel started playing. For reels, this counts plays with 1ms or more of playback.',
    endpoint: 'GET /{video_id}?fields=video_insights',
    apiField: 'blue_reels_play_count / fb_reels_total_plays',
  },
  video_views_unique: {
    name: 'Unique Views',
    description: 'The number of unique people who saw your video/reel at least once.',
    endpoint: 'GET /{video_id}?fields=video_insights',
    apiField: 'post_impressions_unique',
  },
  video_avg_watch_time: {
    name: 'Avg Watch Time',
    description: 'The average time users spent watching this video/reel, including any time spent replaying.',
    endpoint: 'GET /{video_id}?fields=video_insights',
    apiField: 'post_video_avg_time_watched',
  },
  video_length: {
    name: 'Video Length',
    description: 'The total duration of the video/reel in seconds.',
    endpoint: 'GET /{video_id}?fields=length',
    apiField: 'length',
  },
}

// Instagram media-level metric definitions
export const INSTAGRAM_MEDIA_METRICS: Record<string, MetricDefinition> = {
  likes: {
    name: 'Likes',
    description: 'The number of likes on this post. Represents users who tapped the heart icon.',
    endpoint: 'GET /{media_id}/insights?metric=likes',
    apiField: 'likes',
  },
  comments: {
    name: 'Comments',
    description: 'The number of comments on this post. Only counts top-level comments, not replies.',
    endpoint: 'GET /{media_id}/insights?metric=comments',
    apiField: 'comments',
  },
  saved: {
    name: 'Saves',
    description: 'The number of unique accounts that saved this post to their collections.',
    endpoint: 'GET /{media_id}/insights?metric=saved',
    apiField: 'saved',
  },
  shares: {
    name: 'Shares',
    description: 'The number of times this post was shared via direct message, stories, or external apps.',
    endpoint: 'GET /{media_id}/insights?metric=shares',
    apiField: 'shares',
  },
  views: {
    name: 'Total Views',
    description: 'The number of times this post was displayed or played. Includes repeat views by the same account.',
    endpoint: 'GET /{media_id}/insights?metric=views',
    apiField: 'views',
  },
  reach: {
    name: 'Reach',
    description: 'The number of unique accounts that have seen this post at least once. This is an estimated metric and is deduplicated.',
    endpoint: 'GET /{media_id}/insights?metric=reach',
    apiField: 'reach',
  },
  ig_reels_avg_watch_time_ms: {
    name: 'Avg Watch Time',
    description: 'The average time (in milliseconds) that users spent watching this reel before scrolling away.',
    endpoint: 'GET /{media_id}/insights?metric=ig_reels_avg_watch_time',
    apiField: 'ig_reels_avg_watch_time',
  },
  ig_reels_video_view_total_time_ms: {
    name: 'Total Watch Time',
    description: 'The cumulative time (in milliseconds) all users spent watching this reel.',
    endpoint: 'GET /{media_id}/insights?metric=ig_reels_video_view_total_time',
    apiField: 'ig_reels_video_view_total_time',
  },
}

interface MetricTooltipProps {
  metricKey: string
  children: ReactNode
  position?: 'top' | 'bottom' | 'left' | 'right'
  metricType?: 'media' | 'account'
  platform?: 'instagram' | 'facebook'
}

export default function MetricTooltip({
  metricKey,
  children,
  position = 'top',
  metricType = 'media',
  platform = 'instagram'
}: MetricTooltipProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 })
  const triggerRef = useRef<HTMLDivElement>(null)
  const [mounted, setMounted] = useState(false)

  // Select metrics based on platform and type
  const getMetrics = () => {
    if (platform === 'facebook') {
      return metricType === 'account' ? FACEBOOK_PAGE_METRICS : FACEBOOK_POST_METRICS
    }
    return metricType === 'account' ? INSTAGRAM_ACCOUNT_METRICS : INSTAGRAM_MEDIA_METRICS
  }
  const metrics = getMetrics()
  const metric = metrics[metricKey]

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (isVisible && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect()
      const tooltipWidth = 256 // w-64 = 16rem = 256px
      const tooltipHeight = 140 // approximate height
      const gap = 8

      let top = 0
      let left = 0

      switch (position) {
        case 'top':
          top = rect.top - tooltipHeight - gap + window.scrollY
          left = rect.left + rect.width / 2 - tooltipWidth / 2 + window.scrollX
          break
        case 'bottom':
          top = rect.bottom + gap + window.scrollY
          left = rect.left + rect.width / 2 - tooltipWidth / 2 + window.scrollX
          break
        case 'left':
          top = rect.top + rect.height / 2 - tooltipHeight / 2 + window.scrollY
          left = rect.left - tooltipWidth - gap + window.scrollX
          break
        case 'right':
          top = rect.top + rect.height / 2 - tooltipHeight / 2 + window.scrollY
          left = rect.right + gap + window.scrollX
          break
      }

      // Keep tooltip within viewport bounds
      const viewportWidth = window.innerWidth
      const viewportHeight = window.innerHeight

      if (left < 10) left = 10
      if (left + tooltipWidth > viewportWidth - 10) left = viewportWidth - tooltipWidth - 10
      if (top < 10 + window.scrollY) top = 10 + window.scrollY
      if (top + tooltipHeight > viewportHeight + window.scrollY - 10) {
        top = viewportHeight + window.scrollY - tooltipHeight - 10
      }

      setTooltipPosition({ top, left })
    }
  }, [isVisible, position])

  if (!metric) {
    return <>{children}</>
  }

  const tooltipContent = (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.15 }}
          style={{
            position: 'fixed',
            top: tooltipPosition.top - window.scrollY,
            left: tooltipPosition.left - window.scrollX,
            zIndex: 99999,
          }}
          className="pointer-events-none"
        >
          <div className="bg-slate-800 text-white rounded-lg shadow-xl p-3 w-64 text-left">
            <div className="flex items-center gap-2 mb-2">
              <Info className="w-4 h-4 text-blue-400 flex-shrink-0" />
              <span className="font-semibold text-sm">{metric.name}</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed mb-2">
              {metric.description}
            </p>
            <div className="pt-2 border-t border-slate-700">
              <p className="text-[10px] text-slate-400 font-mono break-all">
                {metric.endpoint}
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )

  return (
    <>
      <div
        ref={triggerRef}
        className="h-full"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        {children}
      </div>
      {mounted && createPortal(tooltipContent, document.body)}
    </>
  )
}
