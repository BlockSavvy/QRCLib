'use client'

import { useState } from 'react'

export default function BasicExamplesPage() {
  const [loading, setLoading] = useState(false)
  const [keyPair, setKeyPair] = useState<{
    publicKey: string
    privateKey: string
  } | null>(null)
  const [message, setMessage] = useState('')
  const [signature, setSignature] = useState('')
  const [verificationResult, setVerificationResult] = useState<boolean | null>(null)

  const generateKeys = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/crypto/generate-keys')
      const data = await response.json()
      setKeyPair(data)
    } catch (error) {
      console.error('Error generating keys:', error)
    }
    setLoading(false)
  }

  const signMessage = async () => {
    if (!keyPair || !message) return
    setLoading(true)
    try {
      const response = await fetch('/api/crypto/sign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          privateKey: keyPair.privateKey
        })
      })
      const data = await response.json()
      setSignature(data.signature)
    } catch (error) {
      console.error('Error signing message:', error)
    }
    setLoading(false)
  }

  const verifySignature = async () => {
    if (!keyPair || !message || !signature) return
    setLoading(true)
    try {
      const response = await fetch('/api/crypto/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          signature,
          publicKey: keyPair.publicKey
        })
      })
      const data = await response.json()
      setVerificationResult(data.valid)
    } catch (error) {
      console.error('Error verifying signature:', error)
    }
    setLoading(false)
  }

  return (
    <div className="space-y-12">
      <section>
        <h1 className="text-3xl font-bold neon-text mb-4">
          Basic Cryptographic Operations
        </h1>
        <p className="text-secondary mb-8">
          Explore the fundamental operations of quantum-resistant cryptography:
          key generation, digital signatures, and verification.
        </p>
      </section>

      <section className="space-y-6">
        <div className="cyber-card p-6 rounded-lg">
          <h2 className="text-xl font-semibold neon-text mb-4">Key Generation</h2>
          <button
            onClick={generateKeys}
            disabled={loading}
            className="cyber-button px-4 py-2 rounded disabled:opacity-50"
          >
            Generate Key Pair
          </button>
          {keyPair && (
            <div className="mt-4 space-y-2">
              <div>
                <label className="block text-sm font-medium text-secondary">Public Key</label>
                <pre className="mt-1 p-2 rounded text-sm overflow-x-auto">
                  {keyPair.publicKey}
                </pre>
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary">Private Key</label>
                <pre className="mt-1 p-2 rounded text-sm overflow-x-auto">
                  {keyPair.privateKey}
                </pre>
              </div>
            </div>
          )}
        </div>

        <div className="cyber-card p-6 rounded-lg">
          <h2 className="text-xl font-semibold neon-text mb-4">Digital Signatures</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-secondary">Message</label>
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="mt-1 block w-full rounded-md border-accent-neon bg-background-darker text-text-primary shadow-sm focus:border-accent-cyber focus:ring-accent-cyber"
                placeholder="Enter a message to sign"
              />
            </div>
            <button
              onClick={signMessage}
              disabled={loading || !keyPair || !message}
              className="cyber-button px-4 py-2 rounded disabled:opacity-50"
            >
              Sign Message
            </button>
            {signature && (
              <div>
                <label className="block text-sm font-medium text-secondary">Signature</label>
                <pre className="mt-1 p-2 rounded text-sm overflow-x-auto">
                  {signature}
                </pre>
              </div>
            )}
          </div>
        </div>

        <div className="cyber-card p-6 rounded-lg">
          <h2 className="text-xl font-semibold neon-text mb-4">Signature Verification</h2>
          <button
            onClick={verifySignature}
            disabled={loading || !keyPair || !message || !signature}
            className="cyber-button px-4 py-2 rounded disabled:opacity-50"
          >
            Verify Signature
          </button>
          {verificationResult !== null && (
            <div className={`mt-4 p-4 rounded ${verificationResult ? 'bg-accent-neon bg-opacity-10' : 'bg-accent-cyber bg-opacity-10'}`}>
              <p className={verificationResult ? 'neon-text' : 'text-accent-cyber'}>
                Signature is {verificationResult ? 'valid' : 'invalid'}
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  )
} 