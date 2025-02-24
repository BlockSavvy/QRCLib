import { NextResponse } from 'next/server'
import { verify } from '../../../lib/pqcl/dilithium'

export async function POST(request: Request) {
  try {
    const { message, signature, publicKey } = await request.json()
    
    if (!message || !signature || !publicKey) {
      return NextResponse.json(
        { error: 'Missing required parameters' },
        { status: 400 }
      )
    }

    const verificationKey = Buffer.from(publicKey, 'hex')
    const signatureBuffer = Buffer.from(signature, 'hex')
    const isValid = await verify(message, signatureBuffer, verificationKey)
    
    return NextResponse.json({ valid: isValid })
  } catch (error) {
    console.error('Error verifying signature:', error)
    return NextResponse.json(
      { error: 'Failed to verify signature' },
      { status: 500 }
    )
  }
} 