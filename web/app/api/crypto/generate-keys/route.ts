import { NextResponse } from 'next/server'
import { generateKeys } from '../../../../lib/pqcl/dilithium'

export async function GET() {
  try {
    const { signingKey, verificationKey } = await generateKeys()
    
    return NextResponse.json({
      publicKey: verificationKey.toString('hex'),
      privateKey: signingKey.toString('hex')
    })
  } catch (error) {
    console.error('Error generating keys:', error)
    return NextResponse.json(
      { error: 'Failed to generate keys' },
      { status: 500 }
    )
  }
} 