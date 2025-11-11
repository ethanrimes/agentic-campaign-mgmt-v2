// frontend/components/layout/Navigation.tsx

'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Database, TrendingUp, Lightbulb, BarChart3, Facebook, Instagram } from 'lucide-react'

const navItems = [
  { name: 'News Events', href: '/news-events', icon: Database },
  { name: 'Trends', href: '/trends', icon: TrendingUp },
  { name: 'Ungrounded', href: '/ungrounded', icon: Lightbulb },
  { name: 'Insights', href: '/insights', icon: BarChart3 },
  { name: 'Facebook', href: '/facebook', icon: Facebook },
  { name: 'Instagram', href: '/instagram', icon: Instagram },
]

export default function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="text-xl font-bold text-gray-900">
            📊 Knowledge DB
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
                    'flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  )}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {item.name}
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}
