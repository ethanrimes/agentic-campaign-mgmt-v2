// frontend/components/seeds/SeedModal.tsx

'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, MapPin, Calendar, ExternalLink, Hash, FileText, CheckCircle2, Clock, AlertCircle } from 'lucide-react'
import type { NewsEventSeed, TrendSeed, UngroundedSeed } from '@/types'
import { formatDate, formatRelativeTime, formatDateTime } from '@/lib/utils'
import { getContentCreationTasksBySeed, getCompletedPostsBySeed } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'
import SeedTimeline from './SeedTimeline'

interface SeedModalProps {
  seed: NewsEventSeed | TrendSeed | UngroundedSeed
  seedType: 'news_event' | 'trend' | 'ungrounded'
  postCount: number
  onClose: () => void
}

export default function SeedModal({ seed, seedType, postCount, onClose }: SeedModalProps) {
  const { selectedAsset } = useBusinessAsset()
  const [tasks, setTasks] = useState<any[]>([])
  const [posts, setPosts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      if (!selectedAsset) return
      try {
        setLoading(true)
        const [tasksData, postsData] = await Promise.all([
          getContentCreationTasksBySeed(seed.id, seedType, selectedAsset.id),
          getCompletedPostsBySeed(seed.id, seedType, selectedAsset.id),
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
  }, [seed.id, seedType, selectedAsset])

  const newsEventSeed = seedType === 'news_event' ? seed as NewsEventSeed : null
  const trendSeed = seedType === 'trend' ? seed as TrendSeed : null
  const ungroundedSeed = seedType === 'ungrounded' ? seed as UngroundedSeed : null

  const seedName = newsEventSeed?.name || trendSeed?.name || ungroundedSeed?.idea || 'Content Seed'

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="glass-panel w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl"
          initial={{ scale: 0.95, y: 20, opacity: 0 }}
          animate={{ scale: 1, y: 0, opacity: 1 }}
          exit={{ scale: 0.95, y: 20, opacity: 0 }}
          transition={{ type: "spring", duration: 0.5 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="p-6 border-b border-slate-200/50 dark:border-slate-700/50 flex items-start justify-between bg-white/50 dark:bg-slate-900/50 backdrop-blur-md">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{seedName}</h2>
                {postCount > 0 && (
                  <div className="bg-gradient-to-r from-green-500 to-emerald-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-sm">
                    {postCount} {postCount === 1 ? 'post' : 'posts'}
                  </div>
                )}
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400 flex items-center gap-2">
                <Clock className="w-3.5 h-3.5" />
                Created {formatRelativeTime(seed.created_at)}
                {(trendSeed || ungroundedSeed) && ` • ${(trendSeed?.created_by || ungroundedSeed?.created_by)}`}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-8 space-y-8 bg-white/40 dark:bg-slate-900/40">
            {/* News Event Seed Content */}
            {newsEventSeed && (
              <>
                {/* Description */}
                <div className="p-6 rounded-2xl bg-blue-50/50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-800">
                  <h4 className="text-sm font-bold text-blue-900 dark:text-blue-100 mb-3 flex items-center gap-2">
                    <div className="w-1 h-4 bg-blue-500 rounded-full"></div>
                    Description
                  </h4>
                  <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-lg">{newsEventSeed.description}</p>
                </div>

                {/* Event Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="p-5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm">
                    <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-blue-500" />
                      Location
                    </h4>
                    <p className="text-slate-900 dark:text-white font-medium">{newsEventSeed.location}</p>
                  </div>
                  {newsEventSeed.start_time && (
                    <div className="p-5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm">
                      <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-purple-500" />
                        Date
                      </h4>
                      <p className="text-slate-900 dark:text-white font-medium">
                        {formatDate(newsEventSeed.start_time)}
                        {newsEventSeed.end_time && ` - ${formatDate(newsEventSeed.end_time)}`}
                      </p>
                    </div>
                  )}
                </div>

                {/* Sources */}
                {newsEventSeed.sources && newsEventSeed.sources.length > 0 && (
                  <div>
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                      <div className="w-6 h-6 bg-primary-500 rounded-lg flex items-center justify-center text-white text-xs font-bold">
                        {newsEventSeed.sources.length}
                      </div>
                      Research Sources
                    </h4>
                    <div className="space-y-3">
                      {newsEventSeed.sources.map((source, index) => (
                        <div key={index} className="group p-4 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-primary-300 dark:hover:border-primary-700 transition-colors">
                          <div className="flex items-start justify-between gap-3 mb-2">
                            <a
                              href={source.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-primary-600 dark:text-primary-400 font-semibold flex items-center gap-2 truncate hover:underline"
                            >
                              {new URL(source.url).hostname}
                              <ExternalLink className="w-3.5 h-3.5 flex-shrink-0" />
                            </a>
                            <span className="text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-2 py-1 rounded-full whitespace-nowrap font-medium">
                              {source.found_by}
                            </span>
                          </div>
                          <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">{source.key_findings}</p>
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
                <div className="p-6 rounded-2xl bg-purple-50/50 dark:bg-purple-900/10 border border-purple-100 dark:border-purple-800">
                  <h4 className="text-sm font-bold text-purple-900 dark:text-purple-100 mb-3 flex items-center gap-2">
                    <div className="w-1 h-4 bg-purple-500 rounded-full"></div>
                    Trend Analysis
                  </h4>
                  <p className="text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line text-lg">{trendSeed.description}</p>
                </div>

                {/* Hashtags */}
                {trendSeed.hashtags && trendSeed.hashtags.length > 0 && (
                  <div>
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                      <div className="w-6 h-6 bg-purple-500 rounded-lg flex items-center justify-center text-white text-xs">
                        #
                      </div>
                      Hashtags ({trendSeed.hashtags.length})
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {trendSeed.hashtags.map((tag, i) => (
                        <span key={i} className="text-sm bg-white dark:bg-slate-800 text-purple-600 dark:text-purple-400 px-4 py-2 rounded-full border border-purple-100 dark:border-purple-900 font-medium shadow-sm">
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
                <div className="p-6 rounded-2xl bg-amber-50/50 dark:bg-amber-900/10 border border-amber-100 dark:border-amber-800">
                  <h4 className="text-sm font-bold text-amber-900 dark:text-amber-100 mb-3 flex items-center gap-2">
                    <div className="w-1 h-4 bg-amber-500 rounded-full"></div>
                    Idea
                  </h4>
                  <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-lg">{ungroundedSeed.idea}</p>
                </div>

                {/* Format & Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="p-5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm">
                    <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-amber-500" />
                      Format
                    </h4>
                    <p className="text-slate-900 dark:text-white font-medium">{ungroundedSeed.format}</p>
                  </div>
                  <div className="p-5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm col-span-full">
                    <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">Details</h4>
                    <p className="text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">{ungroundedSeed.details}</p>
                  </div>
                </div>
              </>
            )}

            {/* Content Timeline */}
            <div className="pt-8 border-t border-slate-200 dark:border-slate-700">
              <SeedTimeline
                tasks={tasks}
                posts={posts}
                loading={loading}
              />
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
