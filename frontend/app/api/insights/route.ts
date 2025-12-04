// frontend/app/api/insights/route.ts

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
    const platform = searchParams.get('platform') || 'all' // 'facebook', 'instagram', or 'all'

    if (!business_asset_id) {
      return NextResponse.json(
        { error: 'business_asset_id parameter is required' },
        { status: 400 }
      )
    }

    const result: Record<string, any> = {}

    // Fetch Facebook insights
    if (platform === 'facebook' || platform === 'all') {
      // Facebook page insights
      const fbPageUrl = `${SUPABASE_URL}/rest/v1/facebook_page_insights?business_asset_id=eq.${business_asset_id}&order=metrics_fetched_at.desc&limit=1`
      const fbPageResponse = await fetch(fbPageUrl, {
        headers: {
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        },
        cache: 'no-store',
      })
      if (fbPageResponse.ok) {
        const data = await fbPageResponse.json()
        result.facebook_page = data[0] || null
      }

      // Facebook post insights
      const fbPostsUrl = `${SUPABASE_URL}/rest/v1/facebook_post_insights?business_asset_id=eq.${business_asset_id}&order=metrics_fetched_at.desc&limit=50`
      const fbPostsResponse = await fetch(fbPostsUrl, {
        headers: {
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        },
        cache: 'no-store',
      })
      if (fbPostsResponse.ok) {
        result.facebook_posts = await fbPostsResponse.json()
      }

      // Facebook video insights
      const fbVideosUrl = `${SUPABASE_URL}/rest/v1/facebook_video_insights?business_asset_id=eq.${business_asset_id}&order=metrics_fetched_at.desc&limit=50`
      const fbVideosResponse = await fetch(fbVideosUrl, {
        headers: {
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        },
        cache: 'no-store',
      })
      if (fbVideosResponse.ok) {
        result.facebook_videos = await fbVideosResponse.json()
      }
    }

    // Fetch Instagram insights
    if (platform === 'instagram' || platform === 'all') {
      // Instagram account insights
      const igAccountUrl = `${SUPABASE_URL}/rest/v1/instagram_account_insights?business_asset_id=eq.${business_asset_id}&order=metrics_fetched_at.desc&limit=1`
      const igAccountResponse = await fetch(igAccountUrl, {
        headers: {
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        },
        cache: 'no-store',
      })
      if (igAccountResponse.ok) {
        const data = await igAccountResponse.json()
        result.instagram_account = data[0] || null
      }

      // Instagram media insights
      const igMediaUrl = `${SUPABASE_URL}/rest/v1/instagram_media_insights?business_asset_id=eq.${business_asset_id}&order=metrics_fetched_at.desc&limit=50`
      const igMediaResponse = await fetch(igMediaUrl, {
        headers: {
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        },
        cache: 'no-store',
      })
      if (igMediaResponse.ok) {
        result.instagram_media = await igMediaResponse.json()
      }
    }

    return NextResponse.json(result)
  } catch (error) {
    console.error('Error in insights API:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
