# Tests de l'API Tokenomics

## Installation des dépendances

```bash
pip install -r requirements-dev.txt
```

## Structure des tests

```
tests/
├── __init__.py
├── conftest.py                    # Fixtures partagées
├── test_simulation_endpoints.py   # Tests des endpoints /simulate/*
└── test_middleware.py            # Tests des middlewares
```

## Exécution des tests

### Lancer tous les tests
```bash
pytest
```

### Lancer avec couverture de code
```bash
pytest --cov=app --cov-report=term-missing
```

### Lancer un fichier de test spécifique
```bash
pytest tests/test_simulation_endpoints.py
```

### Lancer un test spécifique
```bash
pytest tests/test_simulation_endpoints.py::test_constant_inflation_simulation
```

### Mode verbeux
```bash
pytest -v
```

### Avec logs détaillés
```bash
pytest --log-cli-level=INFO
```

## Couverture de code

La couverture minimale requise est de 80%. Pour générer un rapport de couverture HTML :

```bash
pytest --cov=app --cov-report=html
```

Le rapport sera généré dans le dossier `htmlcov/`.

## Tests d'intégration

Les tests d'intégration nécessitent une base de données de test et des variables d'environnement spécifiques.
Créez un fichier `.env.test` avec les configurations appropriées.

```bash
# .env.test
ENVIRONMENT=test
JWT_SECRET=test_secret
DATABASE_URL=postgresql://user:pass@localhost:5432/tokenomics_test
```

Puis lancez les tests avec :

```bash
ENV_FILE=.env.test pytest
```

## Mocking

Les appels externes (APIs, blockchain) sont mockés dans les tests. Les mocks sont définis dans `conftest.py`.

## CI/CD

Les tests sont automatiquement exécutés dans le pipeline CI/CD :
- À chaque push sur main
- À chaque pull request
- Avant chaque déploiement

## Bonnes pratiques

1. Chaque endpoint doit avoir :
   - Tests de fonctionnalité basique
   - Tests de validation des inputs
   - Tests d'authentification
   - Tests des cas d'erreur

2. Utiliser des fixtures pour :
   - Données de test
   - Configuration
   - Tokens d'authentification
   - Mocks

3. Nommer les tests clairement :
   - test_[fonctionnalité]_[scénario]
   - Exemple : test_constant_inflation_validation

4. Documenter les tests complexes :
   - Préconditions
   - Étapes
   - Résultats attendus

5. Maintenir l'isolation des tests :
   - Nettoyer les données après chaque test
   - Éviter les dépendances entre tests
   - Utiliser des bases de données temporaires 