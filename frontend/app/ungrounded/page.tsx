// frontend/app/ungrounded/page.tsx

import { getUngroundedSeeds } from '@/lib/api'
import UngroundedSeedCard from '@/components/seeds/UngroundedSeedCard'
import { Lightbulb } from 'lucide-react'

export const dynamic = 'force-dynamic'

export default async function UngroundedPage() {
  const seeds = await getUngroundedSeeds()

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Lightbulb className="w-8 h-8 text-yellow-600" />
          <h1 className="text-3xl font-bold text-gray-900">Ungrounded Seeds</h1>
        </div>
        <p className="text-gray-600">
          Creative content ideas not tied to news or social media trends
        </p>
        <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
          <span className="font-medium">{seeds.length} total ideas</span>
        </div>
      </div>

      {seeds.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <Lightbulb className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No ungrounded seeds found</p>
          <p className="text-sm text-gray-500 mt-2">
            Run the ungrounded generation CLI command to create creative ideas
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {seeds.map((seed) => (
            <UngroundedSeedCard key={seed.id} seed={seed} />
          ))}
        </div>
      )}
    </div>
  )
}
