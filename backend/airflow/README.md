# Pipeline de Données Tokenomics avec Airflow

Ce pipeline Airflow automatise la collecte de données de marché et la mise à jour des simulations tokenomics.

## Architecture

Le pipeline se compose de 5 tâches principales :
1. `fetch_market_data` : Récupère les données de CoinGecko
2. `clean_market_data` : Nettoie et valide les données
3. `check_simulation` : Vérifie si une nouvelle simulation est nécessaire
4. `run_simulation` : Exécute la simulation si nécessaire
5. `notify_success` : Envoie une notification de succès

## Prérequis

1. Python 3.8+
2. Apache Airflow 2.7+
3. MongoDB
4. Accès à l'API CoinGecko
5. Compte Slack (pour les notifications)
6. Serveur SMTP (pour les alertes par email)

## Installation

1. Installer Airflow et ses dépendances :
```bash
pip install apache-airflow
pip install apache-airflow-providers-mongo
pip install apache-airflow-providers-slack
pip install apache-airflow-providers-http
```

2. Initialiser la base de données Airflow :
```bash
airflow db init
```

3. Créer un utilisateur admin :
```bash
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password your_password
```

## Configuration

1. Configurer les connexions Airflow :

   a. MongoDB :
   ```bash
   airflow connections add 'mongo_default' \
       --conn-type 'mongo' \
       --conn-host 'localhost' \
       --conn-port '27017' \
       --conn-schema 'tokenomics'
   ```

   b. Slack :
   ```bash
   airflow connections add 'slack_webhook' \
       --conn-type 'http' \
       --conn-host 'hooks.slack.com' \
       --conn-password 'your_webhook_token'
   ```

   c. API Tokenomics :
   ```bash
   airflow connections add 'tokenomics_api' \
       --conn-type 'http' \
       --conn-host 'localhost' \
       --conn-port '8000'
   ```

2. Configurer les variables Airflow :
```bash
airflow variables set 'email_recipients' '["alert@example.com"]'
airflow variables set 'slack_channel' '#tokenomics-alerts'
```

## Fonctionnement du Scheduler

Le DAG est configuré pour s'exécuter toutes les heures (`schedule_interval='@hourly'`). Voici comment il fonctionne :

1. **Déclenchement** : Le scheduler vérifie toutes les minutes les DAGs à exécuter.

2. **Exécution** : Pour chaque intervalle :
   - Récupère les données de marché
   - Nettoie les données
   - Vérifie si les prix ont changé significativement (>5%)
   - Lance une nouvelle simulation si nécessaire
   - Envoie des notifications

3. **Gestion des erreurs** :
   - Retry automatique (3 tentatives) en cas d'échec
   - Notification par email en cas d'échec définitif
   - Les tâches suivantes sont annulées si une tâche échoue

4. **Monitoring** :
   - Interface web Airflow : http://localhost:8080
   - Logs détaillés dans `/logs/airflow/`
   - Notifications Slack pour chaque exécution réussie
   - Alertes email en cas d'échec

## Démarrage

1. Démarrer le webserver Airflow :
```bash
airflow webserver --port 8080
```

2. Dans un autre terminal, démarrer le scheduler :
```bash
airflow scheduler
```

3. Accéder à l'interface web : http://localhost:8080

## Maintenance

1. **Logs** : Rotation automatique des logs tous les 30 jours
2. **Base de données** : Nettoyage automatique des anciennes exécutions
3. **Monitoring** : Métriques disponibles dans l'interface web

## Dépannage

1. Vérifier les logs :
```bash
airflow tasks test market_data_pipeline fetch_market_data 2024-01-01
```

2. Réinitialiser une tâche échouée :
```bash
airflow tasks clear market_data_pipeline -t fetch_market_data -s 2024-01-01
```

3. Vérifier les connexions :
```bash
airflow connections get mongo_default
``` 