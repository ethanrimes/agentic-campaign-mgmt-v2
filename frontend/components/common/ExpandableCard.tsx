// frontend/components/common/ExpandableCard.tsx

'use client'

import { useState, ReactNode } from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { motion, AnimatePresence } from 'framer-motion'

interface ExpandableCardProps {
  title: string
  subtitle?: string
  preview: ReactNode
  children: ReactNode
  defaultExpanded?: boolean
  badge?: ReactNode
}

export default function ExpandableCard({
  title,
  subtitle,
  preview,
  children,
  defaultExpanded = false,
  badge,
}: ExpandableCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="group bg-white rounded-xl shadow-soft hover:shadow-glow border border-gray-100 overflow-hidden transition-all duration-300"
    >
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-6 text-left hover:bg-gradient-to-br hover:from-primary-50/50 hover:to-secondary-50/30 transition-all duration-300"
      >
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-1">
              <h3 className="text-lg font-bold text-gray-900 truncate group-hover:text-primary-600 transition-colors">
                {title}
              </h3>
              {badge}
            </div>
            {subtitle && (
              <p className="text-sm text-gray-500 mb-2">{subtitle}</p>
            )}
            <div className="text-gray-600">
              {preview}
            </div>
          </div>
          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="ml-4 flex-shrink-0"
          >
            <div className="p-2 rounded-lg bg-gray-100 group-hover:bg-primary-100 transition-colors">
              <ChevronDown className="w-5 h-5 text-gray-600 group-hover:text-primary-600 transition-colors" />
            </div>
          </motion.div>
        </div>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="px-6 pb-6 border-t border-gradient-to-r from-primary-100 via-secondary-100 to-accent-100">
              <motion.div
                initial={{ y: -10, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.3, delay: 0.1 }}
                className="pt-4"
              >
                {children}
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
