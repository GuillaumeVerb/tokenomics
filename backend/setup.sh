#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up Python virtual environment...${NC}"

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

# Install development dependencies if they exist
if [ -f "requirements-dev.txt" ]; then
    echo -e "${BLUE}Installing development dependencies...${NC}"
    pip install -r requirements-dev.txt
fi

# Install Airflow dependencies if they exist
if [ -f "requirements-airflow.txt" ]; then
    echo -e "${BLUE}Installing Airflow dependencies...${NC}"
    pip install -r requirements-airflow.txt
fi

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${BLUE}To activate the virtual environment, run:${NC}"
echo "source venv/bin/activate"

# Création du fichier .env à partir du template
cp .env.example .env

echo "Configuration terminée ! Pour activer l'environnement virtuel :"
echo "source venv/bin/activate"
echo "Pour lancer le serveur en mode développement :"
echo "python run.py" 