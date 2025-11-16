// frontend/components/posts/ScheduledPostsCalendar.tsx

'use client'

import { useState, useMemo } from 'react'
import { ChevronLeft, ChevronRight, Facebook, Instagram } from 'lucide-react'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, startOfWeek, endOfWeek } from 'date-fns'
import type { CompletedPost } from '@/types'

interface ScheduledPostsCalendarProps {
  posts: CompletedPost[]
}

export default function ScheduledPostsCalendar({ posts }: ScheduledPostsCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date())

  // Group posts by date
  const postsByDate = useMemo(() => {
    const grouped: Record<string, CompletedPost[]> = {}
    posts.forEach(post => {
      const date = format(new Date(post.published_at || post.created_at), 'yyyy-MM-dd')
      if (!grouped[date]) {
        grouped[date] = []
      }
      grouped[date].push(post)
    })
    return grouped
  }, [posts])

  // Get calendar days
  const monthStart = startOfMonth(currentDate)
  const monthEnd = endOfMonth(currentDate)
  const calendarStart = startOfWeek(monthStart)
  const calendarEnd = endOfWeek(monthEnd)
  const calendarDays = eachDayOfInterval({ start: calendarStart, end: calendarEnd })

  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

  const handlePrevMonth = () => setCurrentDate(subMonths(currentDate, 1))
  const handleNextMonth = () => setCurrentDate(addMonths(currentDate, 1))
  const handleToday = () => setCurrentDate(new Date())

  return (
    <div className="space-y-4">
      {/* Calendar Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-slate-900">
          {format(currentDate, 'MMMM yyyy')}
        </h3>
        <div className="flex items-center gap-2">
          <button
            onClick={handleToday}
            className="px-3 py-1 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
          >
            Today
          </button>
          <button
            onClick={handlePrevMonth}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-slate-600" />
          </button>
          <button
            onClick={handleNextMonth}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <ChevronRight className="w-5 h-5 text-slate-600" />
          </button>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-2">
        {/* Week day headers */}
        {weekDays.map(day => (
          <div key={day} className="text-center text-sm font-semibold text-slate-600 py-2">
            {day}
          </div>
        ))}

        {/* Calendar days */}
        {calendarDays.map(day => {
          const dateKey = format(day, 'yyyy-MM-dd')
          const dayPosts = postsByDate[dateKey] || []
          const isCurrentMonth = isSameMonth(day, currentDate)
          const isToday = isSameDay(day, new Date())

          return (
            <div
              key={dateKey}
              className={`min-h-[100px] p-2 rounded-lg border transition-all ${
                isCurrentMonth
                  ? 'bg-white border-slate-200'
                  : 'bg-slate-50 border-slate-100'
              } ${isToday ? 'ring-2 ring-cyan-500' : ''}`}
            >
              <div className={`text-sm font-medium mb-2 ${
                isCurrentMonth ? 'text-slate-900' : 'text-slate-400'
              } ${isToday ? 'text-cyan-600 font-bold' : ''}`}>
                {format(day, 'd')}
              </div>
              <div className="space-y-1">
                {dayPosts.map(post => (
                  <div
                    key={post.id}
                    className={`text-xs px-2 py-1 rounded flex items-center gap-1 ${
                      post.platform === 'facebook'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-pink-100 text-pink-700'
                    }`}
                    title={post.text.substring(0, 100)}
                  >
                    {post.platform === 'facebook' ? (
                      <Facebook className="w-3 h-3 flex-shrink-0" />
                    ) : (
                      <Instagram className="w-3 h-3 flex-shrink-0" />
                    )}
                    <span className="truncate flex-1">
                      {post.text.substring(0, 20)}...
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 pt-4 border-t border-slate-200">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-100 rounded"></div>
          <span className="text-sm text-slate-600">Facebook</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-pink-100 rounded"></div>
          <span className="text-sm text-slate-600">Instagram</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-cyan-500 rounded"></div>
          <span className="text-sm text-slate-600">Today</span>
        </div>
      </div>
    </div>
  )
}
