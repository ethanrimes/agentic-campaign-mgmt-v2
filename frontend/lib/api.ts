// frontend/lib/api.ts

import { supabase } from './supabase'
import type {
  NewsEventSeed,
  TrendSeed,
  UngroundedSeed,
  CompletedPost,
  ContentCreationTask,
  InsightReport,
} from '@/types'

// News Event Seeds
export async function getNewsEventSeeds(): Promise<NewsEventSeed[]> {
  const { data, error } = await supabase
    .from('news_event_seeds')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) throw error
  return data || []
}

export async function getNewsEventSeed(id: string): Promise<NewsEventSeed | null> {
  const { data, error } = await supabase
    .from('news_event_seeds')
    .select('*')
    .eq('id', id)
    .single()

  if (error) throw error
  return data
}

// Trend Seeds
export async function getTrendSeeds(): Promise<TrendSeed[]> {
  const { data, error } = await supabase
    .from('trend_seeds')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) throw error
  return data || []
}

export async function getTrendSeed(id: string): Promise<TrendSeed | null> {
  const { data, error } = await supabase
    .from('trend_seeds')
    .select('*')
    .eq('id', id)
    .single()

  if (error) throw error
  return data
}

// Ungrounded Seeds
export async function getUngroundedSeeds(): Promise<UngroundedSeed[]> {
  const { data, error } = await supabase
    .from('ungrounded_seeds')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) throw error
  return data || []
}

export async function getUngroundedSeed(id: string): Promise<UngroundedSeed | null> {
  const { data, error } = await supabase
    .from('ungrounded_seeds')
    .select('*')
    .eq('id', id)
    .single()

  if (error) throw error
  return data
}

// Helper function to get seed info from a post
async function enrichPostWithSeedInfo(post: any) {
  let seedName = ''
  let seedId = ''
  let seedType: 'news_event' | 'trend' | 'ungrounded' | null = null

  if (post.news_event_seed_id) {
    seedId = post.news_event_seed_id
    seedType = 'news_event'
    const { data } = await supabase
      .from('news_event_seeds')
      .select('name')
      .eq('id', post.news_event_seed_id)
      .single()
    seedName = data?.name || 'Unknown'
  } else if (post.trend_seed_id) {
    seedId = post.trend_seed_id
    seedType = 'trend'
    const { data } = await supabase
      .from('trend_seeds')
      .select('name')
      .eq('id', post.trend_seed_id)
      .single()
    seedName = data?.name || 'Unknown'
  } else if (post.ungrounded_seed_id) {
    seedId = post.ungrounded_seed_id
    seedType = 'ungrounded'
    const { data } = await supabase
      .from('ungrounded_seeds')
      .select('idea')
      .eq('id', post.ungrounded_seed_id)
      .single()
    seedName = data?.idea || 'Unknown'
  }

  return {
    ...post,
    content_seed_id: seedId,
    content_seed_type: seedType,
    seed_name: seedName,
  }
}

// Completed Posts
export async function getCompletedPosts(platform?: 'facebook' | 'instagram'): Promise<CompletedPost[]> {
  let query = supabase
    .from('completed_posts')
    .select('*')
    .order('created_at', { ascending: false })

  if (platform) {
    query = query.eq('platform', platform)
  }

  const { data, error } = await query

  if (error) throw error

  // Fetch media URLs and seed info for posts
  const postsWithMedia = await Promise.all(
    (data || []).map(async (post) => {
      let enrichedPost = await enrichPostWithSeedInfo(post)

      if (post.media_ids && Array.isArray(post.media_ids) && post.media_ids.length > 0) {
        const { data: mediaData, error: mediaError } = await supabase
          .from('media')
          .select('public_url')
          .in('id', post.media_ids)

        if (!mediaError && mediaData) {
          enrichedPost = {
            ...enrichedPost,
            media_urls: mediaData.map(m => m.public_url)
          }
        }
      }
      return enrichedPost
    })
  )

  return postsWithMedia
}

export async function getCompletedPost(id: string): Promise<CompletedPost | null> {
  const { data, error } = await supabase
    .from('completed_posts')
    .select('*')
    .eq('id', id)
    .single()

  if (error) throw error

  // Fetch media URLs if media_ids exist
  if (data && data.media_ids && Array.isArray(data.media_ids) && data.media_ids.length > 0) {
    const { data: mediaData, error: mediaError } = await supabase
      .from('media')
      .select('public_url')
      .in('id', data.media_ids)

    if (!mediaError && mediaData) {
      return {
        ...data,
        media_urls: mediaData.map(m => m.public_url)
      }
    }
  }

  return data
}

// Content Creation Tasks
export async function getContentCreationTasksBySeed(seedId: string): Promise<ContentCreationTask[]> {
  const { data, error } = await supabase
    .from('content_creation_tasks')
    .select('*')
    .eq('content_seed_id', seedId)
    .order('created_at', { ascending: false })

  if (error) throw error
  return data || []
}

export async function getCompletedPostsBySeed(seedId: string, seedType: 'news_event' | 'trend' | 'ungrounded'): Promise<CompletedPost[]> {
  // Determine which column to query based on seed type
  const seedColumn = seedType === 'news_event'
    ? 'news_event_seed_id'
    : seedType === 'trend'
    ? 'trend_seed_id'
    : 'ungrounded_seed_id'

  const { data, error } = await supabase
    .from('completed_posts')
    .select('*')
    .eq(seedColumn, seedId)
    .order('created_at', { ascending: false })

  if (error) throw error

  // Fetch media URLs for posts with media_ids
  const postsWithMedia = await Promise.all(
    (data || []).map(async (post) => {
      let enrichedPost = await enrichPostWithSeedInfo(post)

      if (post.media_ids && Array.isArray(post.media_ids) && post.media_ids.length > 0) {
        const { data: mediaData, error: mediaError } = await supabase
          .from('media')
          .select('public_url')
          .in('id', post.media_ids)

        if (!mediaError && mediaData) {
          enrichedPost = {
            ...enrichedPost,
            media_urls: mediaData.map(m => m.public_url)
          }
        }
      }
      return enrichedPost
    })
  )

  return postsWithMedia
}

// Get post counts by seed
export async function getPostCountsBySeed(): Promise<Record<string, number>> {
  const { data: newsEventCounts, error: newsError } = await supabase
    .from('completed_posts')
    .select('news_event_seed_id')
    .not('news_event_seed_id', 'is', null)

  const { data: trendCounts, error: trendError } = await supabase
    .from('completed_posts')
    .select('trend_seed_id')
    .not('trend_seed_id', 'is', null)

  const { data: ungroundedCounts, error: ungroundedError } = await supabase
    .from('completed_posts')
    .select('ungrounded_seed_id')
    .not('ungrounded_seed_id', 'is', null)

  const counts: Record<string, number> = {}

  // Count news event posts
  newsEventCounts?.forEach(post => {
    if (post.news_event_seed_id) {
      counts[post.news_event_seed_id] = (counts[post.news_event_seed_id] || 0) + 1
    }
  })

  // Count trend posts
  trendCounts?.forEach(post => {
    if (post.trend_seed_id) {
      counts[post.trend_seed_id] = (counts[post.trend_seed_id] || 0) + 1
    }
  })

  // Count ungrounded posts
  ungroundedCounts?.forEach(post => {
    if (post.ungrounded_seed_id) {
      counts[post.ungrounded_seed_id] = (counts[post.ungrounded_seed_id] || 0) + 1
    }
  })

  return counts
}

// Insight Reports
export async function getInsightReports(): Promise<InsightReport[]> {
  const { data, error } = await supabase
    .from('insight_reports')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) throw error
  return data || []
}

export async function getInsightReport(id: string): Promise<InsightReport | null> {
  const { data, error } = await supabase
    .from('insight_reports')
    .select('*')
    .eq('id', id)
    .single()

  if (error) throw error
  return data
}
