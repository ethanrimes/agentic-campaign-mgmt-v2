// frontend/components/seeds/UngroundedSeedCard.tsx

'use client'

import { useState, useEffect } from 'react'
import ExpandableCard from '@/components/common/ExpandableCard'
import SeedTimeline from './SeedTimeline'
import { formatRelativeTime } from '@/lib/utils'
import { FileText } from 'lucide-react'
import type { UngroundedSeed } from '@/types'
import { getContentCreationTasksBySeed, getCompletedPostsBySeed } from '@/lib/api'

interface UngroundedSeedCardProps {
  seed: UngroundedSeed
}

export default function UngroundedSeedCard({ seed }: UngroundedSeedCardProps) {
  const [tasks, setTasks] = useState<any[]>([])
  const [posts, setPosts] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    async function loadData() {
      if (!loading) return
      try {
        const [tasksData, postsData] = await Promise.all([
          getContentCreationTasksBySeed(seed.id),
          getCompletedPostsBySeed(seed.id, 'ungrounded'),
        ])
        setTasks(tasksData)
        setPosts(postsData)
      } catch (error) {
        console.error('Failed to load seed data:', error)
      }
    }
    loadData()
  }, [seed.id, loading])

  const preview = (
    <div className="space-y-3">
      <p className="text-sm line-clamp-2 text-gray-700">{seed.idea}</p>
      <div className="flex items-center gap-3">
        <span className="bg-gradient-to-r from-amber-50 to-orange-50 text-amber-700 px-3 py-1.5 rounded-full text-xs font-medium border border-amber-100">
          {seed.format}
        </span>
      </div>
    </div>
  )

  return (
    <ExpandableCard
      title={seed.idea}
      subtitle={`Created ${formatRelativeTime(seed.created_at)} • ${seed.created_by}`}
      preview={preview}
      badge={
        <span className="text-xs bg-gradient-to-r from-amber-50 to-orange-50 text-amber-700 px-3 py-1.5 rounded-full font-medium border border-amber-100">
          {seed.format}
        </span>
      }
    >
      <div className="space-y-6" onClick={() => setLoading(true)}>
        {/* Full Idea */}
        <div className="p-4 bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl border border-amber-100">
          <h4 className="text-sm font-bold text-gray-900 mb-2 flex items-center gap-2">
            <div className="w-1 h-4 bg-gradient-to-b from-amber-500 to-orange-500 rounded-full"></div>
            Creative Idea
          </h4>
          <p className="text-gray-700 leading-relaxed">{seed.idea}</p>
        </div>

        {/* Format */}
        <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-soft">
          <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <FileText className="w-4 h-4 text-amber-600" />
            Content Format
          </h4>
          <span className="inline-flex items-center gap-2 bg-gradient-to-r from-amber-50 to-orange-50 text-amber-700 px-4 py-2 rounded-lg border border-amber-100 font-medium">
            {seed.format}
          </span>
        </div>

        {/* Details */}
        <div className="p-4 bg-gradient-to-br from-purple-50/50 to-pink-50/50 rounded-xl border border-purple-100/50">
          <h4 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
            <div className="w-1 h-4 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></div>
            Creative Direction
          </h4>
          <p className="text-gray-700 leading-relaxed whitespace-pre-line">{seed.details}</p>
        </div>

        {/* Content Timeline */}
        <SeedTimeline tasks={tasks} posts={posts} loading={loading} />
      </div>
    </ExpandableCard>
  )
}
