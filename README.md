# CaliPredict — California Housing Analytics & AI Predictions

Application web de prediction du prix immobilier en Californie, basee sur le dataset **California Housing** (recensement americain, 1990). Le projet combine une analyse exploratoire approfondie avec un modele de regression lineaire enrichi par du clustering geographique.

**URL publique** : deploye sur [Streamlit Cloud](https://streamlit.io/cloud)

**Auteur** : Mathis Ruiz — NEXA -School of Technology M2

---

## Objectif du projet

Ce projet repond a la question de recherche suivante :

> **Quels facteurs influencent le plus le prix immobilier en Californie, et dans quelle mesure un modele de regression lineaire enrichi par du clustering geographique peut-il capturer ces relations ?**

Le dataset regroupe les informations de **20 640 districts** decrits par 8 variables socio-economiques et geographiques. L'objectif est double : comprendre les determinants du prix median des logements et construire un modele predictif fiable.

---

## Dataset

| Propriete | Valeur |
|-----------|--------|
| Source | `sklearn.datasets.fetch_california_housing` |
| Lignes | 20 640 districts |
| Colonnes | 8 features + 1 target |
| Periode | Recensement americain 1990 |
| Target | `MedHouseVal` — prix median (x$100k) |

**Variables** :

| Variable | Description |
|----------|-------------|
| `MedInc` | Revenu median des menages du district (x$10k) |
| `HouseAge` | Age median des logements (annees) |
| `AveRooms` | Nombre moyen de pieces par logement |
| `AveBedrms` | Nombre moyen de chambres par logement |
| `Population` | Population totale du district |
| `AveOccup` | Nombre moyen d'occupants par logement |
| `Latitude` | Latitude geographique du centre du district |
| `Longitude` | Longitude geographique du centre du district |
| `MedHouseVal` | Prix median des logements (x$100k) — **cible** |

**Limites connues** : les prix sont plafonnes a $500 000 (censure a droite), les donnees datent de 1990, et les variables representent des moyennes par district.

---

## Pipeline ML

Le pipeline de prediction suit 5 etapes :

1. **Nettoyage** — Retrait des outliers (methode IQR x3) sur `AveRooms`, `AveBedrms`, `AveOccup`, `Population`
2. **Feature engineering** — Creation de 2 nouvelles variables : `BedroomRatio` (ratio chambres/pieces) et `IncomeLocation` (revenu x latitude)
3. **Clustering geographique** — K-Means (K=1000) sur les coordonnees GPS, encode en one-hot (1 000 features supplementaires)
4. **Standardisation** — `StandardScaler` ajuste uniquement sur le jeu d'entrainement
5. **Prediction** — Regression lineaire multiple sur 1 010 features au total

---

## Performance du modele

| Metrique | Valeur | Interpretation |
|----------|--------|----------------|
| **R²** | 0.8241 | Le modele explique ~82% de la variance des prix |
| **MAE** | ~$32 800 | Erreur absolue moyenne en dollars |
| **RMSE** | 0.4900 | Racine de l'erreur quadratique moyenne |
| **Features** | 1 010 | 8 base + 2 engineered + 1 000 clusters |

---

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Dashboard | Streamlit + Plotly |
| API | FastAPI |
| ML | scikit-learn (LinearRegression, KMeans, StandardScaler) |
| Visualisations avancees | statsmodels (OLS trendline, LOWESS smoother) |
| Geocodage | geopy (Nominatim) |
| Deploiement | Streamlit Cloud |
| Python | 3.10 |

---

## Structure du projet

```
ds-project/
├── app/
│   ├── api/                    # API FastAPI
│   │   ├── routes/
│   │   │   └── predict.py      # Endpoints: /predict, /metrics, /health
│   │   └── schemas/
│   │       └── prediction.py   # Schemas Pydantic (HousingInput, PredictionOutput)
│   ├── core/
│   │   └── model_loader.py     # Chargement et cache des artefacts ML + pipeline de prediction
│   ├── dashboard/              # Dashboard Streamlit
│   │   ├── app.py              # Point d'entree unique (navigation par onglets)
│   │   ├── assets/
│   │   │   └── logo.jpg        # Logo CaliPredict
│   │   ├── components/
│   │   │   └── shared.py       # CSS, constantes, fonctions partagees
│   │   └── pages/
│   │       ├── exploration.py  # Onglet Exploration (6 viz, KPIs, filtres)
│   │       ├── analyse.py      # Onglet Analyse (modele, residus, LOWESS)
│   │       └── prediction.py   # Onglet Prediction (formulaire, geocodage, carte)
│   ├── ml/
│   │   ├── training/           # Scripts d'entrainement
│   │   └── serving/            # Serving du modele
│   └── main.py                 # Point d'entree FastAPI
├── configs/                    # Configuration dev/prod
├── data/
│   └── raw/
│       └── california_housing.csv
├── models/                     # Artefacts entraines (.pkl)
│   ├── linear_regression.pkl
│   ├── scaler.pkl
│   ├── kmeans.pkl
│   ├── feature_names.pkl
│   ├── feature_names_base.pkl
│   ├── metrics.pkl
│   └── test_predictions.csv
├── notebooks/
│   └── RUIZ_MATHIS_ProjetML.ipynb  # Notebook d'analyse exploratoire
├── scripts/
│   └── train_model.py          # Script d'entrainement reproductible
├── tests/                      # Tests unitaires
├── .streamlit/
│   └── config.toml             # Theme CaliPredict (navy + orange)
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── requirements-dev.txt
├── runtime.txt                 # Python 3.10 pour Streamlit Cloud
└── README.md
```

---

## Installation et lancement

### Prerequis

- Python 3.10+
- pip

### Installation

```bash
# Cloner le repo
git clone <url-du-repo>
cd ds-project

# Installer les dependances
make install

# (Optionnel) Installer les dependances de developpement
make install-dev
```

### Entrainement du modele

```bash
make train
```

Le script `scripts/train_model.py` reproduit le pipeline complet du notebook et sauvegarde les artefacts dans `models/`.

### Lancer le dashboard (Streamlit)

```bash
make dashboard
```

Le dashboard est accessible sur `http://localhost:8501`.

### Lancer l'API (FastAPI)

```bash
make api
```

L'API est accessible sur `http://localhost:8000`. Documentation interactive disponible sur `/docs`.

---

## API REST

### `POST /predict`

Predit le prix median d'un district.

**Requete** :
```json
{
  "MedInc": 3.87,
  "HouseAge": 29,
  "AveRooms": 5.43,
  "AveBedrms": 1.10,
  "Population": 1425,
  "AveOccup": 3.07,
  "Latitude": 37.78,
  "Longitude": -122.42
}
```

**Reponse** :
```json
{
  "predicted_price": 2.8432,
  "predicted_price_dollars": "$284,320",
  "features_used": { ... }
}
```

### `GET /metrics`

Retourne les metriques du modele (R², MAE, RMSE).

### `GET /health`

Verifie que le modele est charge et fonctionnel.

---

## Dashboard

Le dashboard est organise en **4 onglets** (navigation horizontale, sans sidebar) :

### Accueil
Presentation du projet, metriques cles du dataset (20 640 lignes, 9 colonnes, 0% valeurs manquantes), apercu des donnees et description des colonnes.

### Exploration des donnees
- **6 visualisations** : distribution des prix (avec annotation de censure a $500k), carte geographique interactive, scatter revenu vs prix (avec trendline OLS), heatmap de correlations (palette colorblind-friendly), box plot par tranche d'age, distribution au choix
- **6 KPIs** : districts, prix moyen, prix median, revenu moyen, age moyen, population totale
- **3 filtres interactifs** : tranche de prix, revenu median, age des logements
- **Export CSV** des donnees filtrees

### Analyse approfondie
- Question de recherche et metriques du modele (R², MAE, RMSE)
- Valeurs reelles vs predites + distribution des residus
- Importance des variables (coefficients)
- Analyse des residus avec smoother LOWESS
- Pipeline de prediction detaille (5 etapes)
- Insights et conclusions (resultats, surprises, limites, recommandations)

### Prediction interactive
- Formulaire de saisie (6 parametres : revenu, population, occupants, age, pieces, chambres)
- Geocodage d'adresse (geopy/Nominatim)
- Carte interactive des districts proches
- Estimation du prix avec marge d'erreur (MAE)
- Position de l'estimation dans la distribution globale

---

## Deploiement sur Streamlit Cloud

Le projet est configure pour un deploiement direct sur Streamlit Cloud :

- `runtime.txt` — specifie Python 3.10
- `requirements.txt` — dependances de production
- `.streamlit/config.toml` — theme personnalise CaliPredict (navy #1E3A5F + orange #D4872E)
- `.gitignore` — exclut `.streamlit/secrets.toml` pour la securite

---

## Commandes disponibles (Makefile)

| Commande | Description |
|----------|-------------|
| `make install` | Installer les dependances |
| `make install-dev` | Installer les dependances de developpement |
| `make train` | Entrainer le modele |
| `make dashboard` | Lancer le dashboard Streamlit (port 8501) |
| `make api` | Lancer l'API FastAPI (port 8000) |
| `make test` | Lancer les tests (pytest) |
| `make lint` | Verifier le code (ruff + black) |
| `make format` | Formater le code |
| `make clean` | Nettoyer les fichiers temporaires |

---

## Auteur

**Mathis Ruiz** — NEXA M2
