# Backend Tokenomics

Backend de l'application Tokenomics, construit avec Flask, FastAPI, MongoDB et diverses bibliothèques d'analyse de données.

## Configuration de l'environnement de développement

### Prérequis
- Python 3.9+
- MongoDB
- Redis (optionnel, pour le cache)

### Installation

1. Cloner le repository et naviguer vers le dossier backend :
```bash
cd backend
```

2. Rendre le script setup.sh exécutable et le lancer :
```bash
chmod +x setup.sh
./setup.sh
```

Ou configurer manuellement :

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate  # Sur Unix/macOS
# ou
.\venv\Scripts\activate  # Sur Windows

# Installer les dépendances
pip install -r requirements.txt

# Copier le fichier d'environnement
cp .env.example .env
```

3. Configurer les variables d'environnement :
   - Ouvrir le fichier `.env`
   - Remplir les variables avec vos propres valeurs

### Démarrage du serveur

En mode développement :
```bash
python run.py
```

Avec gunicorn (production) :
```bash
gunicorn run:app
```

### Tests

Exécuter les tests :
```bash
pytest
```

### Linting et Formatage

Formatter le code :
```bash
black .
isort .
```

Vérifier le style :
```bash
flake8
```

## Déploiement sur Heroku

1. Installer le CLI Heroku et se connecter
2. Créer une nouvelle application :
```bash
heroku create votre-app-name
```

3. Configurer les variables d'environnement :
```bash
heroku config:set MONGODB_URI=votre_uri_mongodb
heroku config:set JWT_SECRET_KEY=votre_secret
# etc. pour toutes les variables d'environnement
```

4. Déployer :
```bash
git push heroku main
```

## Structure du Projet

```
backend/
├── app/
│   ├── models/        # Modèles de données
│   ├── routes/        # Routes API
│   ├── services/      # Logique métier
│   └── utils/         # Utilitaires
├── tests/             # Tests
├── .env.example       # Template des variables d'environnement
├── Procfile          # Configuration Heroku
├── requirements.txt  # Dépendances Python
└── run.py           # Point d'entrée de l'application
``` 