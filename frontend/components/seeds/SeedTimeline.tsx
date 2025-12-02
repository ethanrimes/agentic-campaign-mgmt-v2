// frontend/components/seeds/SeedTimeline.tsx

import { formatDateTime, getStatusColor, cn } from '@/lib/utils'
import type { ContentCreationTask, CompletedPost } from '@/types'
import VerificationStatusBadge from '@/components/common/VerificationStatusBadge'
import { CheckCircle2, Clock, Facebook, Instagram, AlertTriangle, FileEdit } from 'lucide-react'

interface SeedTimelineProps {
  tasks: ContentCreationTask[]
  posts: CompletedPost[]
  loading: boolean
}

export default function SeedTimeline({ tasks, posts, loading }: SeedTimelineProps) {
  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        <p className="text-sm text-slate-500 mt-3">Loading timeline...</p>
      </div>
    )
  }

  if (tasks.length === 0 && posts.length === 0) {
    return (
      <div className="text-center py-8 bg-slate-50/50 dark:bg-slate-800/50 rounded-xl border border-dashed border-slate-300 dark:border-slate-700">
        <p className="text-sm text-slate-500 dark:text-slate-400">No content created from this seed yet</p>
      </div>
    )
  }

  const timelineItems = [
    ...tasks.map(t => ({ type: 'task' as const, data: t, date: new Date(t.created_at) })),
    ...posts.map(p => ({ type: 'post' as const, data: p, date: new Date(p.created_at) }))
  ].sort((a, b) => b.date.getTime() - a.date.getTime())

  return (
    <div className="mt-4">
      <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-6 pl-2">
        Activity Timeline
      </h4>
      <div className="relative space-y-0 pl-2">
        {/* Vertical Line */}
        <div className="absolute left-[19px] top-2 bottom-4 w-0.5 bg-slate-200 dark:bg-slate-700"></div>

        {timelineItems.map((item, index) => {
          const isTask = item.type === 'task'
          const data = item.data
          
          return (
            <div key={isTask ? `t-${data.id}` : `p-${data.id}`} className="relative flex gap-6 pb-8 last:pb-0 group">
              {/* Icon Node */}
              <div className="relative z-10">
                <div className={cn(
                  "w-9 h-9 rounded-full flex items-center justify-center border-2 shadow-sm transition-transform group-hover:scale-110",
                  isTask 
                    ? "bg-blue-100 border-blue-200 text-blue-600 dark:bg-blue-900/30 dark:border-blue-800 dark:text-blue-400" 
                    : "bg-green-100 border-green-200 text-green-600 dark:bg-green-900/30 dark:border-green-800 dark:text-green-400"
                )}>
                  {isTask ? <FileEdit className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
                </div>
              </div>

              {/* Content Card */}
              <div className="flex-1 min-w-0">
                <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700 shadow-sm group-hover:shadow-md transition-all">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <span className={cn(
                        "text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-md mb-1 inline-block",
                        isTask 
                          ? "bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300" 
                          : "bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-300"
                      )}>
                        {isTask ? 'Creation Task' : 'Completed Post'}
                      </span>
                      <h5 className="text-sm font-bold text-slate-900 dark:text-white mt-1">
                        {isTask ? 'Content Generation' : `${(data as CompletedPost).platform === 'facebook' ? 'Facebook' : 'Instagram'} Post`}
                      </h5>
                    </div>
                    <span className="text-xs text-slate-400 dark:text-slate-500 flex items-center gap-1 whitespace-nowrap">
                      <Clock className="w-3 h-3" />
                      {formatDateTime(item.date)}
                    </span>
                  </div>

                  {isTask ? (
                    <div className="text-xs text-slate-600 dark:text-slate-300 space-y-1.5 mt-3 bg-slate-50 dark:bg-slate-900/50 p-3 rounded-lg border border-slate-100 dark:border-slate-800">
                      <div className="flex items-center justify-between">
                        <span className="flex items-center gap-1.5">
                          <Instagram className="w-3.5 h-3.5 text-pink-500" />
                          Instagram
                        </span>
                        <span className="font-medium">
                          {(data as ContentCreationTask).instagram_image_posts} images, {(data as ContentCreationTask).instagram_reel_posts} reels
                        </span>
                      </div>
                      <div className="flex items-center justify-between border-t border-slate-200 dark:border-slate-700 pt-1.5">
                        <span className="flex items-center gap-1.5">
                          <Facebook className="w-3.5 h-3.5 text-blue-600" />
                          Facebook
                        </span>
                        <span className="font-medium">
                          {(data as ContentCreationTask).facebook_feed_posts} feed, {(data as ContentCreationTask).facebook_video_posts} videos
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="mt-3 space-y-3">
                      <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-2 italic">
                        "{(data as CompletedPost).text}"
                      </p>
                      
                      <div className="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-700">
                        <div className="flex items-center gap-2">
                          <VerificationStatusBadge
                            status={(data as CompletedPost).verification_status || 'unverified'}
                            postId={data.id}
                            size="sm"
                          />
                          <span className={cn(
                            "text-[10px] px-2 py-0.5 rounded-full font-bold uppercase",
                            getStatusColor(data.status)
                          )}>
                            {data.status}
                          </span>
                        </div>
                        
                        {(data as CompletedPost).platform_post_url && (
                          <a
                            href={(data as CompletedPost).platform_post_url || '#'}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 transition-colors"
                          >
                            View Live →
                          </a>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
