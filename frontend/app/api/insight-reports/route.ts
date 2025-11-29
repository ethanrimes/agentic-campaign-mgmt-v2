// frontend/app/api/insight-reports/route.ts

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

    // Build query parameters
    const queryParams = new URLSearchParams()
    queryParams.set('select', '*')
    queryParams.set('business_asset_id', `eq.${business_asset_id}`)

    if (id) {
      queryParams.set('id', `eq.${id}`)
    } else {
      queryParams.set('order', 'created_at.desc')
    }

    const url = `${SUPABASE_URL}/rest/v1/insight_reports?${queryParams.toString()}`

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
        { error: 'Failed to fetch insight reports' },
        { status: response.status }
      )
    }

    const data = await response.json()

    // If fetching single item, return just that item or null
    if (id) {
      return NextResponse.json(data[0] || null)
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error('Error in insight-reports API:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
