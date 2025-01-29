#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up Frontend Python virtual environment...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env file...${NC}"
    cat > .env << EOL
# API Configuration
API_URL=http://localhost:8000
API_TOKEN=your_api_token_here

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
EOL
    echo -e "${GREEN}.env file created${NC}"
fi

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${BLUE}To activate the virtual environment, run:${NC}"
echo "source venv/bin/activate"
echo -e "${BLUE}To start the Streamlit app, run:${NC}"
echo "streamlit run app.py"

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