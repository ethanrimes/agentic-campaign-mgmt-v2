// frontend/app/content-seeds/page.tsx

'use client'

import { useState, useEffect } from 'react'
import { getNewsEventSeeds, getTrendSeeds, getUngroundedSeeds, getPostCountsBySeed } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'
import { Database, TrendingUp, Lightbulb, Sparkles } from 'lucide-react'
import ContentSeedsGrid from '@/components/seeds/ContentSeedsGrid'
import type { NewsEventSeed, TrendSeed, UngroundedSeed } from '@/types'

export default function ContentSeedsPage() {
  const { selectedAsset } = useBusinessAsset()
  const [newsSeeds, setNewsSeeds] = useState<NewsEventSeed[]>([])
  const [trendSeeds, setTrendSeeds] = useState<TrendSeed[]>([])
  const [ungroundedSeeds, setUngroundedSeeds] = useState<UngroundedSeed[]>([])
  const [postCounts, setPostCounts] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      if (!selectedAsset) return

      try {
        setLoading(true)
        const [news, trends, ungrounded, counts] = await Promise.all([
          getNewsEventSeeds(selectedAsset.id),
          getTrendSeeds(selectedAsset.id),
          getUngroundedSeeds(selectedAsset.id),
          getPostCountsBySeed(selectedAsset.id),
        ])
        setNewsSeeds(news)
        setTrendSeeds(trends)
        setUngroundedSeeds(ungrounded)
        setPostCounts(counts)
      } catch (error) {
        console.error('Failed to load content seeds:', error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [selectedAsset])

  if (!selectedAsset || loading) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="text-center py-16">
          <Sparkles className="w-16 h-16 text-cyan-400 mx-auto mb-4 animate-pulse" />
          <p className="text-lg text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  const totalSeeds = newsSeeds.length + trendSeeds.length + ungroundedSeeds.length

  return (
    <div className="max-w-7xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="relative mb-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-100/30 via-blue-100/20 to-slate-100/30 rounded-3xl blur-3xl"></div>
        <div className="relative bg-white rounded-2xl p-8 border border-slate-200 shadow-xl">
          <div className="flex items-center gap-4 mb-3">
            <div className="relative">
              <div className="w-14 h-14 bg-gradient-to-br from-cyan-600 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
                <Sparkles className="w-7 h-7 text-white" />
              </div>
              <div className="absolute inset-0 bg-cyan-500 rounded-2xl blur-xl opacity-30"></div>
            </div>
            <div>
              <h1 className="text-4xl font-bold text-slate-900">
                Content Seeds
              </h1>
              <p className="text-slate-600 mt-1">
                All content ideas from news events, social trends, and creative ideation
              </p>
            </div>
          </div>
          <div className="mt-6 flex items-center gap-3 flex-wrap">
            <div className="bg-slate-100 px-4 py-2 rounded-full border border-slate-200">
              <span className="text-sm font-bold text-slate-900">{totalSeeds}</span>
              <span className="text-sm text-slate-600 ml-1">total seeds</span>
            </div>
            <div className="bg-blue-50 px-4 py-2 rounded-full border border-blue-200">
              <span className="text-sm font-bold text-blue-900">{newsSeeds.length}</span>
              <span className="text-sm text-blue-700 ml-1">news events</span>
            </div>
            <div className="bg-purple-50 px-4 py-2 rounded-full border border-purple-200">
              <span className="text-sm font-bold text-purple-900">{trendSeeds.length}</span>
              <span className="text-sm text-purple-700 ml-1">trends</span>
            </div>
            <div className="bg-amber-50 px-4 py-2 rounded-full border border-amber-200">
              <span className="text-sm font-bold text-amber-900">{ungroundedSeeds.length}</span>
              <span className="text-sm text-amber-700 ml-1">ungrounded</span>
            </div>
          </div>
        </div>
      </div>

      {totalSeeds === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-slate-200 shadow-xl">
          <div className="relative inline-block mb-6">
            <Sparkles className="w-16 h-16 text-slate-400 mx-auto" />
            <div className="absolute inset-0 bg-slate-500 blur-2xl opacity-20"></div>
          </div>
          <p className="text-lg font-semibold text-slate-900 mb-2">No content seeds found</p>
          <p className="text-sm text-slate-600 max-w-md mx-auto">
            Run the seed generation agents to populate the database with content ideas
          </p>
        </div>
      ) : (
        <ContentSeedsGrid
          newsSeeds={newsSeeds}
          trendSeeds={trendSeeds}
          ungroundedSeeds={ungroundedSeeds}
          postCounts={postCounts}
        />
      )}
    </div>
  )
}
