// frontend/app/api/completed-posts/route.ts

import { NextRequest, NextResponse } from 'next/server'

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

export async function GET(request: NextRequest) {
  try {
    if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
      return NextResponse.json(
        { error: 'Supabase configuration missing' },
        { status: 500 }
      )
    }

    const searchParams = request.nextUrl.searchParams
    const business_asset_id = searchParams.get('business_asset_id')
    const id = searchParams.get('id')
    const platform = searchParams.get('platform')
    const seed_id = searchParams.get('seed_id')
    const seed_type = searchParams.get('seed_type')

    if (!business_asset_id) {
      return NextResponse.json(
        { error: 'business_asset_id parameter is required' },
        { status: 400 }
      )
    }

    // Build query parameters
    const queryParams = new URLSearchParams()
    queryParams.set('select', '*')
    queryParams.set('business_asset_id', `eq.${business_asset_id}`)

    if (id) {
      queryParams.set('id', `eq.${id}`)
    }

    if (platform) {
      queryParams.set('platform', `eq.${platform}`)
    }

    if (seed_id && seed_type) {
      const seedColumn = seed_type === 'news_event'
        ? 'news_event_seed_id'
        : seed_type === 'trend'
        ? 'trend_seed_id'
        : 'ungrounded_seed_id'
      queryParams.set(seedColumn, `eq.${seed_id}`)
    }

    if (!id) {
      queryParams.set('order', 'created_at.desc')
    }

    const url = `${SUPABASE_URL}/rest/v1/completed_posts?${queryParams.toString()}`

    const response = await fetch(url, {
      headers: {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('Supabase error:', errorText)
      return NextResponse.json(
        { error: 'Failed to fetch completed posts' },
        { status: response.status }
      )
    }

    const posts = await response.json()

    // Enrich posts with media URLs and seed info
    const enrichedPosts = await Promise.all(
      posts.map(async (post: any) => {
        let enrichedPost = { ...post }

        // Fetch seed name
        let seedName = ''
        let seedId = ''
        let seedType: 'news_event' | 'trend' | 'ungrounded' | null = null

        if (post.news_event_seed_id) {
          seedId = post.news_event_seed_id
          seedType = 'news_event'
          const seedUrl = `${SUPABASE_URL}/rest/v1/news_event_seeds?id=eq.${post.news_event_seed_id}&select=name`
          const seedResponse = await fetch(seedUrl, {
            headers: {
              'apikey': SUPABASE_ANON_KEY,
              'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
            },
            cache: 'no-store',
          })
          if (seedResponse.ok) {
            const seedData = await seedResponse.json()
            seedName = seedData[0]?.name || 'Unknown'
          }
        } else if (post.trend_seed_id) {
          seedId = post.trend_seed_id
          seedType = 'trend'
          const seedUrl = `${SUPABASE_URL}/rest/v1/trend_seeds?id=eq.${post.trend_seed_id}&select=name`
          const seedResponse = await fetch(seedUrl, {
            headers: {
              'apikey': SUPABASE_ANON_KEY,
              'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
            },
            cache: 'no-store',
          })
          if (seedResponse.ok) {
            const seedData = await seedResponse.json()
            seedName = seedData[0]?.name || 'Unknown'
          }
        } else if (post.ungrounded_seed_id) {
          seedId = post.ungrounded_seed_id
          seedType = 'ungrounded'
          const seedUrl = `${SUPABASE_URL}/rest/v1/ungrounded_seeds?id=eq.${post.ungrounded_seed_id}&select=idea`
          const seedResponse = await fetch(seedUrl, {
            headers: {
              'apikey': SUPABASE_ANON_KEY,
              'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
            },
            cache: 'no-store',
          })
          if (seedResponse.ok) {
            const seedData = await seedResponse.json()
            seedName = seedData[0]?.idea || 'Unknown'
          }
        }

        enrichedPost.content_seed_id = seedId
        enrichedPost.content_seed_type = seedType
        enrichedPost.seed_name = seedName

        // Fetch media URLs if media_ids exist
        if (post.media_ids && Array.isArray(post.media_ids) && post.media_ids.length > 0) {
          const mediaIds = post.media_ids.join(',')
          const mediaUrl = `${SUPABASE_URL}/rest/v1/media?id=in.(${mediaIds})&select=public_url`
          const mediaResponse = await fetch(mediaUrl, {
            headers: {
              'apikey': SUPABASE_ANON_KEY,
              'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
            },
            cache: 'no-store',
          })
          if (mediaResponse.ok) {
            const mediaData = await mediaResponse.json()
            enrichedPost.media_urls = mediaData.map((m: any) => m.public_url)
          }
        }

        return enrichedPost
      })
    )

    // If fetching single item, return just that item or null
    if (id) {
      return NextResponse.json(enrichedPosts[0] || null)
    }

    return NextResponse.json(enrichedPosts)
  } catch (error) {
    console.error('Error in completed-posts API:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
