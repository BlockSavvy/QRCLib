'use client'

import { useState, useEffect } from 'react'

interface Transaction {
  id: string
  sender: string
  recipient: string
  amount: number
  signature: string
  timestamp: string
  status: 'pending' | 'confirmed' | 'failed'
  confirmations: number
  quantumProtectionLevel: 'standard' | 'enhanced' | 'maximum'
}

interface Block {
  id: string
  transactions: Transaction[]
  previousHash: string
  hash: string
  nonce: number
  timestamp: string
  difficulty: number
  miningTime: number
  size: number
}

interface NetworkStats {
  totalTransactions: number
  totalBlocks: number
  averageBlockTime: number
  currentDifficulty: number
  hashRate: number
  protectedTransactions: number
}

interface Tooltip {
  title: string
  content: string
}

const tooltips: Record<string, Tooltip> = {
  wallet: {
    title: "What's a Wallet?",
    content: "A wallet is your digital identity on the blockchain. It contains your quantum-resistant keys for signing transactions and proving ownership of funds."
  },
  transaction: {
    title: "Creating Transactions",
    content: "Transactions represent the transfer of value between wallets. Each transaction is signed with quantum-resistant signatures to ensure authenticity."
  },
  mining: {
    title: "Mining Blocks",
    content: "Mining is the process of adding new blocks to the blockchain. Each block contains multiple transactions and is linked to the previous block, forming a chain."
  },
  quantumProtection: {
    title: "Quantum Protection",
    content: "Each transaction is protected against quantum computer attacks using Dilithium signatures. Choose from three protection levels based on your security needs."
  }
}

function TooltipCard({ tooltip }: { tooltip: Tooltip }) {
  return (
    <div className="mb-4 p-4 bg-background-darker border border-accent-cyber rounded-lg">
      <h3 className="text-lg font-semibold text-accent-cyber mb-2">{tooltip.title}</h3>
      <p className="text-secondary">{tooltip.content}</p>
    </div>
  )
}

function BlockVisualizer({ block }: { block: Block }) {
  return (
    <div className="p-4 border border-accent-neon rounded-lg space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-accent-neon">Block #{block.id}</span>
        <span className="text-xs text-secondary">
          {new Date(block.timestamp).toLocaleString()}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div>
          <span className="text-secondary">Hash: </span>
          <span className="text-text-primary font-mono">{block.hash.slice(0, 10)}...</span>
        </div>
        <div>
          <span className="text-secondary">Previous: </span>
          <span className="text-text-primary font-mono">{block.previousHash.slice(0, 10)}...</span>
        </div>
        <div>
          <span className="text-secondary">Nonce: </span>
          <span className="text-text-primary">{block.nonce}</span>
        </div>
        <div>
          <span className="text-secondary">Difficulty: </span>
          <span className="text-text-primary">{block.difficulty}</span>
        </div>
        <div>
          <span className="text-secondary">Mining Time: </span>
          <span className="text-text-primary">{block.miningTime}ms</span>
        </div>
        <div>
          <span className="text-secondary">Size: </span>
          <span className="text-text-primary">{block.size} bytes</span>
        </div>
      </div>
      <div className="mt-4">
        <span className="text-sm text-secondary">Transactions ({block.transactions.length}):</span>
        <div className="mt-2 space-y-2">
          {block.transactions.map(tx => (
            <div key={tx.id} className="text-xs p-2 bg-background-darker rounded">
              {tx.sender.slice(0, 10)}... → {tx.recipient.slice(0, 10)}...
              <span className="float-right">{tx.amount} coins</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function NetworkStatsDisplay({ stats }: { stats: NetworkStats }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      <div className="p-4 bg-accent-neon bg-opacity-10 rounded-lg">
        <div className="text-2xl font-bold neon-text">{stats.totalBlocks}</div>
        <div className="text-sm text-secondary">Total Blocks</div>
      </div>
      <div className="p-4 bg-accent-neon bg-opacity-10 rounded-lg">
        <div className="text-2xl font-bold neon-text">{stats.totalTransactions}</div>
        <div className="text-sm text-secondary">Total Transactions</div>
      </div>
      <div className="p-4 bg-accent-neon bg-opacity-10 rounded-lg">
        <div className="text-2xl font-bold neon-text">{stats.protectedTransactions}</div>
        <div className="text-sm text-secondary">Protected Transactions</div>
      </div>
      <div className="p-4 bg-accent-neon bg-opacity-10 rounded-lg">
        <div className="text-2xl font-bold neon-text">{stats.averageBlockTime.toFixed(2)}s</div>
        <div className="text-sm text-secondary">Average Block Time</div>
      </div>
      <div className="p-4 bg-accent-neon bg-opacity-10 rounded-lg">
        <div className="text-2xl font-bold neon-text">{stats.currentDifficulty}</div>
        <div className="text-sm text-secondary">Current Difficulty</div>
      </div>
      <div className="p-4 bg-accent-neon bg-opacity-10 rounded-lg">
        <div className="text-2xl font-bold neon-text">{stats.hashRate.toFixed(2)} H/s</div>
        <div className="text-sm text-secondary">Hash Rate</div>
      </div>
    </div>
  )
}

export default function BlockchainPage() {
  const [loading, setLoading] = useState(false)
  const [wallet, setWallet] = useState<{
    address: string
    publicKey: string
    privateKey: string
  } | null>(null)
  const [testWallets, setTestWallets] = useState<Array<{
    address: string
    publicKey: string
    label: string
  }>>([])
  const [recipient, setRecipient] = useState('')
  const [amount, setAmount] = useState('')
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [blocks, setBlocks] = useState<Block[]>([])
  const [activeSection, setActiveSection] = useState<'wallet' | 'transaction' | 'mining'>('wallet')
  const [networkStats, setNetworkStats] = useState<NetworkStats>({
    totalTransactions: 0,
    totalBlocks: 0,
    averageBlockTime: 0,
    currentDifficulty: 1,
    hashRate: 0,
    protectedTransactions: 0
  })
  const [protectionLevel, setProtectionLevel] = useState<'standard' | 'enhanced' | 'maximum'>('standard')
  const [miningStatus, setMiningStatus] = useState<{
    mining: boolean
    progress: number
    hashesComputed: number
  }>({
    mining: false,
    progress: 0,
    hashesComputed: 0
  })

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

  const createTestWallet = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/crypto/generate-keys')
      const data = await response.json()
      const newWallet = {
        address: `0x${data.publicKey.slice(0, 40)}`,
        publicKey: data.publicKey,
        label: `Test Wallet ${testWallets.length + 1}`
      }
      setTestWallets([...testWallets, newWallet])
      // If no recipient is selected and we have test wallets, select the first one
      if (!recipient && testWallets.length === 0) {
        setRecipient(newWallet.address)
      }
    } catch (error) {
      console.error('Error creating test wallet:', error)
    }
    setLoading(false)
  }

  const createTransaction = async () => {
    if (!wallet || !recipient || !amount) return
    setLoading(true)
    try {
      const response = await fetch('/api/crypto/sign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: `${recipient}:${amount}`,
          privateKey: wallet.privateKey,
          protectionLevel
        })
      })
      const data = await response.json()
      
      const transaction: Transaction = {
        id: `tx_${Date.now()}`,
        sender: wallet.address,
        recipient,
        amount: parseFloat(amount),
        signature: data.signature,
        timestamp: new Date().toISOString(),
        status: 'pending',
        confirmations: 0,
        quantumProtectionLevel: protectionLevel
      }
      
      // Add transaction to blockchain
      const blockchainResponse = await fetch('/api/crypto/blockchain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'addTransaction',
          data: { transaction }
        })
      })
      
      if (!blockchainResponse.ok) {
        throw new Error('Failed to add transaction to blockchain')
      }
      
      setTransactions([...transactions, transaction])
      setRecipient('')
      setAmount('')
    } catch (error) {
      console.error('Error creating transaction:', error)
    }
    setLoading(false)
  }

  const mineBlock = async () => {
    if (transactions.length === 0) return
    setLoading(true)
    setMiningStatus({ mining: true, progress: 0, hashesComputed: 0 })
    
    try {
      // Simulate mining progress
      const totalSteps = 20
      for (let i = 0; i < totalSteps; i++) {
        await new Promise(resolve => setTimeout(resolve, 200))
        setMiningStatus(prev => ({
          ...prev,
          progress: ((i + 1) / totalSteps) * 100,
          hashesComputed: prev.hashesComputed + Math.floor(Math.random() * 1000)
        }))
      }
      
      const response = await fetch('/api/crypto/blockchain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'mineBlock'
        })
      })
      
      if (!response.ok) {
        throw new Error('Failed to mine block')
      }
      
      const { block } = await response.json()
      setBlocks([...blocks, block])
      setTransactions([])
      
      // Update network stats
      setNetworkStats(prev => ({
        ...prev,
        totalBlocks: prev.totalBlocks + 1,
        totalTransactions: prev.totalTransactions + block.transactions.length,
        protectedTransactions: prev.protectedTransactions + block.transactions.length,
        averageBlockTime: (prev.averageBlockTime * prev.totalBlocks + block.miningTime) / (prev.totalBlocks + 1),
        currentDifficulty: block.difficulty,
        hashRate: miningStatus.hashesComputed / (block.miningTime / 1000)
      }))
    } catch (error) {
      console.error('Error mining block:', error)
    }
    
    setLoading(false)
    setMiningStatus({ mining: false, progress: 0, hashesComputed: 0 })
  }

  // Fetch initial blockchain state
  useEffect(() => {
    const fetchBlockchain = async () => {
      try {
        const response = await fetch('/api/crypto/blockchain')
        if (response.ok) {
          const data = await response.json()
          setBlocks(data.blocks)
          setTransactions(data.pendingTransactions)
        }
      } catch (error) {
        console.error('Error fetching blockchain:', error)
      }
    }
    fetchBlockchain()
  }, [])

  useEffect(() => {
    // Automatically highlight the next recommended action
    if (!wallet) {
      setActiveSection('wallet')
    } else if (transactions.length === 0) {
      setActiveSection('transaction')
    } else {
      setActiveSection('mining')
    }
  }, [wallet, transactions])

  return (
    <div className="space-y-12">
      <section>
        <h1 className="text-3xl font-bold neon-text mb-4">
          Quantum-Resistant Blockchain
        </h1>
        <p className="text-secondary mb-8">
          Experience a blockchain implementation secured with quantum-resistant cryptography.
          Follow the steps below to create wallets, send transactions, and mine blocks.
        </p>
        
        <NetworkStatsDisplay stats={networkStats} />
      </section>

      <section className="space-y-6">
        <div className={`cyber-card p-6 rounded-lg ${activeSection === 'wallet' ? 'ring-2 ring-accent-cyber' : ''}`}>
          <TooltipCard tooltip={tooltips.wallet} />
          <h2 className="text-xl font-semibold neon-text mb-4">Step 1: Create Your Wallet</h2>
          {!wallet ? (
            <button
              onClick={createWallet}
              disabled={loading}
              className="cyber-button px-4 py-2 rounded disabled:opacity-50"
            >
              Create Wallet
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

        <div className={`cyber-card p-6 rounded-lg ${activeSection === 'transaction' ? 'ring-2 ring-accent-cyber' : ''}`}>
          <TooltipCard tooltip={tooltips.transaction} />
          <TooltipCard tooltip={tooltips.quantumProtection} />
          <h2 className="text-xl font-semibold neon-text mb-4">Step 2: Create Transaction</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-secondary">Protection Level</label>
              <select
                value={protectionLevel}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setProtectionLevel(e.target.value as 'standard' | 'enhanced' | 'maximum')}
                className="mt-1 block w-full rounded-md border-accent-neon bg-background-darker text-text-primary"
              >
                <option value="standard">Standard (128-bit security)</option>
                <option value="enhanced">Enhanced (192-bit security)</option>
                <option value="maximum">Maximum (256-bit security)</option>
              </select>
            </div>
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
              <label className="block text-sm font-medium text-secondary">Amount</label>
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="mt-1 block w-full rounded-md border-accent-neon bg-background-darker text-text-primary shadow-sm focus:border-accent-cyber focus:ring-accent-cyber"
                placeholder="Enter amount"
              />
            </div>
            <button
              onClick={createTransaction}
              disabled={loading || !wallet || !recipient || !amount}
              className="cyber-button px-4 py-2 rounded disabled:opacity-50"
            >
              Create Protected Transaction
            </button>
          </div>
        </div>

        <div className={`cyber-card p-6 rounded-lg ${activeSection === 'mining' ? 'ring-2 ring-accent-cyber' : ''}`}>
          <TooltipCard tooltip={tooltips.mining} />
          <h2 className="text-xl font-semibold neon-text mb-4">Step 3: Mine Block</h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-medium text-secondary mb-2">Pending Transactions</h3>
              <div className="space-y-2">
                {transactions.map(tx => (
                  <div key={tx.id} className="p-2 border border-accent-neon rounded">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">
                        {tx.sender.slice(0, 10)}... → {tx.recipient.slice(0, 10)}...
                      </span>
                      <span className="text-sm">{tx.amount} coins</span>
                    </div>
                    <div className="mt-1 flex justify-between items-center text-xs text-secondary">
                      <span>Protection: {tx.quantumProtectionLevel}</span>
                      <span>Status: {tx.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {miningStatus.mining && (
              <div className="space-y-2">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-secondary">Mining Progress</span>
                  <span className="text-accent-neon">{miningStatus.progress.toFixed(1)}%</span>
                </div>
                <div className="h-2 bg-background-darker rounded-full overflow-hidden">
                  <div
                    className="h-full bg-accent-neon transition-all duration-200"
                    style={{ width: `${miningStatus.progress}%` }}
                  />
                </div>
                <div className="text-xs text-secondary">
                  Hashes computed: {miningStatus.hashesComputed.toLocaleString()}
                </div>
              </div>
            )}
            
            <button
              onClick={mineBlock}
              disabled={loading || transactions.length === 0}
              className="cyber-button px-4 py-2 rounded disabled:opacity-50"
            >
              Mine New Block
            </button>
          </div>
        </div>

        <section>
          <h2 className="text-2xl font-bold neon-text mb-4">Blockchain Explorer</h2>
          <div className="space-y-4">
            {blocks.map(block => (
              <BlockVisualizer key={block.id} block={block} />
            ))}
            {blocks.length === 0 && (
              <p className="text-center text-secondary">No blocks mined yet</p>
            )}
          </div>
        </section>

        <div className="cyber-card p-6 rounded-lg">
          <h2 className="text-xl font-semibold neon-text mb-4">Test Wallets</h2>
          <div className="space-y-4">
            <button
              onClick={createTestWallet}
              disabled={loading}
              className="cyber-button px-4 py-2 rounded disabled:opacity-50"
            >
              Create Test Wallet
            </button>
            
            <div className="space-y-2">
              {testWallets.map((testWallet) => (
                <div key={testWallet.address} className="p-4 border border-accent-neon rounded-lg">
                  <div className="flex justify-between items-center">
                    <span className="text-accent-neon">{testWallet.label}</span>
                    <button
                      onClick={() => setRecipient(testWallet.address)}
                      className="cyber-button px-2 py-1 text-sm rounded"
                    >
                      Select as Recipient
                    </button>
                  </div>
                  <div className="mt-2">
                    <span className="text-secondary">Address: </span>
                    <span className="text-text-primary">{testWallet.address}</span>
                  </div>
                </div>
              ))}
              {testWallets.length === 0 && (
                <p className="text-secondary text-center">No test wallets created yet</p>
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
} 