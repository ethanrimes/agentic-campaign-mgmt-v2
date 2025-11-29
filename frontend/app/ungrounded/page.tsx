// frontend/app/ungrounded/page.tsx

'use client'

import { useState, useEffect } from 'react'
import { getUngroundedSeeds } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'
import UngroundedSeedCard from '@/components/seeds/UngroundedSeedCard'
import { Lightbulb } from 'lucide-react'
import type { UngroundedSeed } from '@/types'

export default function UngroundedPage() {
  const { selectedAsset } = useBusinessAsset()
  const [seeds, setSeeds] = useState<UngroundedSeed[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadSeeds() {
      if (!selectedAsset) return

      try {
        setLoading(true)
        const data = await getUngroundedSeeds(selectedAsset.id)
        setSeeds(data)
      } catch (error) {
        console.error('Failed to load ungrounded seeds:', error)
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
          <Lightbulb className="w-16 h-16 text-amber-400 mx-auto mb-4 animate-pulse" />
          <p className="text-lg text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto animate-fade-in">
      <div className="relative mb-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-amber-100/50 via-orange-100/30 to-amber-100/50 rounded-3xl blur-3xl"></div>
        <div className="relative glass rounded-2xl p-8 border border-white/50 shadow-soft">
          <div className="flex items-center gap-4 mb-3">
            <div className="relative">
              <div className="w-14 h-14 bg-gradient-to-br from-amber-500 to-orange-500 rounded-2xl flex items-center justify-center shadow-lg">
                <Lightbulb className="w-7 h-7 text-white" />
              </div>
              <div className="absolute inset-0 bg-amber-500 rounded-2xl blur-xl opacity-30"></div>
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
                Ungrounded Seeds
              </h1>
              <p className="text-gray-600 mt-1">
                Creative content ideas not tied to news or social media trends
              </p>
            </div>
          </div>
          <div className="mt-6 flex items-center gap-3">
            <div className="glass px-4 py-2 rounded-full border border-white/30">
              <span className="text-sm font-bold text-gray-900">{seeds.length}</span>
              <span className="text-sm text-gray-600 ml-1">creative ideas</span>
            </div>
          </div>
        </div>
      </div>

      {seeds.length === 0 ? (
        <div className="text-center py-16 glass rounded-2xl border border-white/50 shadow-soft">
          <div className="relative inline-block mb-6">
            <Lightbulb className="w-16 h-16 text-amber-400 mx-auto" />
            <div className="absolute inset-0 bg-amber-500 blur-2xl opacity-20"></div>
          </div>
          <p className="text-lg font-semibold text-gray-900 mb-2">No ungrounded seeds found</p>
          <p className="text-sm text-gray-600 max-w-md mx-auto">
            Run the ungrounded generation CLI command to create original creative ideas
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {seeds.map((seed, index) => (
            <div key={seed.id} className="animate-slide-up" style={{ animationDelay: `${index * 50}ms` }}>
              <UngroundedSeedCard seed={seed} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
