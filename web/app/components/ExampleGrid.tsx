import { FC, ReactNode } from 'react'

interface ExampleGridProps {
  children: ReactNode
}

export const ExampleGrid: FC<ExampleGridProps> = ({ children }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {children}
    </div>
  )
} 