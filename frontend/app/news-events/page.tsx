// frontend/app/news-events/page.tsx

'use client'

import { useState, useEffect } from 'react'
import { getNewsEventSeeds } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'
import NewsEventCard from '@/components/seeds/NewsEventCard'
import { Database, Globe } from 'lucide-react'
import type { NewsEventSeed } from '@/types'

export default function NewsEventsPage() {
  const { selectedAsset } = useBusinessAsset()
  const [seeds, setSeeds] = useState<NewsEventSeed[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadSeeds() {
      if (!selectedAsset) return

      try {
        setLoading(true)
        const data = await getNewsEventSeeds(selectedAsset.id)
        setSeeds(data)
      } catch (error) {
        console.error('Failed to load news event seeds:', error)
      } finally {
        setLoading(false)
      }
    }

    loadSeeds()
  }, [selectedAsset])

  if (!selectedAsset || loading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="text-center py-16">
          <Database className="w-16 h-16 text-blue-400 mx-auto mb-4 animate-pulse" />
          <p className="text-lg text-slate-600 dark:text-slate-400">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto animate-fade-in pb-20">
      <div className="relative mb-10">
        <div className="glass-panel p-8 bg-white/80 dark:bg-slate-900/80">
          <div className="flex items-center gap-4 mb-3">
            <div className="w-14 h-14 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
              <Globe className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                News Event Seeds
              </h1>
              <p className="text-slate-600 dark:text-slate-400 mt-1 font-medium">
                Canonical news events discovered and consolidated from research agents
              </p>
            </div>
          </div>
          <div className="mt-6 flex items-center gap-3">
            <div className="bg-slate-100 dark:bg-slate-800 px-4 py-2 rounded-full border border-slate-200 dark:border-slate-700">
              <span className="text-sm font-bold text-slate-900 dark:text-white">{seeds.length}</span>
              <span className="text-sm text-slate-600 dark:text-slate-400 ml-1">total events</span>
            </div>
          </div>
        </div>
      </div>

      {seeds.length === 0 ? (
        <div className="text-center py-20 glass-panel bg-white/60 dark:bg-slate-900/60">
          <div className="relative inline-block mb-6">
            <Database className="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto" />
          </div>
          <p className="text-lg font-semibold text-slate-900 dark:text-white mb-2">No news event seeds found</p>
          <p className="text-sm text-slate-600 dark:text-slate-400 max-w-md mx-auto">
            Run the news ingestion CLI commands to populate this database with the latest news events
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {seeds.map((seed, index) => (
            <div key={seed.id} className="animate-slide-up" style={{ animationDelay: `${index * 50}ms` }}>
              <NewsEventCard seed={seed} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
