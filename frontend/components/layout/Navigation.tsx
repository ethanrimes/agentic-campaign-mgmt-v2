// frontend/components/layout/Navigation.tsx

'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Database, TrendingUp, Lightbulb, BarChart3, Facebook, Instagram, Sparkles } from 'lucide-react'

const navItems = [
  { name: 'News Events', href: '/news-events', icon: Database, color: 'text-blue-600' },
  { name: 'Trends', href: '/trends', icon: TrendingUp, color: 'text-purple-600' },
  { name: 'Ungrounded', href: '/ungrounded', icon: Lightbulb, color: 'text-amber-600' },
  { name: 'Insights', href: '/insights', icon: BarChart3, color: 'text-green-600' },
  { name: 'Facebook', href: '/facebook', icon: Facebook, color: 'text-blue-700' },
  { name: 'Instagram', href: '/instagram', icon: Instagram, color: 'text-pink-600' },
]

export default function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="sticky top-0 z-50 glass shadow-soft border-b border-white/30 backdrop-blur-xl">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link
            href="/"
            className="flex items-center gap-2 text-xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent hover:scale-105 transition-transform"
          >
            <div className="relative">
              <Sparkles className="w-6 h-6 text-primary-600 animate-pulse-slow" />
              <div className="absolute inset-0 blur-lg bg-primary-400 opacity-30 animate-pulse-slow"></div>
            </div>
            Living Knowledge DB
          </Link>

          <div className="flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname.startsWith(item.href)

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'relative flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 group',
                    isActive
                      ? 'bg-white/80 text-gray-900 shadow-soft'
                      : 'text-gray-600 hover:bg-white/50 hover:text-gray-900'
                  )}
                >
                  <Icon className={cn(
                    'w-4 h-4 transition-all duration-300',
                    isActive ? item.color : 'group-hover:scale-110'
                  )} />
                  <span className="hidden md:inline">{item.name}</span>
                  {isActive && (
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1/2 h-0.5 bg-gradient-to-r from-transparent via-primary-600 to-transparent"></div>
                  )}
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}
