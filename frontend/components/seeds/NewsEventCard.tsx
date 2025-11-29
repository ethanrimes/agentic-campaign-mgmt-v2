// frontend/components/seeds/NewsEventCard.tsx

'use client'

import { useState, useEffect } from 'react'
import ExpandableCard from '@/components/common/ExpandableCard'
import SeedTimeline from './SeedTimeline'
import { formatDate, formatRelativeTime } from '@/lib/utils'
import { MapPin, Calendar, ExternalLink } from 'lucide-react'
import type { NewsEventSeed } from '@/types'
import { getContentCreationTasksBySeed, getCompletedPostsBySeed } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'

interface NewsEventCardProps {
  seed: NewsEventSeed
}

export default function NewsEventCard({ seed }: NewsEventCardProps) {
  const { selectedAsset } = useBusinessAsset()
  const [tasks, setTasks] = useState<any[]>([])
  const [posts, setPosts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [isExpanded, setIsExpanded] = useState(false)

  useEffect(() => {
    async function loadData() {
      if (!isExpanded || !selectedAsset) return
      try {
        setLoading(true)
        const [tasksData, postsData] = await Promise.all([
          getContentCreationTasksBySeed(seed.id, selectedAsset.id),
          getCompletedPostsBySeed(seed.id, 'news_event', selectedAsset.id),
        ])
        setTasks(tasksData)
        setPosts(postsData)
      } catch (error) {
        console.error('Failed to load seed data:', error)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [seed.id, isExpanded, selectedAsset])

  const preview = (
    <div className="space-y-3">
      <p className="text-sm line-clamp-2 text-gray-700">{seed.description}</p>
      <div className="flex flex-wrap gap-3 text-xs">
        {seed.location && (
          <span className="flex items-center gap-1.5 bg-blue-50 text-blue-700 px-3 py-1.5 rounded-full">
            <MapPin className="w-3.5 h-3.5" />
            {seed.location}
          </span>
        )}
        {seed.start_time && (
          <span className="flex items-center gap-1.5 bg-purple-50 text-purple-700 px-3 py-1.5 rounded-full">
            <Calendar className="w-3.5 h-3.5" />
            {formatDate(seed.start_time)}
          </span>
        )}
        <span className="flex items-center gap-1.5 bg-gray-100 text-gray-700 px-3 py-1.5 rounded-full font-medium">
          {seed.sources?.length || 0} sources
        </span>
      </div>
    </div>
  )

  return (
    <ExpandableCard
      title={seed.name}
      subtitle={formatRelativeTime(seed.created_at)}
      preview={preview}
      onExpandChange={setIsExpanded}
    >
      <div className="space-y-6">
        {/* Full Description */}
        <div className="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border border-blue-100">
          <h4 className="text-sm font-bold text-gray-900 mb-2 flex items-center gap-2">
            <div className="w-1 h-4 bg-gradient-to-b from-blue-500 to-cyan-500 rounded-full"></div>
            Description
          </h4>
          <p className="text-gray-700 leading-relaxed">{seed.description}</p>
        </div>

        {/* Event Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-soft hover:shadow-glow transition-all">
            <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-blue-600" />
              Location
            </h4>
            <p className="text-gray-900 font-medium">{seed.location}</p>
          </div>
          {seed.start_time && (
            <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-soft hover:shadow-glow transition-all">
              <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                <Calendar className="w-4 h-4 text-purple-600" />
                Date
              </h4>
              <p className="text-gray-900 font-medium">
                {formatDate(seed.start_time)}
                {seed.end_time && ` - ${formatDate(seed.end_time)}`}
              </p>
            </div>
          )}
        </div>

        {/* Sources */}
        {seed.sources && seed.sources.length > 0 && (
          <div>
            <h4 className="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center text-white text-xs font-bold">
                {seed.sources.length}
              </div>
              Research Sources
            </h4>
            <div className="space-y-3">
              {seed.sources.map((source, index) => (
                <div key={index} className="group p-4 bg-white rounded-xl border border-gray-200 shadow-soft hover:shadow-glow hover:border-primary-200 transition-all">
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary-600 hover:text-primary-700 font-semibold flex items-center gap-2 truncate group-hover:underline"
                    >
                      {new URL(source.url).hostname}
                      <ExternalLink className="w-3.5 h-3.5 flex-shrink-0 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                    </a>
                    <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-full whitespace-nowrap font-medium">
                      {source.found_by}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 leading-relaxed">{source.key_findings}</p>
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
