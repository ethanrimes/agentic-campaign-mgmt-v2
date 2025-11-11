// frontend/app/news-events/page.tsx

import { getNewsEventSeeds } from '@/lib/api'
import NewsEventCard from '@/components/seeds/NewsEventCard'
import { Database } from 'lucide-react'

export const dynamic = 'force-dynamic'

export default async function NewsEventsPage() {
  const seeds = await getNewsEventSeeds()

  return (
    <div className="max-w-6xl mx-auto animate-fade-in">
      <div className="relative mb-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-100/50 via-cyan-100/30 to-blue-100/50 rounded-3xl blur-3xl"></div>
        <div className="relative glass rounded-2xl p-8 border border-white/50 shadow-soft">
          <div className="flex items-center gap-4 mb-3">
            <div className="relative">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center shadow-lg">
                <Database className="w-7 h-7 text-white" />
              </div>
              <div className="absolute inset-0 bg-blue-500 rounded-2xl blur-xl opacity-30"></div>
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                News Event Seeds
              </h1>
              <p className="text-gray-600 mt-1">
                Canonical news events discovered and consolidated from research agents
              </p>
            </div>
          </div>
          <div className="mt-6 flex items-center gap-3">
            <div className="glass px-4 py-2 rounded-full border border-white/30">
              <span className="text-sm font-bold text-gray-900">{seeds.length}</span>
              <span className="text-sm text-gray-600 ml-1">total events</span>
            </div>
          </div>
        </div>
      </div>

      {seeds.length === 0 ? (
        <div className="text-center py-16 glass rounded-2xl border border-white/50 shadow-soft">
          <div className="relative inline-block mb-6">
            <Database className="w-16 h-16 text-blue-400 mx-auto" />
            <div className="absolute inset-0 bg-blue-500 blur-2xl opacity-20"></div>
          </div>
          <p className="text-lg font-semibold text-gray-900 mb-2">No news event seeds found</p>
          <p className="text-sm text-gray-600 max-w-md mx-auto">
            Run the news ingestion CLI commands to populate this database with the latest news events
          </p>
        </div>
      ) : (
        <div className="space-y-4">
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
