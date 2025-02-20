import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Forward to Flask health check
    const response = await fetch('http://127.0.0.1:5000/health')
    if (response.ok) {
      return NextResponse.json({ status: 'healthy' })
    }
    return NextResponse.json({ status: 'unhealthy' }, { status: 500 })
  } catch (error) {
    return NextResponse.json({ status: 'unhealthy', error: String(error) }, { status: 500 })
  }
}
