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
          getCompletedPostsBySeed(seed.id),
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
    <div className="space-y-2">
      <p className="text-sm line-clamp-2">{seed.idea}</p>
      <div className="flex items-center gap-4 text-xs text-gray-500">
        <span className="bg-yellow-50 text-yellow-700 px-2 py-1 rounded-full">
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
        <span className="text-xs bg-yellow-50 text-yellow-700 px-2 py-1 rounded-full">
          {seed.format}
        </span>
      }
    >
      <div className="space-y-6" onClick={() => setLoading(true)}>
        {/* Full Idea */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Idea</h4>
          <p className="text-gray-700">{seed.idea}</p>
        </div>

        {/* Format */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Format</h4>
          <span className="inline-flex items-center gap-2 bg-yellow-50 text-yellow-700 px-3 py-2 rounded-md">
            <FileText className="w-4 h-4" />
            {seed.format}
          </span>
        </div>

        {/* Details */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Creative Direction</h4>
          <p className="text-gray-700 whitespace-pre-line">{seed.details}</p>
        </div>

        {/* Content Timeline */}
        <SeedTimeline tasks={tasks} posts={posts} loading={loading} />
      </div>
    </ExpandableCard>
  )
}
