// frontend/app/api/post-counts/route.ts

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

    if (!business_asset_id) {
      return NextResponse.json(
        { error: 'business_asset_id parameter is required' },
        { status: 400 }
      )
    }

    // Fetch all completed posts for this business asset
    const queryParams = new URLSearchParams()
    queryParams.set('select', 'news_event_seed_id,trend_seed_id,ungrounded_seed_id')
    queryParams.set('business_asset_id', `eq.${business_asset_id}`)

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
        { error: 'Failed to fetch post counts' },
        { status: response.status }
      )
    }

    const posts = await response.json()

    const counts: Record<string, number> = {}

    // Count posts by seed
    posts.forEach((post: any) => {
      if (post.news_event_seed_id) {
        counts[post.news_event_seed_id] = (counts[post.news_event_seed_id] || 0) + 1
      }
      if (post.trend_seed_id) {
        counts[post.trend_seed_id] = (counts[post.trend_seed_id] || 0) + 1
      }
      if (post.ungrounded_seed_id) {
        counts[post.ungrounded_seed_id] = (counts[post.ungrounded_seed_id] || 0) + 1
      }
    })

    return NextResponse.json(counts)
  } catch (error) {
    console.error('Error in post-counts API:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
