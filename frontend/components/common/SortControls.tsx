// frontend/components/common/SortControls.tsx

'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowUpDown, ArrowUp, ArrowDown, Calendar, Check, ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

export type SortMetric = 'scheduled_time' | string
export type SortDirection = 'asc' | 'desc'

export interface SortOption {
  id: string
  label: string
  icon?: React.ReactNode
}

interface SortControlsProps {
  options: SortOption[]
  selectedMetric: SortMetric
  direction: SortDirection
  onMetricChange: (metric: SortMetric) => void
  onDirectionChange: (direction: SortDirection) => void
  accentColor?: 'blue' | 'pink'
}

export default function SortControls({
  options,
  selectedMetric,
  direction,
  onMetricChange,
  onDirectionChange,
  accentColor = 'blue'
}: SortControlsProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const selectedOption = options.find(o => o.id === selectedMetric) || options[0]
  const isDefaultSort = selectedMetric === 'scheduled_time'

  const accentClasses = {
    blue: {
      button: 'hover:border-blue-300 hover:text-blue-600',
      activeButton: 'border-blue-400 text-blue-600 bg-blue-50',
      directionActive: 'bg-blue-500 text-white',
      dropdownItem: 'hover:bg-blue-50',
      dropdownItemActive: 'bg-blue-50 text-blue-700',
      check: 'text-blue-600'
    },
    pink: {
      button: 'hover:border-pink-300 hover:text-pink-600',
      activeButton: 'border-pink-400 text-pink-600 bg-pink-50',
      directionActive: 'bg-pink-500 text-white',
      dropdownItem: 'hover:bg-pink-50',
      dropdownItemActive: 'bg-pink-50 text-pink-700',
      check: 'text-pink-600'
    }
  }

  const colors = accentClasses[accentColor]

  return (
    <div className="flex items-center gap-2" ref={dropdownRef}>
      {/* Sort By Dropdown */}
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            "flex items-center gap-2 px-3 py-2 rounded-lg border transition-all duration-200 text-sm font-medium",
            isDefaultSort
              ? "border-slate-200 text-slate-600 bg-white " + colors.button
              : colors.activeButton
          )}
        >
          <ArrowUpDown className="w-4 h-4" />
          <span className="hidden sm:inline">Sort by:</span>
          <span className="font-semibold">{selectedOption.label}</span>
          <ChevronDown className={cn("w-4 h-4 transition-transform", isOpen && "rotate-180")} />
        </button>

        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
              className="absolute top-full left-0 mt-1 w-56 bg-white rounded-xl shadow-lg border border-slate-200 py-1 z-50"
            >
              {options.map((option) => (
                <button
                  key={option.id}
                  onClick={() => {
                    onMetricChange(option.id)
                    setIsOpen(false)
                  }}
                  className={cn(
                    "w-full flex items-center justify-between px-4 py-2.5 text-sm text-left transition-colors",
                    selectedMetric === option.id
                      ? colors.dropdownItemActive + " font-medium"
                      : "text-slate-700 " + colors.dropdownItem
                  )}
                >
                  <div className="flex items-center gap-2">
                    {option.icon}
                    <span>{option.label}</span>
                  </div>
                  {selectedMetric === option.id && (
                    <Check className={cn("w-4 h-4", colors.check)} />
                  )}
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Direction Toggle - Only show when not default sort */}
      {!isDefaultSort && (
        <motion.div
          initial={{ opacity: 0, width: 0 }}
          animate={{ opacity: 1, width: 'auto' }}
          exit={{ opacity: 0, width: 0 }}
          className="flex items-center bg-slate-100 rounded-lg p-0.5"
        >
          <button
            onClick={() => onDirectionChange('desc')}
            className={cn(
              "flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium transition-all",
              direction === 'desc'
                ? colors.directionActive
                : "text-slate-600 hover:text-slate-900"
            )}
            title="Highest first"
          >
            <ArrowDown className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">High</span>
          </button>
          <button
            onClick={() => onDirectionChange('asc')}
            className={cn(
              "flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium transition-all",
              direction === 'asc'
                ? colors.directionActive
                : "text-slate-600 hover:text-slate-900"
            )}
            title="Lowest first"
          >
            <ArrowUp className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Low</span>
          </button>
        </motion.div>
      )}

      {/* Reset button when not default */}
      {!isDefaultSort && (
        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          onClick={() => onMetricChange('scheduled_time')}
          className="px-2.5 py-1.5 text-xs font-medium text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
        >
          Reset
        </motion.button>
      )}
    </div>
  )
}
