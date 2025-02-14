import postcssPresetEnv from 'postcss-preset-env'
import tailwindcss from 'tailwindcss'
import autoprefixer from 'autoprefixer'
import postcssImport from 'postcss-import'
import cssnano from 'cssnano'

export default {
  plugins: [
    postcssImport,
    tailwindcss,
    postcssPresetEnv({
      stage: 1,
      features: {
        'nesting-rules': true,
        'custom-properties': true,
        'custom-media-queries': true,
      }
    }),
    autoprefixer,
    ...(process.env.NODE_ENV === 'production' ? [cssnano] : [])
  ]
}
