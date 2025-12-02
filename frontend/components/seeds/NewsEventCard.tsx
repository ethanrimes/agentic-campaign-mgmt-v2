// frontend/components/seeds/NewsEventCard.tsx

'use client'

import { useState, useEffect } from 'react'
import ExpandableCard from '@/components/common/ExpandableCard'
import SeedTimeline from './SeedTimeline'
import { formatDate, formatRelativeTime } from '@/lib/utils'
import { MapPin, Calendar, ExternalLink, Globe, Info } from 'lucide-react'
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
          getContentCreationTasksBySeed(seed.id, 'news_event', selectedAsset.id),
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
      <p className="text-sm line-clamp-2 text-slate-600 dark:text-slate-300">{seed.description}</p>
      <div className="flex flex-wrap gap-2 text-xs">
        {seed.location && (
          <span className="flex items-center gap-1.5 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 px-2.5 py-1 rounded-full border border-blue-100 dark:border-blue-800">
            <MapPin className="w-3 h-3" />
            {seed.location}
          </span>
        )}
        {seed.start_time && (
          <span className="flex items-center gap-1.5 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 px-2.5 py-1 rounded-full border border-purple-100 dark:border-purple-800">
            <Calendar className="w-3 h-3" />
            {formatDate(seed.start_time)}
          </span>
        )}
        <span className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2.5 py-1 rounded-full font-medium border border-slate-200 dark:border-slate-700">
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
      <div className="space-y-8 p-2">
        {/* Full Description */}
        <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-50/50 to-cyan-50/50 dark:from-blue-900/10 dark:to-cyan-900/10 border border-blue-100 dark:border-blue-800/50">
          <h4 className="text-xs font-bold text-blue-900 dark:text-blue-100 uppercase tracking-wider mb-3 flex items-center gap-2">
            <Info className="w-4 h-4 text-blue-500" />
            Description
          </h4>
          <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-base">{seed.description}</p>
        </div>

        {/* Event Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50 hover:border-blue-200 dark:hover:border-blue-700 transition-colors">
            <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-2">
              <MapPin className="w-3.5 h-3.5 text-blue-500" />
              Location
            </h4>
            <p className="text-slate-900 dark:text-white font-medium">{seed.location}</p>
          </div>
          {seed.start_time && (
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50 hover:border-purple-200 dark:hover:border-purple-700 transition-colors">
              <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                <Calendar className="w-3.5 h-3.5 text-purple-500" />
                Date
              </h4>
              <p className="text-slate-900 dark:text-white font-medium">
                {formatDate(seed.start_time)}
                {seed.end_time && ` - ${formatDate(seed.end_time)}`}
              </p>
            </div>
          )}
        </div>

        {/* Sources */}
        {seed.sources && seed.sources.length > 0 && (
          <div>
            <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              Research Sources
              <span className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded-full text-[10px]">
                {seed.sources.length}
              </span>
            </h4>
            <div className="space-y-3">
              {seed.sources.map((source, index) => (
                <div key={index} className="group p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-primary-300 dark:hover:border-primary-700 transition-all shadow-sm hover:shadow-md">
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary-600 dark:text-primary-400 font-semibold flex items-center gap-2 truncate hover:underline"
                    >
                      <Globe className="w-3.5 h-3.5 flex-shrink-0 opacity-70" />
                      {new URL(source.url).hostname}
                      <ExternalLink className="w-3 h-3 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </a>
                    <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 px-2 py-1 rounded-md">
                      {source.found_by}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">{source.key_findings}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Content Timeline */}
        <div className="pt-6 border-t border-slate-100 dark:border-slate-800">
          <SeedTimeline
            tasks={tasks}
            posts={posts}
            loading={loading}
          />
        </div>
      </div>
    </ExpandableCard>
  )
}