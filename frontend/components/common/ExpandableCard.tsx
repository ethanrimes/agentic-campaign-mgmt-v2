// frontend/components/common/ExpandableCard.tsx

'use client'

import { useState, ReactNode } from 'react'
import { ChevronDown, MoreVertical } from 'lucide-react'
import { cn } from '@/lib/utils'
import { motion, AnimatePresence } from 'framer-motion'

interface ExpandableCardProps {
  title: string
  subtitle?: string
  preview: ReactNode
  children: ReactNode | ((isExpanded: boolean) => ReactNode)
  defaultExpanded?: boolean
  badge?: ReactNode
  onExpandChange?: (expanded: boolean) => void
}

export default function ExpandableCard({
  title,
  subtitle,
  preview,
  children,
  defaultExpanded = false,
  badge,
  onExpandChange,
}: ExpandableCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  const handleToggle = () => {
    const newExpanded = !isExpanded
    setIsExpanded(newExpanded)
    onExpandChange?.(newExpanded)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "group relative overflow-hidden transition-all duration-300",
        "bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl",
        "border border-white/40 dark:border-slate-700/40",
        "shadow-sm hover:shadow-md",
        "rounded-2xl",
        isExpanded ? "ring-1 ring-primary/20 bg-white/90 dark:bg-slate-900/90 shadow-lg" : ""
      )}
    >
      {/* Decorative gradient hint on hover */}
      <div className="absolute inset-0 bg-gradient-to-r from-primary-500/0 via-primary-500/0 to-primary-500/0 group-hover:via-primary-500/5 transition-colors duration-500 pointer-events-none" />

      <button
        onClick={handleToggle}
        className="w-full p-5 text-left relative z-10"
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-1.5">
              <h3 className={cn(
                "text-lg font-bold truncate transition-colors",
                isExpanded ? "text-primary-700 dark:text-primary-400" : "text-slate-900 dark:text-slate-100"
              )}>
                {title}
              </h3>
              {badge}
            </div>
            
            {subtitle && (
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-3">
                {subtitle}
              </p>
            )}
            
            <motion.div 
              animate={{ opacity: isExpanded ? 0.6 : 1 }}
              className="text-slate-600 dark:text-slate-300"
            >
              {preview}
            </motion.div>
          </div>

          <div className="flex items-center gap-2">
            <motion.div
              animate={{ rotate: isExpanded ? 180 : 0 }}
              transition={{ type: 'spring', stiffness: 200, damping: 20 }}
              className={cn(
                "p-2 rounded-full transition-colors",
                isExpanded 
                  ? "bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400" 
                  : "bg-slate-100 text-slate-500 group-hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400"
              )}
            >
              <ChevronDown className="w-5 h-5" />
            </motion.div>
          </div>
        </div>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 200, damping: 25 }}
            className="relative z-10"
          >
            <div className="px-5 pb-5 pt-2">
              <motion.div
                initial={{ y: 10, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="pt-4 border-t border-slate-200/60 dark:border-slate-700/60"
              >
                {typeof children === 'function' ? children(isExpanded) : children}
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
