// frontend/app/trends/page.tsx

import { getTrendSeeds } from '@/lib/api'
import TrendSeedCard from '@/components/seeds/TrendSeedCard'
import { TrendingUp } from 'lucide-react'

export const dynamic = 'force-dynamic'

export default async function TrendsPage() {
  const seeds = await getTrendSeeds()

  return (
    <div className="max-w-6xl mx-auto animate-fade-in">
      <div className="relative mb-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-100/50 via-pink-100/30 to-purple-100/50 rounded-3xl blur-3xl"></div>
        <div className="relative glass rounded-2xl p-8 border border-white/50 shadow-soft">
          <div className="flex items-center gap-4 mb-3">
            <div className="relative">
              <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-lg">
                <TrendingUp className="w-7 h-7 text-white" />
              </div>
              <div className="absolute inset-0 bg-purple-500 rounded-2xl blur-xl opacity-30"></div>
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                Trend Seeds
              </h1>
              <p className="text-gray-600 mt-1">
                Social media trends discovered through Instagram and Facebook analysis
              </p>
            </div>
          </div>
          <div className="mt-6 flex items-center gap-3">
            <div className="glass px-4 py-2 rounded-full border border-white/30">
              <span className="text-sm font-bold text-gray-900">{seeds.length}</span>
              <span className="text-sm text-gray-600 ml-1">total trends</span>
            </div>
          </div>
        </div>
      </div>

      {seeds.length === 0 ? (
        <div className="text-center py-16 glass rounded-2xl border border-white/50 shadow-soft">
          <div className="relative inline-block mb-6">
            <TrendingUp className="w-16 h-16 text-purple-400 mx-auto" />
            <div className="absolute inset-0 bg-purple-500 blur-2xl opacity-20"></div>
          </div>
          <p className="text-lg font-semibold text-gray-900 mb-2">No trend seeds found</p>
          <p className="text-sm text-gray-600 max-w-md mx-auto">
            Run the trend discovery CLI command to populate this database with trending content
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {seeds.map((seed, index) => (
            <div key={seed.id} className="animate-slide-up" style={{ animationDelay: `${index * 50}ms` }}>
              <TrendSeedCard seed={seed} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
