"""Chargement et mise en cache des artefacts ML."""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from functools import lru_cache


MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"


@lru_cache(maxsize=1)
def load_artifacts():
    """Charge le modèle, scaler et kmeans une seule fois."""
    model = joblib.load(MODELS_DIR / "linear_regression.pkl")
    scaler = joblib.load(MODELS_DIR / "scaler.pkl")
    kmeans = joblib.load(MODELS_DIR / "kmeans.pkl")
    feature_names = joblib.load(MODELS_DIR / "feature_names.pkl")
    feature_names_base = joblib.load(MODELS_DIR / "feature_names_base.pkl")
    metrics = joblib.load(MODELS_DIR / "metrics.pkl")
    return {
        "model": model,
        "scaler": scaler,
        "kmeans": kmeans,
        "feature_names": feature_names,
        "feature_names_base": feature_names_base,
        "metrics": metrics,
    }


def predict(input_data: dict) -> float:
    """
    Pipeline de prédiction complet :
    1. Feature engineering (BedroomRatio, IncomeLocation)
    2. Clustering géographique
    3. Scaling
    4. Prédiction
    """
    artifacts = load_artifacts()
    model = artifacts["model"]
    scaler = artifacts["scaler"]
    kmeans = artifacts["kmeans"]
    feature_names = artifacts["feature_names"]

    # Feature engineering
    input_data["BedroomRatio"] = input_data["AveBedrms"] / max(input_data["AveRooms"], 0.01)
    input_data["IncomeLocation"] = input_data["MedInc"] * input_data["Latitude"]

    # Clustering
    geo = np.array([[input_data["Longitude"], input_data["Latitude"]]])
    cluster_id = kmeans.predict(geo)[0]

    # Construire le vecteur de features complet
    n_clusters = kmeans.n_clusters
    cluster_features = np.zeros(n_clusters)
    cluster_features[cluster_id] = 1.0

    base_features = [
        input_data["MedInc"], input_data["HouseAge"],
        input_data["AveRooms"], input_data["AveBedrms"],
        input_data["Population"], input_data["AveOccup"],
        input_data["Latitude"], input_data["Longitude"],
        input_data["BedroomRatio"], input_data["IncomeLocation"],
    ]

    X = np.array([base_features + list(cluster_features)])

    # Scaling + prédiction
    X_scaled = scaler.transform(X)
    prediction = model.predict(X_scaled)[0]

    return max(prediction, 0.0)  # pas de prix négatif
