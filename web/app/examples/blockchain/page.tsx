'use client'

import { useState, useEffect } from 'react'

interface Transaction {
  id: string
  sender: string
  recipient: string
  amount: number
  signature: string
  timestamp: string
}

interface Block {
  id: string
  transactions: Transaction[]
  previousHash: string
  hash: string
  nonce: number
  timestamp: string
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
          privateKey: wallet.privateKey
        })
      })
      const data = await response.json()
      
      const transaction: Transaction = {
        id: `tx_${Date.now()}`,
        sender: wallet.address,
        recipient,
        amount: parseFloat(amount),
        signature: data.signature,
        timestamp: new Date().toISOString()
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
    try {
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
    } catch (error) {
      console.error('Error mining block:', error)
    }
    setLoading(false)
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
          <h2 className="text-xl font-semibold neon-text mb-4">Step 2: Create Transaction</h2>
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
              Sign & Submit Transaction
            </button>
          </div>
        </div>

        <div className={`cyber-card p-6 rounded-lg ${activeSection === 'mining' ? 'ring-2 ring-accent-cyber' : ''}`}>
          <TooltipCard tooltip={tooltips.mining} />
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold neon-text">Step 3: Mine Blocks</h2>
            <button
              onClick={mineBlock}
              disabled={loading || transactions.length === 0}
              className="cyber-button px-4 py-2 rounded disabled:opacity-50"
            >
              Mine Block
            </button>
          </div>
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-secondary">Pending Transactions</h3>
            {transactions.map(tx => (
              <div key={tx.id} className="p-4 border border-accent-neon rounded-lg">
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-secondary">From: </span>
                    <span className="text-text-primary">{tx.sender}</span>
                  </div>
                  <div>
                    <span className="text-secondary">To: </span>
                    <span className="text-text-primary">{tx.recipient}</span>
                  </div>
                  <div>
                    <span className="text-secondary">Amount: </span>
                    <span className="neon-text">{tx.amount}</span>
                  </div>
                  <div>
                    <span className="text-secondary">Time: </span>
                    <span className="text-text-primary">
                      {new Date(tx.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
            {transactions.length === 0 && (
              <p className="text-secondary text-center">No pending transactions</p>
            )}
          </div>
        </div>

        <div className="cyber-card p-6 rounded-lg">
          <h2 className="text-xl font-semibold neon-text mb-4">Blockchain Explorer</h2>
          <div className="space-y-4">
            {blocks.map(block => (
              <div key={block.id} className="p-4 border border-accent-neon rounded-lg">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-secondary">Block {block.id.split('_')[1]}</span>
                    <span className="text-text-primary">
                      {new Date(block.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-secondary">Hash: </span>
                    <span className="text-text-primary">{block.hash}</span>
                  </div>
                  <div>
                    <span className="text-secondary">Previous Hash: </span>
                    <span className="text-text-primary">{block.previousHash}</span>
                  </div>
                  <div>
                    <span className="text-secondary">Transactions: </span>
                    <span className="neon-text">{block.transactions.length}</span>
                  </div>
                </div>
              </div>
            ))}
            {blocks.length === 0 && (
              <p className="text-secondary text-center">No blocks mined yet</p>
            )}
          </div>
        </div>

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