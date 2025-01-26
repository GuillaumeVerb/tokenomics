import * as React from 'react'
import { styles } from '../utils/styles'

type ButtonVariant = keyof typeof styles.button

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  children: React.ReactNode
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  children,
  className = '',
  ...props
}) => {
  return (
    <button
      className={`${styles.button[variant]} ${className}`.trim()}
      {...props}
    >
      {children}
    </button>
  )
} 