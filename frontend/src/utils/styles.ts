export const styles = {
  button: {
    primary: 'px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors',
    secondary: 'px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors',
  },
  card: 'bg-white rounded-lg shadow-md p-6',
  container: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8',
  input: 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
  select: 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm',
  checkbox: 'h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500',
  heading: {
    h1: 'text-3xl font-bold text-gray-900 sm:text-4xl',
    h2: 'text-2xl font-bold text-gray-900',
    h3: 'text-lg font-medium text-gray-900',
  },
} as const

// Type pour les clés du premier niveau
type StyleKey = keyof typeof styles

// Type pour les clés du second niveau (pour les objets imbriqués)
type NestedStyleKey<K extends StyleKey> = keyof (typeof styles)[K]

// Fonction helper pour accéder aux styles
export function getStyle<K extends StyleKey>(key: K): (typeof styles)[K]
export function getStyle<K extends StyleKey, NK extends NestedStyleKey<K>>(
  key: K,
  nestedKey: NK
): (typeof styles)[K][NK]
export function getStyle<K extends StyleKey, NK extends NestedStyleKey<K>>(
  key: K,
  nestedKey?: NK
) {
  if (nestedKey === undefined) {
    return styles[key]
  }
  return styles[key][nestedKey]
} 