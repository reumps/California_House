"""
Script d'entraînement du modèle California Housing.
Reproduit le pipeline du notebook RUIZ_MATHIS_ProjetML.
Sauvegarde : modèle, scaler, kmeans dans models/
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# --- Chemins ---
ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "raw" / "california_housing.csv"
MODELS_DIR = ROOT / "models"
MODELS_DIR.mkdir(exist_ok=True)

# --- Chargement ---
print("Chargement des données...")
df = pd.read_csv(DATA_PATH)
print(f"  {df.shape[0]:,} lignes, {df.shape[1]} colonnes")

# --- Nettoyage outliers (IQR 3×) ---
df_clean = df.copy()
cols_outliers = ['AveRooms', 'AveBedrms', 'AveOccup', 'Population']
for col in cols_outliers:
    Q1 = df_clean[col].quantile(0.25)
    Q3 = df_clean[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 3 * IQR
    upper = Q3 + 3 * IQR
    before = len(df_clean)
    df_clean = df_clean[(df_clean[col] >= lower) & (df_clean[col] <= upper)]
    print(f"  {col:15s} : {before - len(df_clean):4d} outliers retirés")

print(f"  Dataset nettoyé : {len(df_clean):,} lignes")

# --- Feature engineering ---
df_clean = df_clean.copy()
df_clean['BedroomRatio'] = df_clean['AveBedrms'] / df_clean['AveRooms']
df_clean['IncomeLocation'] = df_clean['MedInc'] * df_clean['Latitude']

# --- Clustering géographique ---
N_CLUSTERS = 1000
print(f"\nClustering géographique (K={N_CLUSTERS})...")
kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
df_clean['GeoCluster'] = kmeans.fit_predict(df_clean[['Longitude', 'Latitude']])

cluster_dummies = pd.get_dummies(df_clean['GeoCluster'], prefix='Cluster', dtype=float)
df_clean = pd.concat([df_clean, cluster_dummies], axis=1)

# --- Préparation features ---
FEATURES_BASE = ['MedInc', 'HouseAge', 'AveRooms', 'AveBedrms',
                 'Population', 'AveOccup', 'Latitude', 'Longitude',
                 'BedroomRatio', 'IncomeLocation']
FEATURES_CLUSTER = [c for c in df_clean.columns if c.startswith('Cluster_')]
FEATURES_ALL = FEATURES_BASE + FEATURES_CLUSTER
TARGET = 'MedHouseVal'

X = df_clean[FEATURES_ALL].values
y = df_clean[TARGET].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE
)

# --- Scaling ---
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)

# --- Entraînement ---
print("\nEntraînement du modèle...")
model = LinearRegression()
model.fit(X_train_sc, y_train)

# --- Évaluation ---
y_pred = model.predict(X_test_sc)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"\n{'='*50}")
print(f"  Résultats sur le jeu de test")
print(f"{'='*50}")
print(f"  MAE  : {mae:.4f}  (~{mae*100_000:,.0f} $)")
print(f"  RMSE : {rmse:.4f}")
print(f"  R²   : {r2:.4f}")

# --- Sauvegarde ---
print("\nSauvegarde des artefacts...")
joblib.dump(model, MODELS_DIR / "linear_regression.pkl")
joblib.dump(scaler, MODELS_DIR / "scaler.pkl")
joblib.dump(kmeans, MODELS_DIR / "kmeans.pkl")
joblib.dump(FEATURES_ALL, MODELS_DIR / "feature_names.pkl")
joblib.dump(FEATURES_BASE, MODELS_DIR / "feature_names_base.pkl")

# Sauvegarder les métriques
metrics = {'mae': mae, 'rmse': rmse, 'r2': r2}
joblib.dump(metrics, MODELS_DIR / "metrics.pkl")

# Sauvegarder actual vs predicted pour le dashboard
test_results = pd.DataFrame({
    'actual': y_test,
    'predicted': y_pred,
    'residual': y_test - y_pred,
})
test_results.to_csv(MODELS_DIR / "test_predictions.csv", index=False)
print(f"  ✓ test_predictions.csv ({len(test_results):,} lignes)")

print(f"\nFichiers sauvegardés dans {MODELS_DIR}/")
for f in MODELS_DIR.glob("*.pkl"):
    print(f"  ✓ {f.name}")

print("\nDone!")
