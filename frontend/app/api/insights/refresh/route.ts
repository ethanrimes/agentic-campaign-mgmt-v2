// frontend/app/api/insights/refresh/route.ts

import { NextRequest, NextResponse } from 'next/server'

// Webhook server URL - defaults to localhost for development
const WEBHOOK_URL = process.env.WEBHOOK_URL || 'http://localhost:3000'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { business_asset_id, type = 'all' } = body

    if (!business_asset_id) {
      return NextResponse.json(
        { status: 'error', message: 'business_asset_id is required' },
        { status: 400 }
      )
    }

    // Determine which endpoint to call based on type
    let endpoint: string
    switch (type) {
      case 'account':
        endpoint = '/insights/refresh-account'
        break
      case 'posts':
        endpoint = '/insights/refresh-posts'
        break
      case 'all':
      default:
        endpoint = '/insights/refresh-all'
        break
    }

    // Call the webhook server
    const response = await fetch(`${WEBHOOK_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ business_asset_id }),
    })

    const result = await response.json()

    // Return the response from the webhook server
    return NextResponse.json(result, { status: response.status })
  } catch (error) {
    console.error('Error in insights refresh API:', error)
    return NextResponse.json(
      { status: 'error', message: 'Failed to refresh insights' },
      { status: 500 }
    )
  }
}
