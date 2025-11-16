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
  const PREVIEW_COUNT = 6 // Show 6 posts initially (2 rows of 3)

  const displayedPosts = isExpanded ? posts : posts.slice(0, PREVIEW_COUNT)
  const hasMore = posts.length > PREVIEW_COUNT

  return (
    <section>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center shadow-lg">
          <FacebookIcon className="w-5 h-5 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900">Facebook Posts</h2>
        <span className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium">
          {posts.length}
        </span>
      </div>

      <FacebookPostGrid posts={displayedPosts} />

      {/* Expand/Collapse Button */}
      {hasMore && (
        <div className="mt-6 flex justify-center">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-2 px-6 py-3 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-full font-medium transition-all border border-blue-200 hover:shadow-md"
          >
            {isExpanded ? (
              <>
                <ChevronUp className="w-4 h-4" />
                Show Less
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4" />
                Show All {posts.length} Posts
              </>
            )}
          </button>
        </div>
      )}
    </section>
  )
}
