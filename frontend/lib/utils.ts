// frontend/lib/utils.ts

import { format, formatDistanceToNow } from 'date-fns'
import clsx, { ClassValue } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function formatDate(date: string | Date): string {
  return format(new Date(date), 'MMM d, yyyy')
}

export function formatDateTime(date: string | Date): string {
  return format(new Date(date), 'MMM d, yyyy h:mm a')
}

export function formatRelativeTime(date: string | Date): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true })
}

export function truncate(text: string, length: number): string {
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

export function getPlatformIcon(platform: 'facebook' | 'instagram'): string {
  return platform === 'facebook' ? '📘' : '📷'
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'completed':
    case 'published':
      return 'text-green-600 bg-green-50'
    case 'pending':
      return 'text-yellow-600 bg-yellow-50'
    case 'in_progress':
      return 'text-blue-600 bg-blue-50'
    case 'failed':
      return 'text-red-600 bg-red-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}
