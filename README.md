
# Portfolio Sustainable

Portfolio Sustainable est un projet académique réalisé dans le cadre du Master MBFA Finance & Data Science. Il illustre la construction d'un portefeuille multi-objectifs intégrant des contraintes de performance financière, de risque et d'empreinte carbone. Le dépôt contient l'ensemble de la chaîne de valeur : collecte de données, calculs des métriques clés, optimisation sous contraintes et visualisation interactive via une application Streamlit.

## Objectifs du projet

- **Rendement** : maximiser le rendement annualisé attendu.
- **Risque** : contrôler la volatilité et le Conditional Value at Risk (CVaR) du portefeuille.
- **Durabilité** : réduire l'intensité carbone pondérée en respectant des seuils définis par l'utilisateur et des limites sectorielles optionnelles.

## Structure du dépôt

```
portfolio-sustainable/
├── app/                   # Application Streamlit
├── data/                  # Données brutes et transformées
├── notebooks/             # Notebooks pédagogiques
├── reports/               # Analyses et figures exportées
├── src/                   # Fonctions métiers (métriques & optimisation)
├── requirements.txt       # Dépendances Python
├── README.md              # Présentation du projet
└── .gitignore
```

## Fonctionnalités clés

- Calculs des principales métriques de performance et de risque : rendement, volatilité, CVaR, drawdown maximal.
- Optimisation convexe avec contraintes de somme des poids, bornes individuelles, intensité carbone, CVaR, turnover et limites sectorielles.
- Notebooks pédagogiques pour télécharger des données via `yfinance`, construire un portefeuille de référence et analyser les scénarios d'optimisation.
- Application Streamlit proposant trois curseurs interactifs (carbone, CVaR, turnover) et affichant les poids optimisés ainsi que les métriques résultantes.

## Installation locale (Python 3.11)

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/<votre-compte>/portfolio-sustainable.git
   cd portfolio-sustainable
   ```

2. **Créer un environnement virtuel**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate  # sous Windows : .venv\\Scripts\\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation dans GitHub Codespaces

- Ouvrir le dépôt dans un Codespace avec une image Python 3.11.
- Exécuter `pip install -r requirements.txt` dans le terminal intégré.
- Lancer les notebooks ou l'application Streamlit comme décrit ci-dessous (les ports sont automatiquement exposés).

## Lancer les notebooks Jupyter

1. Installer Jupyter (inclus dans `requirements.txt`).
2. Depuis la racine du projet :
   ```bash
   jupyter notebook
   ```
3. Ouvrir successivement :
   - `notebooks/01_data_download.ipynb`
   - `notebooks/02_baseline.ipynb`
   - `notebooks/03_optimization.ipynb`

## Lancer l'application Streamlit

Après avoir exécuté le notebook de téléchargement ou placé des fichiers `returns.csv` et `carbon_intensity.csv` dans `data/processed/` :

```bash
streamlit run app/streamlit_app.py
```

L'application propose trois curseurs pour fixer les contraintes puis affiche le portefeuille optimisé ainsi qu'un tableau récapitulatif des métriques.

## Prochaines pistes d'amélioration

- Ajouter des scénarios de stress-tests climatiques (alignement sur 1,5°C ou Net Zero).
- Intégrer des données de controverses ESG et des scores de gouvernance.
- Déployer l'application sur Streamlit Community Cloud pour un accès facilité.

---

Pour toute question ou opportunité professionnelle, n'hésitez pas à me contacter : ce projet illustre ma capacité à relier la finance durable, la modélisation de données et le développement d'outils interactifs.
