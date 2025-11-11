// frontend/components/seeds/NewsEventCard.tsx

'use client'

import { useState, useEffect } from 'react'
import ExpandableCard from '@/components/common/ExpandableCard'
import SeedTimeline from './SeedTimeline'
import { formatDate, formatRelativeTime } from '@/lib/utils'
import { MapPin, Calendar, ExternalLink } from 'lucide-react'
import type { NewsEventSeed } from '@/types'
import { getContentCreationTasksBySeed, getCompletedPostsBySeed } from '@/lib/api'

interface NewsEventCardProps {
  seed: NewsEventSeed
}

export default function NewsEventCard({ seed }: NewsEventCardProps) {
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
      <p className="text-sm line-clamp-2">{seed.description}</p>
      <div className="flex flex-wrap gap-4 text-xs text-gray-500">
        {seed.location && (
          <span className="flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            {seed.location}
          </span>
        )}
        {seed.start_time && (
          <span className="flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            {formatDate(seed.start_time)}
          </span>
        )}
        <span>{seed.sources?.length || 0} sources</span>
      </div>
    </div>
  )

  return (
    <ExpandableCard
      title={seed.name}
      subtitle={formatRelativeTime(seed.created_at)}
      preview={preview}
    >
      <div className="space-y-6" onClick={() => setLoading(true)}>
        {/* Full Description */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Description</h4>
          <p className="text-gray-700">{seed.description}</p>
        </div>

        {/* Event Details */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-1">Location</h4>
            <p className="text-gray-700">{seed.location}</p>
          </div>
          {seed.start_time && (
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-1">Date</h4>
              <p className="text-gray-700">
                {formatDate(seed.start_time)}
                {seed.end_time && ` - ${formatDate(seed.end_time)}`}
              </p>
            </div>
          )}
        </div>

        {/* Sources */}
        {seed.sources && seed.sources.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3">Sources ({seed.sources.length})</h4>
            <div className="space-y-3">
              {seed.sources.map((source, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-md border border-gray-200">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1 truncate"
                    >
                      {new URL(source.url).hostname}
                      <ExternalLink className="w-3 h-3 flex-shrink-0" />
                    </a>
                    <span className="text-xs text-gray-500 whitespace-nowrap">
                      {source.found_by}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700">{source.key_findings}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Content Timeline */}
        <SeedTimeline
          tasks={tasks}
          posts={posts}
          loading={loading}
        />
      </div>
    </ExpandableCard>
  )
}
