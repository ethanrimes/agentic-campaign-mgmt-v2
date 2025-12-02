// frontend/components/seeds/TrendSeedCard.tsx

'use client'

import { useState, useEffect } from 'react'
import ExpandableCard from '@/components/common/ExpandableCard'
import SeedTimeline from './SeedTimeline'
import { formatRelativeTime, formatDateTime } from '@/lib/utils'
import { Hash, User, Activity, TrendingUp, ExternalLink, Clock, Code } from 'lucide-react'
import type { TrendSeed } from '@/types'
import { getContentCreationTasksBySeed, getCompletedPostsBySeed } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'

interface TrendSeedCardProps {
  seed: TrendSeed
}

export default function TrendSeedCard({ seed }: TrendSeedCardProps) {
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
          getContentCreationTasksBySeed(seed.id, 'trend', selectedAsset.id),
          getCompletedPostsBySeed(seed.id, 'trend', selectedAsset.id),
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

  const toolCallCount = seed.tool_calls?.length || 0

  const preview = (
    <div className="space-y-3">
      <p className="text-sm line-clamp-2 text-slate-600 dark:text-slate-300">{seed.description}</p>
      <div className="flex flex-wrap gap-2">
        {seed.hashtags.slice(0, 5).map((tag, i) => (
          <span key={i} className="text-xs bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 px-2.5 py-1 rounded-full font-medium border border-purple-100 dark:border-purple-800">
            #{tag}
          </span>
        ))}
        {seed.hashtags.length > 5 && (
          <span className="text-xs bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 px-2.5 py-1 rounded-full font-medium border border-slate-200 dark:border-slate-700">
            +{seed.hashtags.length - 5} more
          </span>
        )}
        {toolCallCount > 0 && (
          <span className="flex items-center gap-1.5 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 px-2.5 py-1 rounded-full text-xs font-medium border border-green-100 dark:border-green-800">
            <Activity className="w-3 h-3" />
            {toolCallCount} tools
          </span>
        )}
      </div>
    </div>
  )

  return (
    <ExpandableCard
      title={seed.name}
      subtitle={`Created ${formatRelativeTime(seed.created_at)} • ${seed.created_by}`}
      preview={preview}
      onExpandChange={setIsExpanded}
    >
      <div className="space-y-8 p-2">
        {/* Description */}
        <div className="p-6 rounded-2xl bg-gradient-to-br from-purple-50/50 to-pink-50/50 dark:from-purple-900/10 dark:to-pink-900/10 border border-purple-100 dark:border-purple-800/50">
          <h4 className="text-xs font-bold text-purple-900 dark:text-purple-100 uppercase tracking-wider mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-purple-500" />
            Trend Analysis
          </h4>
          <p className="text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line text-base">{seed.description}</p>
        </div>

        {/* Hashtags */}
        {seed.hashtags.length > 0 && (
          <div>
            <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Hash className="w-4 h-4 text-purple-500" />
              Trending Hashtags ({seed.hashtags.length})
            </h4>
            <div className="flex flex-wrap gap-2">
              {seed.hashtags.map((tag, i) => (
                <span key={i} className="group text-sm bg-white dark:bg-slate-800 text-purple-600 dark:text-purple-400 px-3 py-1.5 rounded-lg border border-purple-100 dark:border-purple-900/30 hover:shadow-md hover:border-purple-300 dark:hover:border-purple-700 transition-all cursor-default font-medium">
                  #{tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Referenced Posts */}
        {seed.posts && seed.posts.length > 0 && (
          <div>
            <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <div className="w-5 h-5 bg-blue-500 rounded-md flex items-center justify-center text-white text-[10px] font-bold">
                {seed.posts.length}
              </div>
              Referenced Posts
            </h4>
            <div className="space-y-3">
              {seed.posts.map((post: any, i: number) => (
                <div key={i} className="group p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50 hover:bg-white dark:hover:bg-slate-800 hover:shadow-md transition-all">
                  <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed line-clamp-2 mb-2 italic">"{post.text || 'No caption'}"</p>
                  {post.link && (
                    <a
                      href={post.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-primary-600 dark:text-primary-400 font-medium inline-flex items-center gap-1 hover:underline"
                    >
                      View original post <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tool Calls */}
        {seed.tool_calls && seed.tool_calls.length > 0 && (
          <div>
            <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Code className="w-4 h-4 text-green-500" />
              Tool Executions
            </h4>
            <div className="space-y-3">
              {seed.tool_calls.map((call, i) => (
                <div key={i} className="group p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-green-300 dark:hover:border-green-700 transition-all overflow-hidden">
                  <div className="flex items-start justify-between mb-3">
                    <span className="inline-flex items-center gap-2 text-xs font-bold text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded-md border border-slate-200 dark:border-slate-700">
                      {call.tool_name}
                    </span>
                    <span className="text-xs text-slate-400 dark:text-slate-500 font-mono flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatDateTime(call.timestamp)}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div>
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Arguments</p>
                      <pre className="text-[11px] text-slate-600 dark:text-slate-300 bg-slate-50 dark:bg-slate-800 p-3 rounded-lg border border-slate-100 dark:border-slate-700 overflow-x-auto font-mono custom-scrollbar">
                        {JSON.stringify(call.arguments, null, 2)}
                      </pre>
                    </div>
                    <div>
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Result</p>
                      <pre className="text-[11px] text-slate-600 dark:text-slate-300 bg-slate-50 dark:bg-slate-800 p-3 rounded-lg border border-slate-100 dark:border-slate-700 overflow-x-auto max-h-32 font-mono custom-scrollbar">
                        {JSON.stringify(call.result, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Content Timeline */}
        <div className="pt-6 border-t border-slate-100 dark:border-slate-800">
          <SeedTimeline tasks={tasks} posts={posts} loading={loading} />
        </div>
      </div>
    </ExpandableCard>
  )
}
