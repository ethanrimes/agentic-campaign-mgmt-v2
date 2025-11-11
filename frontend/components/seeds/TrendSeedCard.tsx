// frontend/components/seeds/TrendSeedCard.tsx

'use client'

import { useState, useEffect } from 'react'
import ExpandableCard from '@/components/common/ExpandableCard'
import SeedTimeline from './SeedTimeline'
import { formatRelativeTime } from '@/lib/utils'
import { Hash, User } from 'lucide-react'
import type { TrendSeed } from '@/types'
import { getContentCreationTasksBySeed, getCompletedPostsBySeed } from '@/lib/api'

interface TrendSeedCardProps {
  seed: TrendSeed
}

export default function TrendSeedCard({ seed }: TrendSeedCardProps) {
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
      <div className="flex flex-wrap gap-2">
        {seed.hashtags.slice(0, 5).map((tag, i) => (
          <span key={i} className="text-xs bg-purple-50 text-purple-700 px-2 py-1 rounded-full">
            #{tag}
          </span>
        ))}
        {seed.hashtags.length > 5 && (
          <span className="text-xs text-gray-500">+{seed.hashtags.length - 5} more</span>
        )}
      </div>
    </div>
  )

  return (
    <ExpandableCard
      title={seed.name}
      subtitle={`Created ${formatRelativeTime(seed.created_at)} • ${seed.created_by}`}
      preview={preview}
    >
      <div className="space-y-6" onClick={() => setLoading(true)}>
        {/* Description */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Analysis</h4>
          <p className="text-gray-700 whitespace-pre-line">{seed.description}</p>
        </div>

        {/* Hashtags */}
        {seed.hashtags.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Hash className="w-4 h-4" />
              Hashtags ({seed.hashtags.length})
            </h4>
            <div className="flex flex-wrap gap-2">
              {seed.hashtags.map((tag, i) => (
                <span key={i} className="text-sm bg-purple-50 text-purple-700 px-3 py-1 rounded-full">
                  #{tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Referenced Posts */}
        {seed.posts && seed.posts.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3">
              Referenced Posts ({seed.posts.length})
            </h4>
            <div className="space-y-2">
              {seed.posts.map((post: any, i: number) => (
                <div key={i} className="p-3 bg-gray-50 rounded-md border border-gray-200">
                  <p className="text-sm text-gray-700 line-clamp-2">{post.text || 'No caption'}</p>
                  {post.link && (
                    <a
                      href={post.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-primary-600 hover:text-primary-700 mt-1 inline-block"
                    >
                      View post →
                    </a>
                  )}
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
