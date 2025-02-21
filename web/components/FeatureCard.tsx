interface FeatureCardProps {
  title: string
  description: string
  icon: string
}

export function FeatureCard({ title, description, icon }: FeatureCardProps) {
  return (
    <div className="flex items-start space-x-3 p-3 rounded bg-accent-neon bg-opacity-10 border border-accent-neon">
      <div className="text-2xl">{icon}</div>
      <div>
        <h3 className="font-semibold neon-text">{title}</h3>
        <p className="text-sm text-secondary">{description}</p>
      </div>
    </div>
  )
} 