import Link from 'next/link'
import { FC } from 'react'

interface DemoCardProps {
  title: string
  description: string
  link: string
  icon?: string
}

export const DemoCard: FC<DemoCardProps> = ({ title, description, link, icon }) => {
  return (
    <Link 
      href={link}
      className="cyber-card block p-6 rounded-lg transition-all duration-300"
    >
      <div className="flex items-center gap-4">
        {icon && (
          <div className="w-12 h-12 flex items-center justify-center rounded-full bg-accent-cyber bg-opacity-20 border border-accent-cyber">
            <span className="text-2xl neon-text">{icon}</span>
          </div>
        )}
        <div>
          <h3 className="text-xl font-bold neon-text mb-2">{title}</h3>
          <p className="text-secondary">{description}</p>
        </div>
      </div>
    </Link>
  )
} 