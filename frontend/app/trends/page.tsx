// frontend/app/trends/page.tsx

import { getTrendSeeds } from '@/lib/api'
import TrendSeedCard from '@/components/seeds/TrendSeedCard'
import { TrendingUp } from 'lucide-react'

export const dynamic = 'force-dynamic'

export default async function TrendsPage() {
  const seeds = await getTrendSeeds()

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <TrendingUp className="w-8 h-8 text-purple-600" />
          <h1 className="text-3xl font-bold text-gray-900">Trend Seeds</h1>
        </div>
        <p className="text-gray-600">
          Social media trends discovered through Instagram and Facebook analysis
        </p>
        <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
          <span className="font-medium">{seeds.length} total trends</span>
        </div>
      </div>

      {seeds.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No trend seeds found</p>
          <p className="text-sm text-gray-500 mt-2">
            Run the trend discovery CLI command to populate this database
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {seeds.map((seed) => (
            <TrendSeedCard key={seed.id} seed={seed} />
          ))}
        </div>
      )}
    </div>
  )
}
