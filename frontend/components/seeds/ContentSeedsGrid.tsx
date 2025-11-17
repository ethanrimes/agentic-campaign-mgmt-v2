// frontend/components/seeds/ContentSeedsGrid.tsx

'use client'

import { useState, useEffect } from 'react'
import { Database, TrendingUp, Lightbulb, ChevronDown } from 'lucide-react'
import NewsEventCard from './NewsEventCard'
import TrendSeedCard from './TrendSeedCard'
import UngroundedSeedCard from './UngroundedSeedCard'
import type { NewsEventSeed, TrendSeed, UngroundedSeed } from '@/types'

interface ContentSeedsGridProps {
  newsSeeds: NewsEventSeed[]
  trendSeeds: TrendSeed[]
  ungroundedSeeds: UngroundedSeed[]
  postCounts: Record<string, number>
  initialSeedId?: string
  initialSeedType?: 'news_event' | 'trend' | 'ungrounded'
}

type SectionType = 'news' | 'trends' | 'creative' | null

export default function ContentSeedsGrid({ newsSeeds, trendSeeds, ungroundedSeeds, postCounts, initialSeedId, initialSeedType }: ContentSeedsGridProps) {
  // Determine initial section based on initialSeedType
  const getInitialSection = (): SectionType => {
    if (initialSeedType === 'news_event') return 'news'
    if (initialSeedType === 'trend') return 'trends'
    if (initialSeedType === 'ungrounded') return 'creative'
    return 'news'
  }

  const [expandedSection, setExpandedSection] = useState<SectionType>(getInitialSection())

  // Scroll to seed card when initialSeedId is provided
  useEffect(() => {
    if (initialSeedId) {
      // Wait for DOM to render
      setTimeout(() => {
        const element = document.getElementById(`seed-${initialSeedId}`)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' })
          // Trigger click to expand the card
          element.click()
        }
      }, 500)
    }
  }, [initialSeedId])

  const toggleSection = (section: SectionType) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  const sections = [
    {
      id: 'news' as SectionType,
      title: 'News Events',
      icon: Database,
      color: 'blue',
      count: newsSeeds.length,
      seeds: newsSeeds,
      CardComponent: NewsEventCard,
    },
    {
      id: 'trends' as SectionType,
      title: 'Social Media Trends',
      icon: TrendingUp,
      color: 'purple',
      count: trendSeeds.length,
      seeds: trendSeeds,
      CardComponent: TrendSeedCard,
    },
    {
      id: 'creative' as SectionType,
      title: 'Creative Ideas',
      icon: Lightbulb,
      color: 'amber',
      count: ungroundedSeeds.length,
      seeds: ungroundedSeeds,
      CardComponent: UngroundedSeedCard,
    },
  ]

  const getColorClasses = (color: string) => {
    const colorMap = {
      blue: {
        bg: 'bg-blue-600',
        bgLight: 'bg-blue-50',
        text: 'text-blue-700',
        border: 'border-blue-200',
        hover: 'hover:bg-blue-100',
      },
      purple: {
        bg: 'bg-purple-600',
        bgLight: 'bg-purple-50',
        text: 'text-purple-700',
        border: 'border-purple-200',
        hover: 'hover:bg-purple-100',
      },
      amber: {
        bg: 'bg-amber-600',
        bgLight: 'bg-amber-50',
        text: 'text-amber-700',
        border: 'border-amber-200',
        hover: 'hover:bg-amber-100',
      },
    }
    return colorMap[color as keyof typeof colorMap] || colorMap.blue
  }

  return (
    <div className="space-y-6">
      {/* Filter Buttons */}
      <div className="flex flex-wrap gap-3 justify-center">
        {sections.map((section) => {
          const colors = getColorClasses(section.color)
          const isActive = expandedSection === section.id
          const Icon = section.icon

          return (
            <button
              key={section.id}
              onClick={() => toggleSection(section.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full border-2 transition-all ${
                isActive
                  ? `${colors.bg} text-white ${colors.border}`
                  : `${colors.bgLight} ${colors.text} ${colors.border} ${colors.hover}`
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="font-medium">{section.title}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full ${
                isActive ? 'bg-white/20' : 'bg-white'
              }`}>
                {section.count}
              </span>
            </button>
          )
        })}
      </div>

      {/* Sections */}
      {sections.map((section) => {
        const isExpanded = expandedSection === section.id
        const colors = getColorClasses(section.color)
        const Icon = section.icon
        const CardComponent = section.CardComponent

        if (!isExpanded || section.seeds.length === 0) return null

        return (
          <section key={section.id} className="animate-fade-in">
            <div className="flex items-center gap-3 mb-6">
              <div className={`w-10 h-10 ${colors.bg} rounded-xl flex items-center justify-center shadow-lg`}>
                <Icon className="w-5 h-5 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">{section.title}</h2>
              <span className={`text-sm ${colors.bgLight} ${colors.text} px-3 py-1 rounded-full font-medium ${colors.border} border`}>
                {section.count}
              </span>
            </div>

            {/* Grid Layout */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {section.seeds.map((seed: any, index: number) => {
                const postCount = postCounts[seed.id] || 0
                return (
                  <div
                    key={seed.id}
                    id={`seed-${seed.id}`}
                    className="animate-slide-up relative"
                    style={{ animationDelay: `${index * 30}ms` }}
                  >
                    {postCount > 0 && (
                      <div className="absolute -top-2 -right-2 z-10 bg-gradient-to-br from-green-500 to-emerald-600 text-white text-xs font-bold px-3 py-1.5 rounded-full shadow-lg border-2 border-white">
                        {postCount} {postCount === 1 ? 'post' : 'posts'}
                      </div>
                    )}
                    <CardComponent seed={seed} />
                  </div>
                )
              })}
            </div>
          </section>
        )
      })}

      {/* Show message if no section is expanded */}
      {!expandedSection && (
        <div className="text-center py-16 bg-white rounded-2xl border border-slate-200 shadow-xl">
          <p className="text-lg font-semibold text-slate-900 mb-2">Select a category to view content seeds</p>
          <p className="text-sm text-slate-600 max-w-md mx-auto">
            Click on one of the buttons above to explore different types of content seeds
          </p>
        </div>
      )}
    </div>
  )
}
