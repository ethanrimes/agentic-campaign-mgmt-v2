// frontend/components/posts/ExpandableFacebookPosts.tsx

'use client'

import { useState } from 'react'
import { Facebook as FacebookIcon, ChevronDown, ChevronUp } from 'lucide-react'
import FacebookPostGrid from './FacebookPostGrid'
import type { CompletedPost } from '@/types'

interface ExpandableFacebookPostsProps {
  posts: CompletedPost[]
}

export default function ExpandableFacebookPosts({ posts }: ExpandableFacebookPostsProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const PREVIEW_COUNT = 10 // Show 10 posts initially (2 rows of 5)

  const displayedPosts = isExpanded ? posts : posts.slice(0, PREVIEW_COUNT)
  const hasMore = posts.length > PREVIEW_COUNT

  return (
    <section>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-md">
          <FacebookIcon className="w-5 h-5 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Facebook Posts</h2>
        <span className="text-sm bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 px-3 py-1 rounded-full font-medium border border-blue-100 dark:border-blue-800">
          {posts.length}
        </span>
      </div>

      <FacebookPostGrid posts={displayedPosts} />

      {/* Expand/Collapse Button */}
      {hasMore && (
        <div className="mt-8 flex justify-center">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="group flex items-center gap-2 px-6 py-2.5 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-full font-medium transition-all border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-md"
          >
            {isExpanded ? (
              <>
                <ChevronUp className="w-4 h-4 text-slate-400 dark:text-slate-500 group-hover:text-primary-500 transition-colors" />
                Show Less
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4 text-slate-400 dark:text-slate-500 group-hover:text-primary-500 transition-colors" />
                Show All {posts.length} Posts
              </>
            )}
          </button>
        </div>
      )}
    </section>
  )
}