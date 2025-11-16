// frontend/components/layout/Navigation.tsx

'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'
import { cn } from '@/lib/utils'
import { ChevronDown, Zap } from 'lucide-react'

const navItems = [
  { name: 'Content Seeds', href: '/content-seeds' },
  { name: 'Scheduled Posts', href: '/scheduled-posts' },
  { name: 'Insight Reports', href: '/insights' },
  { name: 'Facebook', href: '/facebook' },
  { name: 'Instagram', href: '/instagram' },
  { name: 'Login', href: '/login' },
]

export default function Navigation() {
  const pathname = usePathname()
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const currentCampaign = 'Penn Daily Buzz'

  return (
    <nav className="sticky top-0 z-50 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 shadow-lg border-b border-slate-700">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link
            href="/"
            className="flex items-center gap-3 text-xl font-bold text-white hover:scale-105 transition-transform group"
          >
            <div className="relative">
              <Zap className="w-7 h-7 text-cyan-400 group-hover:text-cyan-300 transition-colors" />
              <div className="absolute inset-0 blur-md bg-cyan-400 opacity-40 group-hover:opacity-60 transition-opacity"></div>
            </div>
            <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent">
              BuzzFactory
            </span>
          </Link>

          {/* Navigation Items */}
          <div className="flex items-center space-x-1">
            {navItems.map((item) => {
              const isActive = pathname.startsWith(item.href)

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'relative px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                    isActive
                      ? 'bg-slate-700 text-white shadow-lg'
                      : 'text-slate-300 hover:bg-slate-700/50 hover:text-white'
                  )}
                >
                  {item.name}
                  {isActive && (
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-3/4 h-0.5 bg-gradient-to-r from-transparent via-cyan-400 to-transparent"></div>
                  )}
                </Link>
              )
            })}

            {/* Campaign Dropdown */}
            <div className="relative ml-4">
              <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="flex items-center gap-2 px-4 py-2 bg-slate-700 text-white rounded-lg text-sm font-medium hover:bg-slate-600 transition-all duration-200"
              >
                <span>{currentCampaign}</span>
                <ChevronDown className={cn(
                  "w-4 h-4 transition-transform duration-200",
                  isDropdownOpen && "rotate-180"
                )} />
              </button>

              {isDropdownOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-slate-800 rounded-lg shadow-xl border border-slate-700 overflow-hidden">
                  <div className="py-1">
                    <div className="px-4 py-2 text-slate-300 hover:bg-slate-700 cursor-pointer transition-colors">
                      {currentCampaign}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
