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

# Backend Services

## Market Data Service

Le service de données de marché récupère les prix et autres métriques des cryptomonnaies depuis CoinGecko et les stocke dans MongoDB.

### Prérequis

1. Python 3.8+
2. MongoDB installé et en cours d'exécution
3. Dépendances Python :
```bash
pip install requests pymongo
```

### Configuration

1. MongoDB doit être accessible à l'URL par défaut : `mongodb://localhost:27017/`
2. La base de données `tokenomics` sera créée automatiquement
3. Les index nécessaires seront créés automatiquement lors de la première exécution

### Utilisation

#### Exécution manuelle

```bash
# Depuis le répertoire backend/
python scripts/fetch_market_data.py
```

#### Configuration du Cron Job

Pour exécuter le script toutes les 5 minutes :

1. Rendez le script exécutable :
```bash
chmod +x scripts/fetch_market_data.py
```

2. Ouvrez votre crontab :
```bash
crontab -e
```

3. Ajoutez la ligne suivante (ajustez les chemins selon votre installation) :
```
*/5 * * * * /chemin/vers/venv/bin/python /chemin/vers/backend/scripts/fetch_market_data.py
```

### Logs

Les logs sont écrits dans :
- Console (stdout)
- Fichier : `backend/logs/market_data.log`

### Structure des données

Les données sont stockées dans la collection `market_data` avec la structure suivante :

```javascript
{
  "token_id": "bitcoin",
  "symbol": "BTC",
  "name": "Bitcoin",
  "timestamp": ISODate("2024-01-01T12:00:00Z"),
  "price_usd": 42000.50,
  "market_cap": 820000000000,
  "total_volume": 25000000000,
  "circulating_supply": 19500000,
  "total_supply": 21000000,
  "max_supply": 21000000,
  "price_change_percentage": {
    "24h": 2.5,
    "7d": -1.2,
    "30d": 5.8
  }
}
```

### Gestion des erreurs

Le script gère automatiquement :
- Les timeouts (10 secondes par défaut)
- Les rate limits de l'API CoinGecko (pause de 60 secondes)
- Les tentatives de reconnexion (3 tentatives maximum)

Toutes les erreurs sont enregistrées dans les logs.

### Tokens suivis

Par défaut, les tokens suivants sont suivis :
- Bitcoin (BTC)
- Ethereum (ETH)
- Binance Coin (BNB)
- Cardano (ADA)
- Solana (SOL)
- Polkadot (DOT)
- Avalanche (AVAX)

Pour modifier la liste, ajustez la constante `TOKENS` dans `services/market_data.py`. 