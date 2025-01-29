declare module '*.css' {
  const styles: { [className: string]: string }
  export default styles
}

declare module 'tailwindcss/tailwind.css'
declare module 'tailwindcss/base'
declare module 'tailwindcss/components'
declare module 'tailwindcss/utilities'
