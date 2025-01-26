# Frontend Tokenomics

Interface utilisateur Streamlit pour simuler et visualiser différents scénarios tokenomics.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

L'application utilise deux variables d'environnement :

- `API_URL` : URL de l'API backend (par défaut: http://localhost:8000)
- `API_TOKEN` : Token JWT pour l'authentification

Vous pouvez les configurer de plusieurs façons :

1. Variables d'environnement :
```bash
export API_URL=http://localhost:8000
export API_TOKEN=votre_token_jwt
```

2. Fichier `.env` :
```
API_URL=http://localhost:8000
API_TOKEN=votre_token_jwt
```

## Lancement

```bash
streamlit run app.py
```

L'application sera accessible à l'adresse : http://localhost:8501

## Utilisation

1. Entrez les paramètres de simulation :
   - Supply initiale
   - Taux d'inflation (%)
   - Durée en années

2. Cliquez sur "Simuler"

3. Visualisez les résultats :
   - Métriques clés
   - Graphique interactif
   - Tableau de données
   - Export CSV 