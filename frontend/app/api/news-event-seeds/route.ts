// frontend/app/api/news-event-seeds/route.ts

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

    if (!business_asset_id) {
      return NextResponse.json(
        { error: 'business_asset_id parameter is required' },
        { status: 400 }
      )
    }

    // Build query parameters with source relation via junction table
    // This fetches news_event_seeds with their related sources through news_event_seed_sources
    const queryParams = new URLSearchParams()
    queryParams.set('select', 'id,name,start_time,end_time,location,description,created_at,business_asset_id,news_event_seed_sources(sources(id,url,key_findings,found_by,created_at))')
    queryParams.set('business_asset_id', `eq.${business_asset_id}`)

    if (id) {
      queryParams.set('id', `eq.${id}`)
    } else {
      queryParams.set('order', 'created_at.desc')
    }

    const url = `${SUPABASE_URL}/rest/v1/news_event_seeds?${queryParams.toString()}`

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
        { error: 'Failed to fetch news event seeds' },
        { status: response.status }
      )
    }

    const data = await response.json()

    // Transform the nested junction table structure to flat sources array
    // From: { news_event_seed_sources: [{ sources: { id, url, ... } }] }
    // To:   { sources: [{ id, url, ... }] }
    const transformedData = data.map((seed: any) => {
      const sources = seed.news_event_seed_sources
        ?.map((junction: any) => junction.sources)
        .filter(Boolean) || []

      // Remove the junction table field and add flattened sources
      const { news_event_seed_sources, ...rest } = seed
      return { ...rest, sources }
    })

    // If fetching single item, return just that item or null
    if (id) {
      return NextResponse.json(transformedData[0] || null)
    }

    return NextResponse.json(transformedData)
  } catch (error) {
    console.error('Error in news-event-seeds API:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
