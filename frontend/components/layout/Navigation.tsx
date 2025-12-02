// frontend/components/layout/Navigation.tsx

'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState, useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'
import { 
  ChevronDown, 
  Zap, 
  Loader2, 
  Sparkles, 
  Calendar, 
  BarChart3, 
  ShieldCheck, 
  Facebook, 
  Instagram 
} from 'lucide-react'
import { useBusinessAsset } from '@/lib/business-asset-context'
import { motion, AnimatePresence } from 'framer-motion'

const navItems = [
  { name: 'Seeds', href: '/content-seeds', icon: Sparkles },
  { name: 'Schedule', href: '/scheduled-posts', icon: Calendar },
  { name: 'Insights', href: '/insights', icon: BarChart3 },
  { name: 'Verifier', href: '/verifier', icon: ShieldCheck },
  { name: 'Facebook', href: '/facebook', icon: Facebook },
  { name: 'Instagram', href: '/instagram', icon: Instagram },
]

export default function Navigation() {
  const pathname = usePathname()
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)
  const { selectedAsset, allAssets, setSelectedAsset, isLoading } = useBusinessAsset()
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Handle scroll for glass effect intensity
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const handleAssetSelect = (assetId: string) => {
    const asset = allAssets.find(a => a.id === assetId)
    if (asset) {
      setSelectedAsset(asset)
      setIsDropdownOpen(false)
    }
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-50 flex justify-center px-4 pt-4 pointer-events-none">
      <motion.nav 
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 100, damping: 20 }}
        className={cn(
          "pointer-events-auto flex items-center gap-2 px-3 py-2 rounded-full border transition-all duration-300",
          isScrolled 
            ? "bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-white/20 shadow-lg" 
            : "bg-white/50 dark:bg-slate-900/50 backdrop-blur-md border-white/10 shadow-soft"
        )}
      >
        {/* Logo */}
        <Link
          href="/"
          className="flex items-center gap-2 px-3 py-2 mr-2 group"
        >
          <div className="relative flex items-center justify-center w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl shadow-lg group-hover:scale-105 transition-transform">
            <Zap className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-purple-600 hidden md:block">
            SMM
          </span>
        </Link>

        {/* Navigation Items */}
        <div className="flex items-center gap-1">
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.href)
            const Icon = item.icon

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'relative flex items-center justify-center px-3 py-2 rounded-full transition-all duration-300 group',
                  isActive
                    ? 'text-primary-600'
                    : 'text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'
                )}
              >
                {isActive && (
                  <motion.div
                    layoutId="nav-active"
                    className="absolute inset-0 bg-primary-50 dark:bg-primary-900/20 rounded-full"
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}
                <span className="relative flex items-center gap-2 text-sm font-medium z-10">
                  <Icon className={cn("w-4 h-4 transition-transform group-hover:scale-110", isActive && "stroke-[2.5px]")} />
                  <span className="hidden lg:inline">{item.name}</span>
                </span>
              </Link>
            )
          })}
        </div>

        {/* Divider */}
        <div className="w-px h-6 bg-slate-200 dark:bg-slate-700 mx-2 hidden sm:block"></div>

        {/* Business Asset Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className={cn(
              "flex items-center gap-2 px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 border min-w-[160px]",
              isDropdownOpen 
                ? "bg-slate-100 dark:bg-slate-800 border-slate-200" 
                : "bg-transparent hover:bg-slate-100/50 dark:hover:bg-slate-800/50 border-transparent hover:border-slate-200"
            )}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-primary-500" />
                <span className="text-slate-500">Loading...</span>
              </>
            ) : (
              <>
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span className="truncate flex-1 text-left text-slate-700 dark:text-slate-200">
                  {selectedAsset?.name || 'Select Asset'}
                </span>
                <ChevronDown className={cn(
                  "w-4 h-4 text-slate-400 transition-transform duration-200",
                  isDropdownOpen && "rotate-180"
                )} />
              </>
            )}
          </button>

          <AnimatePresence>
            {isDropdownOpen && !isLoading && (
              <motion.div
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 mt-2 w-64 bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-100 dark:border-slate-800 overflow-hidden p-2 z-50"
              >
                <div className="px-3 py-2 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider border-b border-slate-100 dark:border-slate-800 mb-1">
                  Active Campaign
                </div>
                <div className="space-y-1 max-h-[300px] overflow-y-auto custom-scrollbar">
                  {allAssets.length === 0 ? (
                    <div className="px-3 py-2 text-slate-400 text-sm text-center italic">
                      No assets found
                    </div>
                  ) : (
                    allAssets.map((asset) => (
                      <button
                        key={asset.id}
                        onClick={() => handleAssetSelect(asset.id)}
                        className={cn(
                          "w-full px-3 py-2 rounded-xl text-left text-sm transition-all flex items-center justify-between group",
                          selectedAsset?.id === asset.id
                            ? "bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-300"
                            : "text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800"
                        )}
                      >
                        <span className="font-medium">{asset.name}</span>
                        {selectedAsset?.id === asset.id && (
                          <motion.div layoutId="check">
                            <div className="w-1.5 h-1.5 rounded-full bg-primary-500"></div>
                          </motion.div>
                        )}
                      </button>
                    ))
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.nav>
    </div>
  )
}
