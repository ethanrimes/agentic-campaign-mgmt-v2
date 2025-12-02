// frontend/components/seeds/UngroundedSeedCard.tsx

'use client'

import { useState, useEffect } from 'react'
import ExpandableCard from '@/components/common/ExpandableCard'
import SeedTimeline from './SeedTimeline'
import { formatRelativeTime } from '@/lib/utils'
import { FileText, Lightbulb, Sparkles } from 'lucide-react'
import type { UngroundedSeed } from '@/types'
import { getContentCreationTasksBySeed, getCompletedPostsBySeed } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'

interface UngroundedSeedCardProps {
  seed: UngroundedSeed
}

export default function UngroundedSeedCard({ seed }: UngroundedSeedCardProps) {
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
          getContentCreationTasksBySeed(seed.id, 'ungrounded', selectedAsset.id),
          getCompletedPostsBySeed(seed.id, 'ungrounded', selectedAsset.id),
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
      <p className="text-sm line-clamp-2 text-slate-600 dark:text-slate-300">{seed.idea}</p>
      <div className="flex items-center gap-3">
        <span className="bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 px-2.5 py-1 rounded-full text-xs font-medium border border-amber-100 dark:border-amber-800">
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
        <span className="text-xs bg-gradient-to-r from-amber-500 to-orange-500 text-white px-2.5 py-1 rounded-full font-bold shadow-sm flex items-center gap-1">
          <Lightbulb className="w-3 h-3" />
          Creative
        </span>
      }
      onExpandChange={setIsExpanded}
    >
      <div className="space-y-8 p-2">
        {/* Full Idea */}
        <div className="p-6 rounded-2xl bg-gradient-to-br from-amber-50/50 to-orange-50/50 dark:from-amber-900/10 dark:to-orange-900/10 border border-amber-100 dark:border-amber-800/50">
          <h4 className="text-xs font-bold text-amber-900 dark:text-amber-100 uppercase tracking-wider mb-3 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-500" />
            Creative Concept
          </h4>
          <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-lg">{seed.idea}</p>
        </div>

        {/* Format & Details */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1 p-5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50">
            <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <FileText className="w-4 h-4 text-amber-500" />
              Format
            </h4>
            <span className="inline-flex items-center gap-2 bg-white dark:bg-slate-700 text-amber-700 dark:text-amber-300 px-3 py-1.5 rounded-lg border border-amber-100 dark:border-amber-900/30 font-medium shadow-sm">
              {seed.format}
            </span>
          </div>
          
          <div className="md:col-span-2 p-5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm">
            <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">Execution Details</h4>
            <p className="text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">{seed.details}</p>
          </div>
        </div>

        {/* Content Timeline */}
        <div className="pt-6 border-t border-slate-100 dark:border-slate-800">
          <SeedTimeline tasks={tasks} posts={posts} loading={loading} />
        </div>
      </div>
    </ExpandableCard>
  )
}