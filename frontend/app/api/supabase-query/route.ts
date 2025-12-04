// frontend/app/api/supabase-query/route.ts

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
    const table = searchParams.get('table')
    const select = searchParams.get('select') || '*'
    const business_asset_id = searchParams.get('business_asset_id')

    if (!table) {
      return NextResponse.json(
        { error: 'Table parameter is required' },
        { status: 400 }
      )
    }

    if (!business_asset_id) {
      return NextResponse.json(
        { error: 'business_asset_id parameter is required' },
        { status: 400 }
      )
    }

    // Build query parameters
    const queryParams = new URLSearchParams()
    queryParams.set('select', select)
    queryParams.set('business_asset_id', `eq.${business_asset_id}`)

    // Add any additional filter parameters
    for (const [key, value] of searchParams.entries()) {
      if (key !== 'table' && key !== 'select' && key !== 'business_asset_id') {
        queryParams.set(key, value)
      }
    }

    // Fetch from Supabase
    const url = `${SUPABASE_URL}/rest/v1/${table}?${queryParams.toString()}`

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
        { error: 'Failed to fetch data from Supabase' },
        { status: response.status }
      )
    }

    const data = await response.json()

    return NextResponse.json({
      data,
      count: Array.isArray(data) ? data.length : 1,
      business_asset_id,
    })
  } catch (error) {
    console.error('Error in supabase-query:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
