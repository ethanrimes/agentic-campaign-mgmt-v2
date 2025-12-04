// frontend/app/api/verifier-responses/route.ts

import { NextRequest, NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'

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
    const completed_post_id = searchParams.get('completed_post_id')

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
      // Fetch by ID
      queryParams.set('id', `eq.${id}`)
    } else if (completed_post_id) {
      // Fetch by completed post ID (get most recent)
      queryParams.set('completed_post_id', `eq.${completed_post_id}`)
      queryParams.set('order', 'created_at.desc')
      queryParams.set('limit', '1')
    } else {
      // Fetch all
      queryParams.set('order', 'created_at.desc')
    }

    const url = `${SUPABASE_URL}/rest/v1/verifier_responses?${queryParams.toString()}`

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
        { error: 'Failed to fetch verifier responses' },
        { status: response.status }
      )
    }

    const data = await response.json()

    // If fetching by ID or completed_post_id, return just that item or null
    if (id || completed_post_id) {
      return NextResponse.json(data[0] || null)
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error('Error in verifier-responses API:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
