// frontend/components/seeds/SeedModal.tsx

'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, MapPin, Calendar, ExternalLink, Hash, FileText, CheckCircle2, Clock, AlertCircle } from 'lucide-react'
import type { NewsEventSeed, TrendSeed, UngroundedSeed } from '@/types'
import { formatDate, formatRelativeTime, formatDateTime } from '@/lib/utils'
import { getContentCreationTasksBySeed, getCompletedPostsBySeed } from '@/lib/api'
import SeedTimeline from './SeedTimeline'

interface SeedModalProps {
  seed: NewsEventSeed | TrendSeed | UngroundedSeed
  seedType: 'news_event' | 'trend' | 'ungrounded'
  postCount: number
  onClose: () => void
}

export default function SeedModal({ seed, seedType, postCount, onClose }: SeedModalProps) {
  const [tasks, setTasks] = useState<any[]>([])
  const [posts, setPosts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        const [tasksData, postsData] = await Promise.all([
          getContentCreationTasksBySeed(seed.id),
          getCompletedPostsBySeed(seed.id, seedType),
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
  }, [seed.id, seedType])

  const newsEventSeed = seedType === 'news_event' ? seed as NewsEventSeed : null
  const trendSeed = seedType === 'trend' ? seed as TrendSeed : null
  const ungroundedSeed = seedType === 'ungrounded' ? seed as UngroundedSeed : null

  const seedName = newsEventSeed?.name || trendSeed?.name || ungroundedSeed?.idea || 'Content Seed'

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col"
          initial={{ scale: 0.9, y: 20 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.9, y: 20 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="p-6 border-b border-slate-200 flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-2xl font-bold text-slate-900">{seedName}</h2>
                {postCount > 0 && (
                  <div className="bg-gradient-to-br from-green-500 to-emerald-600 text-white text-xs font-bold px-3 py-1.5 rounded-full shadow-lg">
                    {postCount} {postCount === 1 ? 'post' : 'posts'}
                  </div>
                )}
              </div>
              <p className="text-sm text-slate-600">
                Created {formatRelativeTime(seed.created_at)}
                {(trendSeed || ungroundedSeed) && ` • ${(trendSeed?.created_by || ungroundedSeed?.created_by)}`}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600 transition-colors p-2 hover:bg-slate-100 rounded-lg"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* News Event Seed Content */}
            {newsEventSeed && (
              <>
                {/* Description */}
                <div className="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border border-blue-100">
                  <h4 className="text-sm font-bold text-gray-900 mb-2 flex items-center gap-2">
                    <div className="w-1 h-4 bg-gradient-to-b from-blue-500 to-cyan-500 rounded-full"></div>
                    Description
                  </h4>
                  <p className="text-gray-700 leading-relaxed">{newsEventSeed.description}</p>
                </div>

                {/* Event Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-soft">
                    <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-blue-600" />
                      Location
                    </h4>
                    <p className="text-gray-900 font-medium">{newsEventSeed.location}</p>
                  </div>
                  {newsEventSeed.start_time && (
                    <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-soft">
                      <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-purple-600" />
                        Date
                      </h4>
                      <p className="text-gray-900 font-medium">
                        {formatDate(newsEventSeed.start_time)}
                        {newsEventSeed.end_time && ` - ${formatDate(newsEventSeed.end_time)}`}
                      </p>
                    </div>
                  )}
                </div>

                {/* Sources */}
                {newsEventSeed.sources && newsEventSeed.sources.length > 0 && (
                  <div>
                    <h4 className="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
                      <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center text-white text-xs font-bold">
                        {newsEventSeed.sources.length}
                      </div>
                      Research Sources
                    </h4>
                    <div className="space-y-3">
                      {newsEventSeed.sources.map((source, index) => (
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
              </>
            )}

            {/* Trend Seed Content */}
            {trendSeed && (
              <>
                {/* Description */}
                <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-100">
                  <h4 className="text-sm font-bold text-gray-900 mb-2 flex items-center gap-2">
                    <div className="w-1 h-4 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></div>
                    Trend Analysis
                  </h4>
                  <p className="text-gray-700 leading-relaxed whitespace-pre-line">{trendSeed.description}</p>
                </div>

                {/* Hashtags */}
                {trendSeed.hashtags && trendSeed.hashtags.length > 0 && (
                  <div>
                    <h4 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
                      <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center text-white text-xs">
                        #
                      </div>
                      Hashtags ({trendSeed.hashtags.length})
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {trendSeed.hashtags.map((tag, i) => (
                        <span key={i} className="text-sm bg-gradient-to-r from-purple-50 to-pink-50 text-purple-700 px-4 py-2 rounded-full border border-purple-100 font-medium">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Ungrounded Seed Content */}
            {ungroundedSeed && (
              <>
                {/* Full Idea */}
                <div className="p-4 bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl border border-amber-100">
                  <h4 className="text-sm font-bold text-gray-900 mb-2 flex items-center gap-2">
                    <div className="w-1 h-4 bg-gradient-to-b from-amber-500 to-orange-500 rounded-full"></div>
                    Idea
                  </h4>
                  <p className="text-gray-700 leading-relaxed">{ungroundedSeed.idea}</p>
                </div>

                {/* Format & Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-soft">
                    <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-amber-600" />
                      Format
                    </h4>
                    <p className="text-gray-900 font-medium">{ungroundedSeed.format}</p>
                  </div>
                  <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-soft col-span-full">
                    <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Details</h4>
                    <p className="text-gray-700 leading-relaxed whitespace-pre-line">{ungroundedSeed.details}</p>
                  </div>
                </div>
              </>
            )}

            {/* Content Timeline */}
            <SeedTimeline
              tasks={tasks}
              posts={posts}
              loading={loading}
            />
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
