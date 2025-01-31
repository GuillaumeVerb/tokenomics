# Guide Utilisateur - Simulateur de Tokenomics

## Table des matières
- [Installation et Configuration](#installation-et-configuration)
  - [Prérequis](#prérequis)
  - [Installation locale](#installation-locale)
  - [Configuration de l'environnement](#configuration-de-lenvironnement)
- [Déploiement](#déploiement)
  - [Docker](#docker)
  - [Heroku](#heroku)
  - [Vercel](#vercel)
- [Utilisation du simulateur](#utilisation-du-simulateur)
  - [Simulation simple](#simulation-simple)
  - [Scénario avancé](#scénario-avancé)
  - [Comparaison de scénarios](#comparaison-de-scénarios)
- [Fonctionnalités des graphiques](#fonctionnalités-des-graphiques)
- [Limites et avertissements](#limites-et-avertissements)
- [FAQ et dépannage](#faq-et-dépannage)

## Installation et Configuration

### Prérequis
- Python 3.11+
- Node.js 18+
- MongoDB 6.0+
- Git

### Installation locale

1. Cloner le repository :
```bash
git clone https://github.com/votre-username/tokenomics.git
cd tokenomics
```

2. Installation du backend :
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
pip install -r requirements.txt
```

3. Installation du frontend :
```bash
cd frontend
npm install
```

### Configuration de l'environnement

1. Backend (`.env`) :
```env
MONGODB_URI=mongodb://localhost:27017/tokenomics
JWT_SECRET=votre_secret_jwt
ENVIRONMENT=development
```

2. Frontend (`.env.local`) :
```env
VITE_API_URL=http://localhost:8000
```

3. Lancer en mode développement :

Backend :
```bash
cd backend
uvicorn app.main:app --reload
```

Frontend :
```bash
cd frontend
npm run dev
```

Le simulateur sera accessible sur `http://localhost:5173`

## Déploiement

### Docker

1. Construction de l'image :
```bash
docker build -t tokenomics-api ./backend
```

2. Lancement du conteneur :
```bash
docker run -p 8000:8000 \
  -e MONGODB_URI=votre_uri_mongodb \
  -e JWT_SECRET=votre_secret \
  -e ENVIRONMENT=production \
  tokenomics-api
```

### Heroku

1. Installation du CLI Heroku :
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

2. Déploiement :
```bash
heroku login
heroku create votre-app
heroku config:set MONGODB_URI=votre_uri_mongodb
heroku config:set JWT_SECRET=votre_secret
heroku config:set ENVIRONMENT=production
git push heroku main
```

### Vercel

1. Installation du CLI Vercel :
```bash
npm install -g vercel
```

2. Déploiement :
```bash
cd frontend
vercel
```

## Utilisation du simulateur

### Simulation simple

La page de simulation simple permet de :
- Définir les paramètres de base du token
- Visualiser l'évolution du prix et de la liquidité
- Ajuster les paramètres en temps réel

![Simulation Simple](docs/images/simulation-simple.png)

Paramètres disponibles :
- Supply initial
- Prix initial
- Liquidité initiale
- Taux d'inflation
- Période de vesting

### Scénario avancé

La page de scénario avancé offre :
- Configuration détaillée des vesting schedules
- Paramètres de staking
- Simulation d'événements de marché
- Métriques avancées

![Scénario Avancé](docs/images/scenario-avance.png)

### Comparaison de scénarios

Permet de :
- Comparer jusqu'à 3 scénarios différents
- Analyser les différences de performance
- Exporter les résultats

![Comparaison](docs/images/comparaison.png)

## Fonctionnalités des graphiques

Les graphiques Plotly offrent plusieurs fonctionnalités interactives :

1. Zoom :
   - Utiliser la molette de la souris
   - Double-clic pour réinitialiser
   - Box select pour zoomer sur une zone

2. Hover :
   - Affichage des valeurs précises
   - Informations contextuelles
   - Métriques calculées

3. Export :
   - Format PNG pour les images
   - Export PDF du rapport complet
   - Export Excel des données brutes

![Fonctionnalités Graphiques](docs/images/graphiques.png)

## Limites et avertissements

1. Paramètres critiques :
   - Inflation > 100% : ⚠️ Risque de dévaluation rapide
   - Liquidité < 10% : ⚠️ Forte volatilité possible
   - Vesting < 6 mois : ⚠️ Pression de vente potentielle

2. Performances :
   - Limite de 10 ans pour les simulations
   - Max 3 scénarios en comparaison
   - Rafraîchissement des graphiques : 1s

## FAQ et dépannage

### Erreurs courantes

1. "Failed to connect to MongoDB"
   - Vérifier que MongoDB est lancé
   - Vérifier l'URI de connexion
   - Vérifier les permissions

2. "API endpoint not found"
   - Vérifier que le backend est lancé
   - Vérifier VITE_API_URL dans .env.local
   - Vérifier les logs du backend

3. "Invalid parameters"
   - Supply initial doit être > 0
   - Prix initial doit être > 0
   - Liquidité doit être entre 0 et 100%

### Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation API
- Contacter le support technique

---

## Contribution

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les détails. 