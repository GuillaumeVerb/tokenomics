#!/bin/bash

# Création de l'environnement virtuel
python3 -m venv venv

# Activation de l'environnement virtuel
source venv/bin/activate

# Installation des dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Création du fichier .env à partir du template
cp .env.example .env

echo "Configuration terminée ! Pour activer l'environnement virtuel :"
echo "source venv/bin/activate"
echo "Pour lancer le serveur en mode développement :"
echo "python run.py" 