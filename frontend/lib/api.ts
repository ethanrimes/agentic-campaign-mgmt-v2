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

  // Fetch media URLs for posts with media_ids
  const postsWithMedia = await Promise.all(
    (data || []).map(async (post) => {
      if (post.media_ids && Array.isArray(post.media_ids) && post.media_ids.length > 0) {
        const { data: mediaData, error: mediaError } = await supabase
          .from('media')
          .select('public_url')
          .in('id', post.media_ids)

        if (!mediaError && mediaData) {
          return {
            ...post,
            media_urls: mediaData.map(m => m.public_url)
          }
        }
      }
      return post
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

export async function getCompletedPostsBySeed(seedId: string): Promise<CompletedPost[]> {
  const { data, error } = await supabase
    .from('completed_posts')
    .select('*')
    .eq('content_seed_id', seedId)
    .order('created_at', { ascending: false })

  if (error) throw error

  // Fetch media URLs for posts with media_ids
  const postsWithMedia = await Promise.all(
    (data || []).map(async (post) => {
      if (post.media_ids && Array.isArray(post.media_ids) && post.media_ids.length > 0) {
        const { data: mediaData, error: mediaError } = await supabase
          .from('media')
          .select('public_url')
          .in('id', post.media_ids)

        if (!mediaError && mediaData) {
          return {
            ...post,
            media_urls: mediaData.map(m => m.public_url)
          }
        }
      }
      return post
    })
  )

  return postsWithMedia
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
