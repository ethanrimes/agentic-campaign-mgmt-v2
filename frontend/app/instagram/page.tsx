// frontend/app/instagram/page.tsx

'use client'

import { useState, useEffect } from 'react'
import { getCompletedPosts } from '@/lib/api-client'
import { useBusinessAsset } from '@/lib/business-asset-context'
import { Instagram } from 'lucide-react'
import InstagramPostGrid from '@/components/posts/InstagramPostGrid'
import type { CompletedPost } from '@/types'

export default function InstagramPage() {
  const { selectedAsset } = useBusinessAsset()
  const [posts, setPosts] = useState<CompletedPost[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadPosts() {
      if (!selectedAsset) return

      try {
        setLoading(true)
        const data = await getCompletedPosts(selectedAsset.id, 'instagram')
        setPosts(data)
      } catch (error) {
        console.error('Failed to load Instagram posts:', error)
      } finally {
        setLoading(false)
      }
    }

    loadPosts()
  }, [selectedAsset])

  if (!selectedAsset || loading) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="text-center py-16">
          <Instagram className="w-16 h-16 text-pink-400 mx-auto mb-4 animate-pulse" />
          <p className="text-lg text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  const statusCounts = {
    published: posts.filter(p => p.status === 'published').length,
    pending: posts.filter(p => p.status === 'pending').length,
    failed: posts.filter(p => p.status === 'failed').length,
  }

  return (
    <div className="max-w-7xl mx-auto animate-fade-in">
      <div className="relative mb-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-100/30 via-blue-100/20 to-slate-100/30 rounded-3xl blur-3xl"></div>
        <div className="relative bg-white rounded-2xl p-8 border border-slate-200 shadow-xl">
          <div className="flex items-center gap-4 mb-3">
            <div className="relative">
              <div className="w-14 h-14 bg-gradient-to-br from-pink-600 to-rose-600 rounded-2xl flex items-center justify-center shadow-lg">
                <Instagram className="w-7 h-7 text-white" />
              </div>
              <div className="absolute inset-0 bg-pink-600 rounded-2xl blur-xl opacity-30"></div>
            </div>
            <div>
              <h1 className="text-4xl font-bold text-slate-900">
                Instagram Posts
              </h1>
              <p className="text-slate-600 mt-1">
                Published and scheduled Instagram content
              </p>
            </div>
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <div className="bg-slate-100 px-4 py-2 rounded-full border border-slate-200">
              <span className="text-sm font-bold text-slate-900">{posts.length}</span>
              <span className="text-sm text-slate-600 ml-1">total posts</span>
            </div>
            <div className="bg-green-50 px-3 py-2 rounded-full border border-green-200 text-sm">
              <span className="text-green-700 font-medium">{statusCounts.published}</span>
              <span className="text-green-600 ml-1">published</span>
            </div>
            <div className="bg-amber-50 px-3 py-2 rounded-full border border-amber-200 text-sm">
              <span className="text-amber-700 font-medium">{statusCounts.pending}</span>
              <span className="text-amber-600 ml-1">pending</span>
            </div>
            {statusCounts.failed > 0 && (
              <div className="bg-red-50 px-3 py-2 rounded-full border border-red-200 text-sm">
                <span className="text-red-700 font-medium">{statusCounts.failed}</span>
                <span className="text-red-600 ml-1">failed</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {posts.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-slate-200 shadow-xl">
          <div className="relative inline-block mb-6">
            <Instagram className="w-16 h-16 text-slate-400 mx-auto" />
            <div className="absolute inset-0 bg-slate-500 blur-2xl opacity-20"></div>
          </div>
          <p className="text-lg font-semibold text-slate-900 mb-2">No Instagram posts found</p>
          <p className="text-sm text-slate-600 max-w-md mx-auto">
            Content will appear here after the content creation agent runs
          </p>
        </div>
      ) : (
        <InstagramPostGrid posts={posts} accountName={selectedAsset.name} />
      )}
    </div>
  )
}
