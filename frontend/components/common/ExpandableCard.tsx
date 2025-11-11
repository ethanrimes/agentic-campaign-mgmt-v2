// frontend/components/common/ExpandableCard.tsx

'use client'

import { useState, ReactNode } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { cn } from '@/lib/utils'

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
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-6 text-left hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-1">
              <h3 className="text-lg font-semibold text-gray-900 truncate">
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
          <div className="ml-4 flex-shrink-0">
            {isExpanded ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </div>
        </div>
      </button>

      {isExpanded && (
        <div className="px-6 pb-6 border-t border-gray-100">
          <div className="pt-4">
            {children}
          </div>
        </div>
      )}
    </div>
  )
}
