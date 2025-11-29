// frontend/app/api/business-assets/route.ts

import { NextResponse } from 'next/server'

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

export async function GET() {
  try {
    if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
      return NextResponse.json(
        { error: 'Supabase configuration missing' },
        { status: 500 }
      )
    }

    // Fetch active business assets from Supabase
    const response = await fetch(
      `${SUPABASE_URL}/rest/v1/business_assets?is_active=eq.true&select=id,name,is_active,created_at,updated_at&order=name.asc`,
      {
        headers: {
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json',
        },
        cache: 'no-store', // Don't cache to always get fresh data
      }
    )

    if (!response.ok) {
      const errorText = await response.text()
      console.error('Supabase error:', errorText)
      return NextResponse.json(
        { error: 'Failed to fetch business assets' },
        { status: response.status }
      )
    }

    const assets = await response.json()

    return NextResponse.json({
      assets,
      count: assets.length,
    })
  } catch (error) {
    console.error('Error fetching business assets:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
