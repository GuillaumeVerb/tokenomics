#!/bin/bash

# Install dependencies
npm install -D tailwindcss@latest postcss@latest autoprefixer@latest
npm install -D postcss-import postcss-preset-env postcss-nesting cssnano
npm install -D @types/node @types/react @types/react-dom typescript
npm install @tanstack/react-query axios react-router-dom

# Initialize Tailwind CSS if not already done
if [ ! -f tailwind.config.js ]; then
  npx tailwindcss init -p
fi

# Create necessary directories
mkdir -p .vscode
mkdir -p src/types

# Create CSS types file
cat > src/types/css.d.ts << EOL
declare module '*.css' {
  const styles: { [className: string]: string }
  export default styles
}

declare module 'tailwindcss/tailwind.css'
declare module 'tailwindcss/base'
declare module 'tailwindcss/components'
declare module 'tailwindcss/utilities'
EOL

# Install VS Code extensions if code command is available
if command -v code &> /dev/null; then
  code --install-extension bradlc.vscode-tailwindcss
  code --install-extension csstools.postcss
  code --install-extension dbaeumer.vscode-eslint
  code --install-extension EditorConfig.EditorConfig
fi

# Create EditorConfig file
cat > .editorconfig << EOL
root = true

[*]
end_of_line = lf
insert_final_newline = true
charset = utf-8
indent_style = space
indent_size = 2

[*.{js,jsx,ts,tsx,css}]
trim_trailing_whitespace = true
EOL

# Create PostCSS config type file
cat > src/types/postcss.d.ts << EOL
declare module 'postcss-preset-env'
declare module 'postcss-import'
declare module 'postcss-nesting'
declare module 'cssnano'
EOL

# Add PostCSS comment to index.css
if ! grep -q "postcss-preset-env" src/index.css; then
  sed -i.bak '1i/* postcss-preset-env stage 1 */\n/* @import "tailwindcss/base"; */\n/* @import "tailwindcss/components"; */\n/* @import "tailwindcss/utilities"; */' src/index.css
  rm src/index.css.bak
fi

echo "Setup complete! Please restart VS Code for the changes to take effect." 