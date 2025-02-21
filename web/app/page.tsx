import { DemoCard } from '@/components/DemoCard'
import { ExampleGrid } from '@/components/ExampleGrid'
import { FeatureCard } from '@/components/FeatureCard'

export default function Home() {
  return (
    <div className="space-y-12">
      <section className="text-center">
        <h1 className="text-4xl font-bold neon-text mb-4">
          Quantum-Resistant Cryptography Library
        </h1>
        <p className="text-xl text-secondary max-w-3xl mx-auto">
          A Python library implementing post-quantum cryptographic algorithms, 
          including Kyber (Key Encapsulation) and Dilithium (Digital Signatures).
          Protect your applications against quantum computer threats.
        </p>
      </section>

      <section>
        <h2 className="text-2xl font-bold neon-text mb-6">
          Live Examples
        </h2>
        <ExampleGrid>
          <DemoCard
            title="Basic Operations"
            description="Explore key generation, signing, and encryption using quantum-resistant algorithms."
            link="/examples/basic"
            icon="🔑"
          />
          <DemoCard
            title="Secure Messaging"
            description="End-to-end encrypted chat using Kyber for key exchange and Dilithium for signatures."
            link="/examples/messaging"
            icon="💬"
          />
          <DemoCard
            title="Blockchain Demo"
            description="Quantum-resistant blockchain implementation with secure transactions."
            link="/examples/blockchain"
            icon="⛓️"
          />
          <DemoCard
            title="Bitcoin Protection"
            description="Protect Bitcoin wallets and transactions against quantum threats."
            link="/examples/bitcoin"
            icon="₿"
          />
          <DemoCard
            title="File Storage"
            description="Secure file storage and sharing with quantum-resistant encryption."
            link="/examples/storage"
            icon="📁"
          />
          <DemoCard
            title="API Security"
            description="Quantum-safe API authentication and data protection."
            link="/examples/api"
            icon="🔐"
          />
        </ExampleGrid>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="cyber-card p-6 rounded-lg">
          <h2 className="text-2xl font-bold neon-text mb-4">
            Key Features
          </h2>
          <div className="space-y-4">
            <FeatureCard
              title="Kyber Key Encapsulation"
              description="NIST-approved post-quantum key exchange mechanism"
              icon="🔄"
            />
            <FeatureCard
              title="Dilithium Signatures"
              description="Quantum-resistant digital signatures for document authenticity"
              icon="✍️"
            />
            <FeatureCard
              title="Hybrid Protection"
              description="Combine classical and quantum-resistant algorithms"
              icon="🛡️"
            />
            <FeatureCard
              title="Easy Integration"
              description="Simple API for adding quantum resistance to any application"
              icon="🔌"
            />
          </div>
        </div>

        <div className="cyber-card p-6 rounded-lg">
          <h2 className="text-2xl font-bold neon-text mb-4">
            Real-World Applications
          </h2>
          <div className="space-y-4">
            <FeatureCard
              title="Cryptocurrency"
              description="Protect wallets and transactions against quantum attacks"
              icon="💰"
            />
            <FeatureCard
              title="Secure Communication"
              description="End-to-end encrypted messaging and file sharing"
              icon="📱"
            />
            <FeatureCard
              title="Document Signing"
              description="Long-term valid digital signatures for legal documents"
              icon="📄"
            />
            <FeatureCard
              title="Data Protection"
              description="Future-proof encryption for sensitive information"
              icon="🔒"
            />
          </div>
        </div>
      </section>

      <section className="cyber-card -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-2xl font-bold neon-text mb-4">
            Why Quantum-Resistant Cryptography?
          </h2>
          <p className="text-secondary mb-6">
            Quantum computers pose a significant threat to current cryptographic systems.
            Our library implements NIST-approved post-quantum algorithms to protect
            against both classical and quantum computer attacks.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="p-4 rounded bg-accent-neon bg-opacity-10">
              <h3 className="font-bold neon-text mb-2">Shor&apos;s Algorithm</h3>
              <p className="text-sm text-secondary">Can break RSA and ECC in polynomial time on quantum computers</p>
            </div>
            <div className="p-4 rounded bg-accent-neon bg-opacity-10">
              <h3 className="font-bold neon-text mb-2">Grover&apos;s Algorithm</h3>
              <p className="text-sm text-secondary">Reduces symmetric crypto security by half on quantum computers</p>
            </div>
            <div className="p-4 rounded bg-accent-neon bg-opacity-10">
              <h3 className="font-bold neon-text mb-2">Our Solution</h3>
              <p className="text-sm text-secondary">Post-quantum algorithms resistant to both classical and quantum attacks</p>
            </div>
          </div>
          <a
            href="https://github.com/BlockSavvy/QRCLib"
            target="_blank"
            rel="noopener noreferrer"
            className="cyber-button inline-flex items-center justify-center px-5 py-3 text-base font-medium rounded-md"
          >
            View on GitHub
          </a>
        </div>
      </section>
    </div>
  )
}
