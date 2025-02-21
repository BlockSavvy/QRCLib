'use client'

import { useState, useEffect } from 'react'

interface Message {
  id: string
  sender: string
  recipient: string
  content: string
  timestamp: string
  signature: string
}

export default function MessagingPage() {
  const [loading, setLoading] = useState(false)
  const [wallet, setWallet] = useState<{
    address: string
    publicKey: string
    privateKey: string
  } | null>(null)
  const [testIdentities, setTestIdentities] = useState<Array<{
    address: string
    publicKey: string
    label: string
  }>>([])
  const [recipient, setRecipient] = useState('')
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<Message[]>([])

  const createWallet = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/crypto/generate-keys')
      const data = await response.json()
      setWallet({
        address: `0x${data.publicKey.slice(0, 40)}`,
        publicKey: data.publicKey,
        privateKey: data.privateKey
      })
    } catch (error) {
      console.error('Error creating wallet:', error)
    }
    setLoading(false)
  }

  const createTestIdentity = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/crypto/generate-keys')
      const data = await response.json()
      const newIdentity = {
        address: `0x${data.publicKey.slice(0, 40)}`,
        publicKey: data.publicKey,
        label: `Test Identity ${testIdentities.length + 1}`
      }
      setTestIdentities([...testIdentities, newIdentity])
      // If no recipient is selected and we have test identities, select the first one
      if (!recipient && testIdentities.length === 0) {
        setRecipient(newIdentity.address)
      }
    } catch (error) {
      console.error('Error creating test identity:', error)
    }
    setLoading(false)
  }

  const sendMessage = async () => {
    if (!wallet || !recipient || !message) return
    setLoading(true)
    try {
      // Sign message
      const signResponse = await fetch('/api/crypto/sign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          privateKey: wallet.privateKey
        })
      })
      const { signature } = await signResponse.json()

      // Encrypt and send message
      const response = await fetch('/api/crypto/messaging', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sender: wallet.address,
          recipient,
          message,
          signature
        })
      })
      
      if (response.ok) {
        const newMessage = await response.json()
        setMessages([...messages, newMessage])
        setMessage('')
      }
    } catch (error) {
      console.error('Error sending message:', error)
    }
    setLoading(false)
  }

  useEffect(() => {
    const fetchMessages = async () => {
      if (!wallet) return
      try {
        const response = await fetch('/api/crypto/messaging')
        if (response.ok) {
          const data = await response.json()
          setMessages(data.messages)
        }
      } catch (error) {
        console.error('Error fetching messages:', error)
      }
    }
    fetchMessages()
  }, [wallet])

  return (
    <div className="space-y-12">
      <section>
        <h1 className="text-3xl font-bold neon-text mb-4">
          Quantum-Resistant Secure Messaging
        </h1>
        <p className="text-secondary mb-8">
          Experience end-to-end encrypted messaging using quantum-resistant cryptography.
          Messages are signed with Dilithium signatures and encrypted using Kyber key exchange.
        </p>
      </section>

      <section className="space-y-6">
        <div className="cyber-card p-6 rounded-lg">
          <h2 className="text-xl font-semibold neon-text mb-4">Your Identity</h2>
          {!wallet ? (
            <button
              onClick={createWallet}
              disabled={loading}
              className="cyber-button px-4 py-2 rounded disabled:opacity-50"
            >
              Create Identity
            </button>
          ) : (
            <div className="space-y-2">
              <div>
                <label className="block text-sm font-medium text-secondary">Your Address</label>
                <pre className="mt-1 p-2 rounded text-sm overflow-x-auto neon-text">
                  {wallet.address}
                </pre>
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary">Public Key</label>
                <pre className="mt-1 p-2 rounded text-sm overflow-x-auto">
                  {wallet.publicKey}
                </pre>
              </div>
            </div>
          )}
        </div>

        <div className="cyber-card p-6 rounded-lg">
          <h2 className="text-xl font-semibold neon-text mb-4">Test Identities</h2>
          <div className="space-y-4">
            <button
              onClick={createTestIdentity}
              disabled={loading}
              className="cyber-button px-4 py-2 rounded disabled:opacity-50"
            >
              Create Test Identity
            </button>
            
            <div className="space-y-2">
              {testIdentities.map((identity) => (
                <div key={identity.address} className="p-4 border border-accent-neon rounded-lg">
                  <div className="flex justify-between items-center">
                    <span className="text-accent-neon">{identity.label}</span>
                    <button
                      onClick={() => setRecipient(identity.address)}
                      className="cyber-button px-2 py-1 text-sm rounded"
                    >
                      Select as Recipient
                    </button>
                  </div>
                  <div className="mt-2">
                    <span className="text-secondary">Address: </span>
                    <span className="text-text-primary">{identity.address}</span>
                  </div>
                </div>
              ))}
              {testIdentities.length === 0 && (
                <p className="text-secondary text-center">No test identities created yet</p>
              )}
            </div>
          </div>
        </div>

        <div className="cyber-card p-6 rounded-lg">
          <h2 className="text-xl font-semibold neon-text mb-4">Send Message</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-secondary">Recipient Address</label>
              <input
                type="text"
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
                className="mt-1 block w-full rounded-md border-accent-neon bg-background-darker text-text-primary shadow-sm focus:border-accent-cyber focus:ring-accent-cyber"
                placeholder="Enter recipient's address"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary">Message</label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="mt-1 block w-full rounded-md border-accent-neon bg-background-darker text-text-primary shadow-sm focus:border-accent-cyber focus:ring-accent-cyber"
                rows={3}
                placeholder="Enter your message"
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={loading || !wallet || !recipient || !message}
              className="cyber-button px-4 py-2 rounded disabled:opacity-50"
            >
              Send Encrypted Message
            </button>
          </div>
        </div>

        <div className="cyber-card p-6 rounded-lg">
          <h2 className="text-xl font-semibold neon-text mb-4">Message History</h2>
          <div className="space-y-4">
            {messages.map(msg => (
              <div key={msg.id} className="p-4 border border-accent-neon rounded-lg">
                <div className="grid grid-cols-2 gap-2 text-sm mb-2">
                  <div>
                    <span className="text-secondary">From: </span>
                    <span className="text-text-primary">{msg.sender}</span>
                  </div>
                  <div>
                    <span className="text-secondary">To: </span>
                    <span className="text-text-primary">{msg.recipient}</span>
                  </div>
                  <div className="col-span-2">
                    <span className="text-secondary">Time: </span>
                    <span className="text-text-primary">
                      {new Date(msg.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
                <p className="text-text-primary">{msg.content}</p>
              </div>
            ))}
            {messages.length === 0 && (
              <p className="text-secondary text-center">No messages yet</p>
            )}
          </div>
        </div>
      </section>
    </div>
  )
} 