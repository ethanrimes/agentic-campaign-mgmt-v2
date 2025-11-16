// frontend/app/content-seeds/page.tsx

import { getNewsEventSeeds, getTrendSeeds, getUngroundedSeeds } from '@/lib/api'
import { Database, TrendingUp, Lightbulb, Sparkles } from 'lucide-react'
import NewsEventCard from '@/components/seeds/NewsEventCard'
import TrendSeedCard from '@/components/seeds/TrendSeedCard'
import UngroundedSeedCard from '@/components/seeds/UngroundedSeedCard'

export const dynamic = 'force-dynamic'

export default async function ContentSeedsPage() {
  const [newsSeeds, trendSeeds, ungroundedSeeds] = await Promise.all([
    getNewsEventSeeds(),
    getTrendSeeds(),
    getUngroundedSeeds(),
  ])

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
        <div className="space-y-12">
          {/* News Events Section */}
          {newsSeeds.length > 0 && (
            <section>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-xl flex items-center justify-center shadow-lg">
                  <Database className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-slate-900">News Events</h2>
                <span className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium">
                  {newsSeeds.length}
                </span>
              </div>
              <div className="grid grid-cols-1 gap-4">
                {newsSeeds.map((seed, index) => (
                  <div key={seed.id} className="animate-slide-up" style={{ animationDelay: `${index * 30}ms` }}>
                    <NewsEventCard seed={seed} />
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Trends Section */}
          {trendSeeds.length > 0 && (
            <section>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-pink-600 rounded-xl flex items-center justify-center shadow-lg">
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-slate-900">Social Media Trends</h2>
                <span className="text-sm bg-purple-100 text-purple-700 px-3 py-1 rounded-full font-medium">
                  {trendSeeds.length}
                </span>
              </div>
              <div className="grid grid-cols-1 gap-4">
                {trendSeeds.map((seed, index) => (
                  <div key={seed.id} className="animate-slide-up" style={{ animationDelay: `${index * 30}ms` }}>
                    <TrendSeedCard seed={seed} />
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Ungrounded Section */}
          {ungroundedSeeds.length > 0 && (
            <section>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-amber-600 to-orange-600 rounded-xl flex items-center justify-center shadow-lg">
                  <Lightbulb className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-slate-900">Creative Ideas</h2>
                <span className="text-sm bg-amber-100 text-amber-700 px-3 py-1 rounded-full font-medium">
                  {ungroundedSeeds.length}
                </span>
              </div>
              <div className="grid grid-cols-1 gap-4">
                {ungroundedSeeds.map((seed, index) => (
                  <div key={seed.id} className="animate-slide-up" style={{ animationDelay: `${index * 30}ms` }}>
                    <UngroundedSeedCard seed={seed} />
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  )
}
