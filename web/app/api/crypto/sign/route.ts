import { NextResponse } from 'next/server'
import { sign } from 'lib/pqcl/dilithium'

export async function POST(request: Request) {
  try {
    const { message, privateKey } = await request.json()
    
    if (!message || !privateKey) {
      return NextResponse.json(
        { error: 'Missing required parameters' },
        { status: 400 }
      )
    }

    const signingKey = Buffer.from(privateKey, 'hex')
    const signature = await sign(message, signingKey)
    
    return NextResponse.json({
      signature: signature.toString('hex')
    })
  } catch (error) {
    console.error('Error signing message:', error)
    return NextResponse.json(
      { error: 'Failed to sign message' },
      { status: 500 }
    )
  }
} 