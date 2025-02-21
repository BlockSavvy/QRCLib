import { NextResponse } from 'next/server'

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

interface BlockchainData {
  blocks: Block[]
  pendingTransactions: Transaction[]
}

// Mock blockchain data store
const blockchain: BlockchainData = {
  blocks: [],
  pendingTransactions: []
}

export async function GET() {
  try {
    return NextResponse.json(blockchain)
  } catch (error) {
    console.error('Error fetching blockchain:', error)
    return NextResponse.json(
      { error: 'Failed to fetch blockchain data' },
      { status: 500 }
    )
  }
}

export async function POST(request: Request) {
  try {
    const { action, data } = await request.json()

    switch (action) {
      case 'addTransaction': {
        const { transaction } = data as { transaction: Transaction }
        if (!transaction) {
          return NextResponse.json(
            { error: 'Missing transaction data' },
            { status: 400 }
          )
        }
        blockchain.pendingTransactions.push(transaction)
        return NextResponse.json({ success: true })
      }

      case 'mineBlock': {
        if (blockchain.pendingTransactions.length === 0) {
          return NextResponse.json(
            { error: 'No pending transactions to mine' },
            { status: 400 }
          )
        }

        const previousBlock = blockchain.blocks[blockchain.blocks.length - 1]
        const previousHash = previousBlock ? previousBlock.hash : '0'.repeat(64)

        const newBlock: Block = {
          id: `block_${blockchain.blocks.length + 1}`,
          transactions: [...blockchain.pendingTransactions],
          previousHash,
          hash: `hash_${Date.now()}`, // Mock hash
          nonce: Math.floor(Math.random() * 1000000),
          timestamp: new Date().toISOString()
        }

        blockchain.blocks.push(newBlock)
        blockchain.pendingTransactions = []

        return NextResponse.json({ success: true, block: newBlock })
      }

      default:
        return NextResponse.json(
          { error: 'Invalid action' },
          { status: 400 }
        )
    }
  } catch (error) {
    console.error('Error processing blockchain request:', error)
    return NextResponse.json(
      { error: 'Failed to process blockchain request' },
      { status: 500 }
    )
  }
} 