'use client'

import { useState, useEffect } from 'react'
import { SHA256 } from 'crypto-js'

interface BitcoinWallet {
  address: string
  publicKey: string
  privateKey: string
  balance: number
  protectedTransactions: ProtectedTransaction[]
}

interface ProtectedTransaction {
  id: string
  txHash: string
  sender: string
  recipient: string
  amount: number
  fee: number
  quantumSignature: string
  timestamp: string
  status: 'pending' | 'confirmed' | 'failed'
  blockHeight?: number
  confirmations: number
  protectionLevel: ProtectionLevel
  estimatedQuantumSecurity: number
  dilithiumStrength: string // Added for educational purposes
}

type ProtectionLevel = 'standard' | 'enhanced' | 'maximum'

interface NetworkStats {
  protectedTransactions: number
  totalQuantumSecurity: number
  averageProtectionLevel: ProtectionLevel
  dilithiumUsage: {
    standard: number
    enhanced: number
    maximum: number
  }
  recentBlocks: number
  networkHealth: number // Percentage
}

interface Tooltip {
  title: string
  content: string
}

const tooltips: Record<string, Tooltip> = {
  wallet: {
    title: "Quantum-Protected Bitcoin Wallet",
    content: "A hybrid wallet combining traditional Bitcoin keys with quantum-resistant signatures. Your funds remain secure even if quantum computers break ECDSA."
  },
  transaction: {
    title: "Protected Transactions",
    content: "Each transaction is secured with both Bitcoin's ECDSA and our Dilithium quantum-resistant signatures, ensuring long-term security."
  },
  fees: {
    title: "Protection Fees",
    content: "Additional fees cover the quantum protection overhead. Higher protection levels use stronger Dilithium parameters for better security."
  },
  security: {
    title: "Quantum Security Estimation",
    content: "We estimate protection time based on quantum computer development trends and the chosen Dilithium security level."
  },
  dilithium: {
    title: "Dilithium Protection",
    content: "Dilithium is a quantum-resistant signature scheme that remains secure even against attacks by quantum computers."
  }
}

function TooltipCard({ tooltip }: { tooltip: Tooltip }) {
  return (
    <div className="cyber-card p-4 mb-4">
      <h3 className="text-lg font-semibold neon-text mb-2">{tooltip.title}</h3>
      <p className="text-secondary">{tooltip.content}</p>
    </div>
  )
}

function generateTransactionHash(
  sender: string,
  recipient: string,
  amount: number,
  timestamp: string
): string {
  return SHA256(`${sender}:${recipient}:${amount}:${timestamp}`).toString()
}

function calculateFee(amount: number, protectionLevel: string): number {
  const baseFee = amount * 0.001 // 0.1% base fee
  const protectionMultiplier = {
    standard: 1,
    enhanced: 1.5,
    maximum: 2
  }[protectionLevel] || 1
  return baseFee * protectionMultiplier
}

function estimateQuantumSecurity(protectionLevel: string): number {
  // Estimated years of protection based on current quantum computing progress
  return {
    standard: 10,
    enhanced: 20,
    maximum: 30
  }[protectionLevel] || 10
}

export default function BitcoinProtectionPage() {
  const [loading, setLoading] = useState(false)
  const [wallet, setWallet] = useState<BitcoinWallet | null>(null)
  const [testWallets, setTestWallets] = useState<BitcoinWallet[]>([])
  const [selectedRecipient, setSelectedRecipient] = useState<string>('')
  const [amount, setAmount] = useState<string>('')
  const [protectionLevel, setProtectionLevel] = useState<ProtectionLevel>('standard')
  const [networkStats, setNetworkStats] = useState<NetworkStats>({
    protectedTransactions: 0,
    totalQuantumSecurity: 0,
    averageProtectionLevel: 'standard',
    dilithiumUsage: {
      standard: 0,
      enhanced: 0,
      maximum: 0
    },
    recentBlocks: 0,
    networkHealth: 100
  })

  useEffect(() => {
    // Simulate more realistic network statistics
    const interval = setInterval(() => {
      setNetworkStats(prev => {
        // Simulate organic growth in protected transactions
        const newTransactions = Math.floor(Math.random() * 2)
        const protectionLevel = ['standard', 'enhanced', 'maximum'][Math.floor(Math.random() * 3)] as ProtectionLevel
        
        // Update Dilithium usage stats
        const dilithiumUsage = { ...prev.dilithiumUsage }
        dilithiumUsage[protectionLevel] += newTransactions
        
        // Calculate network health (95-100%)
        const networkHealth = 95 + (Math.random() * 5)
        
        return {
          protectedTransactions: prev.protectedTransactions + newTransactions,
          totalQuantumSecurity: prev.totalQuantumSecurity + (newTransactions * estimateQuantumSecurity(protectionLevel)),
          averageProtectionLevel: protectionLevel,
          dilithiumUsage,
          recentBlocks: prev.recentBlocks + (Math.random() > 0.7 ? 1 : 0),
          networkHealth
        }
      })
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const createWallet = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/crypto/generate-keys')
      const { publicKey, privateKey } = await response.json()
      
      const newWallet: BitcoinWallet = {
        address: `bc1${publicKey.slice(0, 38)}`,
        publicKey,
        privateKey,
        balance: 10.0, // Mock balance
        protectedTransactions: []
      }
      
      setWallet(newWallet)
    } catch (error) {
      console.error('Error creating wallet:', error)
    }
    setLoading(false)
  }

  const createTestWallet = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/crypto/generate-keys')
      const { publicKey, privateKey } = await response.json()
      
      const newWallet: BitcoinWallet = {
        address: `bc1${publicKey.slice(0, 38)}`,
        publicKey,
        privateKey,
        balance: 5.0 + Math.random() * 10, // Random balance between 5-15 BTC
        protectedTransactions: []
      }
      
      setTestWallets(prev => [...prev, newWallet])
      if (!selectedRecipient) {
        setSelectedRecipient(newWallet.address)
      }
    } catch (error) {
      console.error('Error creating test wallet:', error)
    }
    setLoading(false)
  }

  const protectTransaction = async () => {
    if (!wallet || !selectedRecipient || !amount) return
    
    setLoading(true)
    try {
      const timestamp = new Date().toISOString()
      const txHash = generateTransactionHash(
        wallet.address,
        selectedRecipient,
        parseFloat(amount),
        timestamp
      )
      
      const fee = calculateFee(parseFloat(amount), protectionLevel)
      const security = estimateQuantumSecurity(protectionLevel)
      
      // Sign transaction with quantum-resistant signature
      const response = await fetch('/api/crypto/sign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: txHash,
          privateKey: wallet.privateKey
        })
      })
      
      const { signature } = await response.json()
      
      const newTransaction: ProtectedTransaction = {
        id: `tx_${Date.now()}`,
        txHash,
        sender: wallet.address,
        recipient: selectedRecipient,
        amount: parseFloat(amount),
        fee,
        quantumSignature: signature,
        timestamp,
        status: 'pending',
        confirmations: 0,
        protectionLevel,
        estimatedQuantumSecurity: security,
        dilithiumStrength: 'N/A' // Assuming no dilithium strength for now
      }
      
      setWallet(prev => prev ? {
        ...prev,
        balance: prev.balance - parseFloat(amount) - fee,
        protectedTransactions: [newTransaction, ...prev.protectedTransactions]
      } : null)
      
    } catch (error) {
      console.error('Error protecting transaction:', error)
    }
    setLoading(false)
  }

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-3xl font-bold neon-text mb-4">
          Quantum-Protected Bitcoin Transactions
        </h1>
        <p className="text-secondary mb-8">
          Secure your Bitcoin transactions against quantum computer attacks using
          post-quantum cryptography. Our hybrid protection system ensures your
          transactions remain secure even if quantum computers break ECDSA.
        </p>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="cyber-card p-6 rounded-lg col-span-2">
          <h2 className="text-xl font-semibold neon-text mb-4">Wallet Control Center</h2>
          
          {!wallet ? (
            <button
              onClick={createWallet}
              disabled={loading}
              className="cyber-button px-4 py-2 rounded disabled:opacity-50"
            >
              Create Quantum-Protected Wallet
            </button>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary">Your Address</label>
                <pre className="mt-1 p-2 rounded text-sm break-all">
                  {wallet.address}
                </pre>
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary">Balance</label>
                <div className="text-2xl font-bold neon-text">
                  {wallet.balance.toFixed(8)} BTC
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="cyber-card p-6 rounded-lg">
          <h2 className="text-xl font-semibold neon-text mb-4">Network Stats</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-secondary">Protected Transactions</label>
              <div className="text-xl neon-text">{networkStats.protectedTransactions}</div>
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary">Network Health</label>
              <div className="text-xl neon-text">{networkStats.networkHealth.toFixed(2)}%</div>
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary">Recent Blocks</label>
              <div className="text-xl neon-text">{networkStats.recentBlocks}</div>
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary">Dilithium Usage</label>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span>Standard:</span>
                  <span className="neon-text">{networkStats.dilithiumUsage.standard}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Enhanced:</span>
                  <span className="neon-text">{networkStats.dilithiumUsage.enhanced}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Maximum:</span>
                  <span className="neon-text">{networkStats.dilithiumUsage.maximum}</span>
                </div>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary">Total Security</label>
              <div className="text-xl neon-text">{networkStats.totalQuantumSecurity.toFixed(1)} years</div>
            </div>
          </div>
        </div>
      </section>

      <section className="cyber-card p-6 rounded-lg">
        <h2 className="text-xl font-semibold neon-text mb-4">Create Protected Transaction</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-secondary">Recipient</label>
              <div className="flex gap-2">
                <select
                  value={selectedRecipient}
                  onChange={(e) => setSelectedRecipient(e.target.value)}
                  className="mt-1 block w-full rounded-md border-accent-neon bg-background-darker text-text-primary"
                >
                  <option value="">Select recipient</option>
                  {testWallets.map(wallet => (
                    <option key={wallet.address} value={wallet.address}>
                      {wallet.address.slice(0, 10)}... ({wallet.balance.toFixed(2)} BTC)
                    </option>
                  ))}
                </select>
                <button
                  onClick={createTestWallet}
                  disabled={loading}
                  className="cyber-button px-4 py-2 rounded disabled:opacity-50"
                >
                  Create Test Wallet
                </button>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary">Amount (BTC)</label>
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                step="0.00000001"
                min="0"
                max={wallet?.balance || 0}
                className="mt-1 block w-full rounded-md border-accent-neon bg-background-darker text-text-primary"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary">Protection Level</label>
              <select
                value={protectionLevel}
                onChange={(e) => setProtectionLevel(e.target.value as ProtectionLevel)}
                className="mt-1 block w-full rounded-md border-accent-neon bg-background-darker text-text-primary"
              >
                <option value="standard">Standard (10 years quantum security)</option>
                <option value="enhanced">Enhanced (20 years quantum security)</option>
                <option value="maximum">Maximum (30 years quantum security)</option>
              </select>
            </div>
            
            <button
              onClick={protectTransaction}
              disabled={loading || !wallet || !selectedRecipient || !amount}
              className="cyber-button px-4 py-2 rounded disabled:opacity-50 w-full"
            >
              Protect & Send Transaction
            </button>
          </div>
          
          <div className="space-y-4">
            <TooltipCard tooltip={tooltips.security} />
            <div className="p-4 rounded bg-accent-neon bg-opacity-10 border border-accent-neon">
              <h3 className="text-lg font-semibold neon-text mb-2">Transaction Summary</h3>
              {amount && (
                <>
                  <div className="flex justify-between text-secondary">
                    <span>Amount:</span>
                    <span>{parseFloat(amount).toFixed(8)} BTC</span>
                  </div>
                  <div className="flex justify-between text-secondary">
                    <span>Protection Fee:</span>
                    <span>{calculateFee(parseFloat(amount), protectionLevel).toFixed(8)} BTC</span>
                  </div>
                  <div className="flex justify-between text-secondary">
                    <span>Quantum Security:</span>
                    <span>{estimateQuantumSecurity(protectionLevel)} years</span>
                  </div>
                  <div className="flex justify-between font-bold neon-text mt-2">
                    <span>Total:</span>
                    <span>
                      {(parseFloat(amount) + calculateFee(parseFloat(amount), protectionLevel)).toFixed(8)} BTC
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="cyber-card p-6 rounded-lg">
        <h2 className="text-xl font-semibold neon-text mb-4">Learn About Quantum Protection</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="p-4 rounded bg-accent-neon bg-opacity-10 border border-accent-neon">
              <h3 className="text-lg font-semibold neon-text mb-2">How It Works</h3>
              <p className="text-secondary mb-4">
                When you create a quantum-protected transaction, we:
              </p>
              <ol className="list-decimal list-inside space-y-2 text-secondary">
                <li>Generate a hybrid wallet with both Bitcoin and Dilithium keys</li>
                <li>Create your Bitcoin transaction normally</li>
                <li>Add an extra Dilithium signature for quantum protection</li>
                <li>Store both signatures in the blockchain</li>
              </ol>
            </div>
            
            <div className="p-4 rounded bg-accent-neon bg-opacity-10 border border-accent-neon">
              <h3 className="text-lg font-semibold neon-text mb-2">Protection Levels</h3>
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium text-secondary">Standard (10 years)</h4>
                  <p className="text-sm text-secondary">Uses Dilithium2 parameters - Good for most transactions</p>
                </div>
                <div>
                  <h4 className="font-medium text-secondary">Enhanced (20 years)</h4>
                  <p className="text-sm text-secondary">Uses Dilithium3 parameters - Better for large amounts</p>
                </div>
                <div>
                  <h4 className="font-medium text-secondary">Maximum (30 years)</h4>
                  <p className="text-sm text-secondary">Uses Dilithium5 parameters - Best for critical transactions</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 rounded bg-accent-neon bg-opacity-10 border border-accent-neon">
              <h3 className="text-lg font-semibold neon-text mb-2">Example Code</h3>
              <pre className="text-sm text-secondary overflow-x-auto p-2 bg-background-darker rounded">
                <code>{`# Create a quantum-protected wallet
wallet = QuantumProtectedWallet()

# Protect a Bitcoin transaction
tx_hash = "4a5e1e4b..."
protected_tx = wallet.protect_transaction(tx_hash)

# Verify the protection
is_valid = wallet.verify_protected_transaction(
    protected_tx
)`}</code>
              </pre>
              <p className="text-sm text-secondary mt-2">
                This is a simplified version of how our quantum protection works behind the scenes.
              </p>
            </div>
            
            <div className="p-4 rounded bg-accent-neon bg-opacity-10 border border-accent-neon">
              <h3 className="text-lg font-semibold neon-text mb-2">Why Quantum Protection?</h3>
              <div className="space-y-2 text-secondary">
                <p>🔓 Quantum computers could break Bitcoin&apos;s current security</p>
                <p>🔒 Dilithium signatures remain secure against quantum attacks</p>
                <p>⚡ Our hybrid approach protects your funds for the future</p>
                <p>💪 Higher protection levels use stronger quantum parameters</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {wallet && wallet.protectedTransactions.length > 0 && (
        <section className="cyber-card p-6 rounded-lg">
          <h2 className="text-xl font-semibold neon-text mb-4">Protected Transactions</h2>
          <div className="space-y-4">
            {wallet.protectedTransactions.map(tx => (
              <div key={tx.id} className="p-4 rounded bg-background-darker border border-accent-neon">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-secondary">Amount</label>
                    <div className="font-mono neon-text">{tx.amount.toFixed(8)} BTC</div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary">Protection</label>
                    <div className="font-mono neon-text capitalize">{tx.protectionLevel}</div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary">Security</label>
                    <div className="font-mono neon-text">{tx.estimatedQuantumSecurity} years</div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary">Status</label>
                    <div className="font-mono neon-text capitalize">{tx.status}</div>
                  </div>
                </div>
                <div className="mt-2">
                  <label className="block text-sm font-medium text-secondary">Transaction Hash</label>
                  <div className="font-mono text-sm text-secondary break-all">{tx.txHash}</div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
} 