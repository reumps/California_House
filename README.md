# California Housing Price Predictor

Web app de prédiction du prix immobilier en Californie, basée sur le dataset California Housing (1990).

## Stack

- **API** : FastAPI
- **Dashboard** : Streamlit + Plotly
- **ML** : scikit-learn (Régression Linéaire + K-Means clustering)

## Quick Start

```bash
# Installer les dépendances
make install

# Entraîner le modèle
make train

# Lancer l'API (port 8000)
make api

# Lancer le dashboard (port 8501) — dans un autre terminal
make dashboard
```

## Performance du modèle

| Métrique | Valeur |
|----------|--------|
| R² | 0.82 |
| MAE | ~$32,800 |
| RMSE | 0.49 |

## Structure

```
app/
├── api/          # FastAPI backend
├── core/         # Chargement modèle
├── dashboard/    # Streamlit frontend
└── ml/           # Training & serving
```

## Auteur

Mathis Ruiz
