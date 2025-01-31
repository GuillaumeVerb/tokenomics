# Guide de contribution

Nous sommes ravis que vous souhaitiez contribuer au simulateur de tokenomics ! Ce document fournit les lignes directrices pour contribuer au projet.

## Comment contribuer

1. **Fork & Clone**
   - Faites un fork du repository
   - Clonez votre fork localement
   ```bash
   git clone https://github.com/votre-username/tokenomics.git
   ```

2. **Branches**
   - Créez une branche pour votre fonctionnalité
   ```bash
   git checkout -b feature/ma-fonctionnalite
   ```
   - Utilisez des noms descriptifs (ex: `feature/add-staking`, `fix/mongodb-connection`)

3. **Commits**
   - Faites des commits atomiques
   - Utilisez des messages clairs et descriptifs
   ```bash
   git commit -m "feat: ajoute la simulation de staking"
   git commit -m "fix: corrige la connexion MongoDB"
   ```

4. **Tests**
   - Ajoutez des tests pour les nouvelles fonctionnalités
   - Assurez-vous que tous les tests passent
   ```bash
   cd backend
   pytest
   cd ../frontend
   npm test
   ```

5. **Documentation**
   - Mettez à jour la documentation si nécessaire
   - Commentez votre code
   - Ajoutez des docstrings pour les fonctions Python

## Standards de code

### Backend (Python)
- Suivez PEP 8
- Utilisez des type hints
- Docstrings pour les fonctions et classes
- Tests avec pytest

### Frontend (TypeScript/React)
- Suivez les conventions ESLint
- Utilisez des composants fonctionnels
- Tests avec Jest et React Testing Library
- Styles avec Tailwind CSS

## Pull Requests

1. **Préparation**
   - Mettez à jour votre branche avec main
   ```bash
   git fetch origin
   git rebase origin/main
   ```
   - Vérifiez que les tests passent

2. **Soumission**
   - Créez la PR sur GitHub
   - Décrivez clairement les changements
   - Référencez les issues concernées
   - Ajoutez des captures d'écran si pertinent

3. **Review**
   - Répondez aux commentaires
   - Faites les modifications demandées
   - Maintenez la PR à jour avec main

## Rapport de bugs

Utilisez les issues GitHub avec :
- Description détaillée du problème
- Étapes pour reproduire
- Comportement attendu vs observé
- Environnement (OS, versions)
- Logs d'erreur si disponibles

## Nouvelles fonctionnalités

Pour proposer une nouvelle fonctionnalité :
1. Ouvrez une issue de discussion
2. Décrivez la fonctionnalité en détail
3. Expliquez pourquoi elle serait utile
4. Attendez le feedback avant de commencer

## Questions

Pour toute question :
- Consultez d'abord les issues existantes
- Utilisez les discussions GitHub
- Contactez l'équipe via Slack

## License

En contribuant, vous acceptez que votre code soit sous la même licence que le projet (voir LICENSE). 