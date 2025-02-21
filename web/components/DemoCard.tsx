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
      className="block p-6 bg-white rounded-lg border border-gray-200 shadow-md hover:bg-gray-50 transition-colors"
    >
      <div className="flex items-center gap-4">
        {icon && (
          <div className="w-12 h-12 flex items-center justify-center rounded-full bg-blue-100">
            <span className="text-2xl">{icon}</span>
          </div>
        )}
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>
          <p className="text-gray-600">{description}</p>
        </div>
      </div>
    </Link>
  )
} 