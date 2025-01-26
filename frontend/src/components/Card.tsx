import * as React from 'react'
import { styles } from '../utils/styles'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  ...props
}) => {
  return (
    <div
      className={`${styles.card} ${className}`.trim()}
      {...props}
    >
      {children}
    </div>
  )
} 