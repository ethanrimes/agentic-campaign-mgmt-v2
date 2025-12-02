// frontend/components/seeds/TrendSeedCard.tsx

'use client'

import { useState, useEffect } from 'react'
import ExpandableCard from '@/components/common/ExpandableCard'
import SeedTimeline from './SeedTimeline'
import { formatRelativeTime, formatDateTime } from '@/lib/utils'
import { Hash, User, Activity } from 'lucide-react'
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
      <p className="text-sm line-clamp-2 text-gray-700">{seed.description}</p>
      <div className="flex flex-wrap gap-2">
        {seed.hashtags.slice(0, 5).map((tag, i) => (
          <span key={i} className="text-xs bg-gradient-to-r from-purple-50 to-pink-50 text-purple-700 px-3 py-1.5 rounded-full font-medium border border-purple-100">
            #{tag}
          </span>
        ))}
        {seed.hashtags.length > 5 && (
          <span className="text-xs bg-gray-100 text-gray-700 px-3 py-1.5 rounded-full font-medium">
            +{seed.hashtags.length - 5} more
          </span>
        )}
        {toolCallCount > 0 && (
          <span className="flex items-center gap-1.5 bg-green-50 text-green-700 px-3 py-1.5 rounded-full text-xs font-medium border border-green-100">
            <Activity className="w-3.5 h-3.5" />
            {toolCallCount} tool calls
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
      <div className="space-y-6">
        {/* Description */}
        <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-100">
          <h4 className="text-sm font-bold text-gray-900 mb-2 flex items-center gap-2">
            <div className="w-1 h-4 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></div>
            Trend Analysis
          </h4>
          <p className="text-gray-700 leading-relaxed whitespace-pre-line">{seed.description}</p>
        </div>

        {/* Hashtags */}
        {seed.hashtags.length > 0 && (
          <div>
            <h4 className="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Hash className="w-4 h-4 text-white" />
              </div>
              Trending Hashtags ({seed.hashtags.length})
            </h4>
            <div className="flex flex-wrap gap-2">
              {seed.hashtags.map((tag, i) => (
                <span key={i} className="group text-sm bg-gradient-to-r from-purple-50 to-pink-50 text-purple-700 px-4 py-2 rounded-full border border-purple-100 hover:shadow-lg hover:scale-105 transition-all cursor-default font-medium">
                  #{tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Referenced Posts */}
        {seed.posts && seed.posts.length > 0 && (
          <div>
            <h4 className="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center text-white text-xs font-bold">
                {seed.posts.length}
              </div>
              Referenced Posts
            </h4>
            <div className="space-y-3">
              {seed.posts.map((post: any, i: number) => (
                <div key={i} className="group p-4 bg-white rounded-xl border border-gray-200 shadow-soft hover:shadow-glow hover:border-purple-200 transition-all">
                  <p className="text-sm text-gray-700 leading-relaxed line-clamp-2 mb-2">{post.text || 'No caption'}</p>
                  {post.link && (
                    <a
                      href={post.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-purple-600 hover:text-purple-700 font-medium inline-flex items-center gap-1 group-hover:underline"
                    >
                      View post →
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
            <h4 className="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg flex items-center justify-center text-white text-xs font-bold">
                {seed.tool_calls.length}
              </div>
              Tool Executions
            </h4>
            <div className="space-y-3">
              {seed.tool_calls.map((call, i) => (
                <div key={i} className="group p-4 bg-white rounded-xl border border-gray-200 shadow-soft hover:shadow-glow hover:border-purple-200 transition-all overflow-hidden">
                  <div className="flex items-start justify-between mb-3">
                    <span className="inline-flex items-center gap-2 text-sm font-bold text-gray-900 bg-gradient-to-r from-purple-50 to-pink-50 px-3 py-1.5 rounded-lg border border-purple-100">
                      {call.tool_name}
                    </span>
                    <span className="text-xs text-gray-500 font-medium">
                      {formatDateTime(call.timestamp)}
                    </span>
                  </div>

                  {/* Arguments */}
                  <div className="mb-3">
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Arguments:</p>
                    <pre className="text-xs text-gray-700 bg-gray-50 p-3 rounded-lg border border-gray-200 overflow-x-auto font-mono">
                      {JSON.stringify(call.arguments, null, 2)}
                    </pre>
                  </div>

                  {/* Result */}
                  <div>
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Result:</p>
                    <pre className="text-xs text-gray-700 bg-gradient-to-br from-green-50 to-emerald-50 p-3 rounded-lg border border-green-100 overflow-x-auto max-h-40 font-mono">
                      {JSON.stringify(call.result, null, 2)}
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Content Timeline */}
        <SeedTimeline tasks={tasks} posts={posts} loading={loading} />
      </div>
    </ExpandableCard>
  )
}
