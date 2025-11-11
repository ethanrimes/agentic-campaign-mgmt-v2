// frontend/app/news-events/page.tsx

import { getNewsEventSeeds } from '@/lib/api'
import NewsEventCard from '@/components/seeds/NewsEventCard'
import { Database } from 'lucide-react'

export const dynamic = 'force-dynamic'

export default async function NewsEventsPage() {
  const seeds = await getNewsEventSeeds()

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Database className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">News Event Seeds</h1>
        </div>
        <p className="text-gray-600">
          Canonical news events discovered and consolidated from research agents
        </p>
        <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
          <span className="font-medium">{seeds.length} total events</span>
        </div>
      </div>

      {seeds.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No news event seeds found</p>
          <p className="text-sm text-gray-500 mt-2">
            Run the news ingestion CLI commands to populate this database
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {seeds.map((seed) => (
            <NewsEventCard key={seed.id} seed={seed} />
          ))}
        </div>
      )}
    </div>
  )
}
