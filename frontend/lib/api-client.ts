// frontend/lib/api-client.ts
// Client-side API helpers that call Next.js API routes with business_asset_id

'use client'

import type {
  NewsEventSeed,
  TrendSeed,
  UngroundedSeed,
  CompletedPost,
  ContentCreationTask,
  InsightReport,
  VerifierResponse,
} from '@/types'

// Helper to build URL with business_asset_id
function buildApiUrl(path: string, params: Record<string, string> = {}): string {
  const queryParams = new URLSearchParams(params)
  return `${path}?${queryParams.toString()}`
}

// News Event Seeds
export async function getNewsEventSeeds(business_asset_id: string): Promise<NewsEventSeed[]> {
  const response = await fetch(buildApiUrl('/api/news-event-seeds', { business_asset_id }))
  if (!response.ok) {
    throw new Error('Failed to fetch news event seeds')
  }
  return response.json()
}

export async function getNewsEventSeed(id: string, business_asset_id: string): Promise<NewsEventSeed | null> {
  const response = await fetch(buildApiUrl('/api/news-event-seeds', { business_asset_id, id }))
  if (!response.ok) {
    throw new Error('Failed to fetch news event seed')
  }
  return response.json()
}

// Trend Seeds
export async function getTrendSeeds(business_asset_id: string): Promise<TrendSeed[]> {
  const response = await fetch(buildApiUrl('/api/trend-seeds', { business_asset_id }))
  if (!response.ok) {
    throw new Error('Failed to fetch trend seeds')
  }
  return response.json()
}

export async function getTrendSeed(id: string, business_asset_id: string): Promise<TrendSeed | null> {
  const response = await fetch(buildApiUrl('/api/trend-seeds', { business_asset_id, id }))
  if (!response.ok) {
    throw new Error('Failed to fetch trend seed')
  }
  return response.json()
}

// Ungrounded Seeds
export async function getUngroundedSeeds(business_asset_id: string): Promise<UngroundedSeed[]> {
  const response = await fetch(buildApiUrl('/api/ungrounded-seeds', { business_asset_id }))
  if (!response.ok) {
    throw new Error('Failed to fetch ungrounded seeds')
  }
  return response.json()
}

export async function getUngroundedSeed(id: string, business_asset_id: string): Promise<UngroundedSeed | null> {
  const response = await fetch(buildApiUrl('/api/ungrounded-seeds', { business_asset_id, id }))
  if (!response.ok) {
    throw new Error('Failed to fetch ungrounded seed')
  }
  return response.json()
}

// Completed Posts
export async function getCompletedPosts(
  business_asset_id: string,
  platform?: 'facebook' | 'instagram'
): Promise<CompletedPost[]> {
  const params: Record<string, string> = { business_asset_id }
  if (platform) {
    params.platform = platform
  }

  const response = await fetch(buildApiUrl('/api/completed-posts', params))
  if (!response.ok) {
    throw new Error('Failed to fetch completed posts')
  }
  return response.json()
}

export async function getCompletedPost(id: string, business_asset_id: string): Promise<CompletedPost | null> {
  const response = await fetch(buildApiUrl('/api/completed-posts', { business_asset_id, id }))
  if (!response.ok) {
    throw new Error('Failed to fetch completed post')
  }
  return response.json()
}

// Content Creation Tasks
export async function getContentCreationTasksBySeed(
  seedId: string,
  seedType: 'news_event' | 'trend' | 'ungrounded',
  business_asset_id: string
): Promise<ContentCreationTask[]> {
  const response = await fetch(buildApiUrl('/api/content-creation-tasks', {
    business_asset_id,
    seed_id: seedId,
    seed_type: seedType
  }))
  if (!response.ok) {
    throw new Error('Failed to fetch content creation tasks')
  }
  return response.json()
}

export async function getCompletedPostsBySeed(
  seedId: string,
  seedType: 'news_event' | 'trend' | 'ungrounded',
  business_asset_id: string
): Promise<CompletedPost[]> {
  const response = await fetch(buildApiUrl('/api/completed-posts', {
    business_asset_id,
    seed_id: seedId,
    seed_type: seedType
  }))
  if (!response.ok) {
    throw new Error('Failed to fetch completed posts by seed')
  }
  return response.json()
}

// Get post counts by seed
export async function getPostCountsBySeed(business_asset_id: string): Promise<Record<string, number>> {
  const response = await fetch(buildApiUrl('/api/post-counts', { business_asset_id }))
  if (!response.ok) {
    throw new Error('Failed to fetch post counts')
  }
  return response.json()
}

// Insight Reports
export async function getInsightReports(business_asset_id: string): Promise<InsightReport[]> {
  const response = await fetch(buildApiUrl('/api/insight-reports', { business_asset_id }))
  if (!response.ok) {
    throw new Error('Failed to fetch insight reports')
  }
  return response.json()
}

export async function getInsightReport(id: string, business_asset_id: string): Promise<InsightReport | null> {
  const response = await fetch(buildApiUrl('/api/insight-reports', { business_asset_id, id }))
  if (!response.ok) {
    throw new Error('Failed to fetch insight report')
  }
  return response.json()
}

// Verifier Responses
export async function getVerifierResponses(business_asset_id: string): Promise<VerifierResponse[]> {
  const response = await fetch(buildApiUrl('/api/verifier-responses', { business_asset_id }))
  if (!response.ok) {
    throw new Error('Failed to fetch verifier responses')
  }
  return response.json()
}

export async function getVerifierResponse(id: string, business_asset_id: string): Promise<VerifierResponse | null> {
  const response = await fetch(buildApiUrl('/api/verifier-responses', { business_asset_id, id }))
  if (!response.ok) {
    throw new Error('Failed to fetch verifier response')
  }
  return response.json()
}

export async function getVerifierResponseByPostId(
  completed_post_id: string,
  business_asset_id: string
): Promise<VerifierResponse | null> {
  const response = await fetch(buildApiUrl('/api/verifier-responses', {
    business_asset_id,
    completed_post_id
  }))
  if (!response.ok) {
    throw new Error('Failed to fetch verifier response by post ID')
  }
  return response.json()
}

// Insights
import type {
  CachedInsights,
  InsightsRefreshResponse,
  FacebookPostInsights,
  FacebookVideoInsights,
  InstagramMediaInsights,
} from '@/types'

export async function getCachedInsights(
  business_asset_id: string,
  platform: 'facebook' | 'instagram' | 'all' = 'all'
): Promise<CachedInsights> {
  const response = await fetch(buildApiUrl('/api/insights', { business_asset_id, platform }))
  if (!response.ok) {
    throw new Error('Failed to fetch cached insights')
  }
  return response.json()
}

export async function refreshInsights(
  business_asset_id: string,
  type: 'account' | 'posts' | 'all' = 'all'
): Promise<InsightsRefreshResponse> {
  const response = await fetch('/api/insights/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ business_asset_id, type }),
  })
  return response.json()
}

// Helper to get post insights by platform_post_id
export async function getPostInsights(
  business_asset_id: string,
  platform_post_id: string,
  platform: 'facebook' | 'instagram'
): Promise<FacebookPostInsights | InstagramMediaInsights | null> {
  const insights = await getCachedInsights(business_asset_id, platform)

  if (platform === 'facebook') {
    return insights.facebook_posts?.find(p => p.platform_post_id === platform_post_id) || null
  } else {
    return insights.instagram_media?.find(m => m.platform_media_id === platform_post_id) || null
  }
}

// Helper to get video insights
export async function getVideoInsights(
  business_asset_id: string,
  video_id: string
): Promise<FacebookVideoInsights | null> {
  const insights = await getCachedInsights(business_asset_id, 'facebook')
  return insights.facebook_videos?.find(v => v.platform_video_id === video_id) || null
}
