// frontend/components/seeds/ContentSeedsGrid.tsx

'use client'

import { useState, useEffect } from 'react'
import { Database, TrendingUp, Lightbulb, ArrowRight } from 'lucide-react'
import SeedModal from './SeedModal'
import type { NewsEventSeed, TrendSeed, UngroundedSeed } from '@/types'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'

interface ContentSeedsGridProps {
  newsSeeds: NewsEventSeed[]
  trendSeeds: TrendSeed[]
  ungroundedSeeds: UngroundedSeed[]
  postCounts: Record<string, number>
  initialSeedId?: string
  initialSeedType?: 'news_event' | 'trend' | 'ungrounded'
}

type SectionType = 'news' | 'trends' | 'creative' | null
type SelectedSeed = { seed: NewsEventSeed | TrendSeed | UngroundedSeed; type: 'news_event' | 'trend' | 'ungrounded' } | null

export default function ContentSeedsGrid({ newsSeeds, trendSeeds, ungroundedSeeds, postCounts, initialSeedId, initialSeedType }: ContentSeedsGridProps) {
  const getInitialSection = (): SectionType => {
    if (initialSeedType === 'news_event') return 'news'
    if (initialSeedType === 'trend') return 'trends'
    if (initialSeedType === 'ungrounded') return 'creative'
    return 'news'
  }

  const [expandedSection, setExpandedSection] = useState<SectionType>(getInitialSection())
  const [selectedSeed, setSelectedSeed] = useState<SelectedSeed>(null)

  useEffect(() => {
    if (initialSeedId && initialSeedType) {
      let seed: any = null
      if (initialSeedType === 'news_event') {
        seed = newsSeeds.find(s => s.id === initialSeedId)
      } else if (initialSeedType === 'trend') {
        seed = trendSeeds.find(s => s.id === initialSeedId)
      } else if (initialSeedType === 'ungrounded') {
        seed = ungroundedSeeds.find(s => s.id === initialSeedId)
      }

      if (seed) {
        setSelectedSeed({ seed, type: initialSeedType })
      }
    }
  }, [initialSeedId, initialSeedType, newsSeeds, trendSeeds, ungroundedSeeds])

  const handleSeedClick = (seed: any, type: 'news_event' | 'trend' | 'ungrounded') => {
    setSelectedSeed({ seed, type })
  }

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
      seedType: 'news_event' as const,
    },
    {
      id: 'trends' as SectionType,
      title: 'Social Media Trends',
      icon: TrendingUp,
      color: 'purple',
      count: trendSeeds.length,
      seeds: trendSeeds,
      seedType: 'trend' as const,
    },
    {
      id: 'creative' as SectionType,
      title: 'Creative Ideas',
      icon: Lightbulb,
      color: 'amber',
      count: ungroundedSeeds.length,
      seeds: ungroundedSeeds,
      seedType: 'ungrounded' as const,
    },
  ]

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05
      }
    }
  }

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  }

  return (
    <>
      <div className="space-y-8">
        {/* Filter Buttons */}
        <div className="flex flex-wrap gap-4 justify-center">
          {sections.map((section) => {
            const isActive = expandedSection === section.id
            const Icon = section.icon
            
            // Dynamic colors based on section type
            let activeClass = ""
            let iconColor = ""
            if (section.color === 'blue') {
              activeClass = "bg-blue-500 border-blue-500 text-white shadow-blue-500/30"
              iconColor = "text-blue-500"
            } else if (section.color === 'purple') {
              activeClass = "bg-purple-500 border-purple-500 text-white shadow-purple-500/30"
              iconColor = "text-purple-500"
            } else {
              activeClass = "bg-amber-500 border-amber-500 text-white shadow-amber-500/30"
              iconColor = "text-amber-500"
            }

            return (
              <motion.button
                key={section.id}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => toggleSection(section.id)}
                className={cn(
                  "flex items-center gap-3 px-6 py-3 rounded-full border-2 transition-all duration-300 shadow-sm",
                  isActive
                    ? `${activeClass} shadow-lg`
                    : "bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-600"
                )}
              >
                <Icon className={cn("w-5 h-5", isActive ? "text-white" : iconColor)} />
                <span className="font-bold text-sm tracking-wide">{section.title}</span>
                <span className={cn(
                  "ml-1 text-xs px-2 py-0.5 rounded-full font-mono",
                  isActive ? "bg-white/20 text-white" : "bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400"
                )}>
                  {section.count}
                </span>
              </motion.button>
            )
          })}
        </div>

        {/* Sections */}
        <AnimatePresence mode="wait">
          {sections.map((section) => {
            if (expandedSection !== section.id || section.seeds.length === 0) return null

            return (
              <motion.section
                key={section.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <div className="flex items-center gap-3 mb-6 px-2">
                  <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{section.title}</h2>
                  <div className="h-px flex-1 bg-gradient-to-r from-slate-200 via-slate-100 to-transparent dark:from-slate-700 dark:via-slate-800"></div>
                </div>

                <motion.div 
                  variants={container}
                  initial="hidden"
                  animate="show"
                  className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                >
                  {section.seeds.map((seed: any) => {
                    const postCount = postCounts[seed.id] || 0
                    const seedName = seed.name || seed.idea
                    const seedSubtitle = section.seedType === 'news_event'
                      ? seed.location
                      : section.seedType === 'trend'
                      ? `${seed.hashtags?.length || 0} hashtags`
                      : seed.format

                    return (
                      <motion.div
                        key={seed.id}
                        variants={item}
                        layoutId={`seed-${seed.id}`}
                        onClick={() => handleSeedClick(seed, section.seedType)}
                        className="group relative cursor-pointer glass-panel p-6 hover:-translate-y-1"
                      >
                        {postCount > 0 && (
                          <div className="absolute -top-2 -right-2 z-10 bg-gradient-to-br from-green-500 to-emerald-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg border-2 border-white dark:border-slate-900">
                            {postCount}
                          </div>
                        )}
                        
                        <div className="mb-4">
                          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-1 line-clamp-2 group-hover:text-primary-500 transition-colors">
                            {seedName}
                          </h3>
                          {seedSubtitle && (
                            <p className="text-xs font-medium text-primary-600 dark:text-primary-400 uppercase tracking-wide">
                              {seedSubtitle}
                            </p>
                          )}
                        </div>
                        
                        <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-3 mb-4 leading-relaxed">
                          {seed.description || seed.idea || seed.details}
                        </p>

                        <div className="flex items-center text-xs font-medium text-slate-400 group-hover:text-primary-500 transition-colors">
                          View Details <ArrowRight className="w-3 h-3 ml-1 transition-transform group-hover:translate-x-1" />
                        </div>
                      </motion.div>
                    )
                  })}
                </motion.div>
              </motion.section>
            )
          })}
        </AnimatePresence>

        {/* Empty State */}
        {!expandedSection && (
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }}
            className="text-center py-20 glass-panel"
          >
            <p className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Select a category above</p>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Explore the living database of content ideas
            </p>
          </motion.div>
        )}
      </div>

      {/* Seed Modal */}
      {selectedSeed && (
        <SeedModal
          seed={selectedSeed.seed}
          seedType={selectedSeed.type}
          postCount={postCounts[selectedSeed.seed.id] || 0}
          onClose={() => setSelectedSeed(null)}
        />
      )}
    </>
  )
}