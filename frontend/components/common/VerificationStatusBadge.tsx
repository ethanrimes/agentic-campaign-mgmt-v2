// frontend/components/common/VerificationStatusBadge.tsx

'use client'

import { ShieldCheck, ShieldX, ShieldAlert } from 'lucide-react'
import Link from 'next/link'
import { cn } from '@/lib/utils'

type VerificationStatus = 'verified' | 'rejected' | 'unverified'

interface VerificationStatusBadgeProps {
  status: VerificationStatus
  postId: string
  size?: 'sm' | 'md'
  className?: string
}

export default function VerificationStatusBadge({
  status,
  postId,
  size = 'md',
  className,
}: VerificationStatusBadgeProps) {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-3 py-1.5 gap-1.5',
  }

  const iconSize = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
  }

  const statusConfig = {
    verified: {
      bg: 'bg-green-50 hover:bg-green-100',
      text: 'text-green-700',
      border: 'border-green-100 hover:border-green-200',
      icon: ShieldCheck,
      label: 'Verified',
    },
    rejected: {
      bg: 'bg-red-50 hover:bg-red-100',
      text: 'text-red-700',
      border: 'border-red-100 hover:border-red-200',
      icon: ShieldX,
      label: 'Rejected',
    },
    unverified: {
      bg: 'bg-amber-50 hover:bg-amber-100',
      text: 'text-amber-700',
      border: 'border-amber-100 hover:border-amber-200',
      icon: ShieldAlert,
      label: 'Unverified',
    },
  }

  const config = statusConfig[status]
  const Icon = config.icon

  // Only link to verifier report if verified or rejected (has a report)
  const isClickable = status === 'verified' || status === 'rejected'

  const badgeContent = (
    <span
      className={cn(
        'flex items-center rounded-full font-medium border transition-all',
        sizeClasses[size],
        config.bg,
        config.text,
        config.border,
        isClickable && 'cursor-pointer',
        className
      )}
    >
      <Icon className={iconSize[size]} />
      {config.label}
    </span>
  )

  if (isClickable) {
    return (
      <Link
        href={`/verifier?post=${postId}`}
        onClick={(e) => e.stopPropagation()}
        className="group relative inline-block"
      >
        <span
          className={cn(
            'flex items-center rounded-full font-medium border transition-all',
            sizeClasses[size],
            config.bg,
            config.text,
            config.border,
            'cursor-pointer',
            className
          )}
        >
          <Icon className={iconSize[size]} />
          <span className="group-hover:hidden">{config.label}</span>
          <span className="hidden group-hover:inline underline decoration-dotted underline-offset-2">View Report</span>
        </span>
      </Link>
    )
  }

  return badgeContent
}
